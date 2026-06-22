"""
Cloud Agility Broker — FastAPI Backend
"""

from __future__ import annotations
import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session

import database
import models
import audit
from engines import compliance_engine, cost_engine, provisioning_engine
from report import build_json_report, build_pdf_report

# ── Init ──────────────────────────────────────────────────────────────────────
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Cloud Agility Broker",
    description="Automated cloud migration decision engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


# ── Companies ─────────────────────────────────────────────────────────────────
@app.get("/companies")
def list_companies(db: Session = Depends(database.get_db)):
    return db.query(models.Company).all()


@app.post("/companies")
def create_company(data: models.CompanyCreate, db: Session = Depends(database.get_db)):
    company = models.Company(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@app.get("/companies/{company_id}")
def get_company(company_id: str, db: Session = Depends(database.get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")
    return company


# ── Data Assets ───────────────────────────────────────────────────────────────
@app.get("/assets")
def list_assets(
    company_id: str | None = Query(None),
    db: Session = Depends(database.get_db),
):
    q = db.query(models.DataAsset)
    if company_id:
        q = q.filter(models.DataAsset.company_id == company_id)
    return q.all()


@app.post("/assets")
def create_asset(data: models.DataAssetCreate, db: Session = Depends(database.get_db)):
    asset = models.DataAsset(**data.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@app.get("/assets/{asset_id}")
def get_asset(asset_id: str, db: Session = Depends(database.get_db)):
    asset = db.query(models.DataAsset).filter(models.DataAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    return asset


# ── Cloud Accounts ────────────────────────────────────────────────────────────
@app.get("/cloud-accounts")
def list_accounts(
    company_id: str | None = Query(None),
    db: Session = Depends(database.get_db),
):
    q = db.query(models.CloudAccount)
    if company_id:
        q = q.filter(models.CloudAccount.company_id == company_id)
    return q.all()


@app.post("/cloud-accounts")
def create_account(data: models.CloudAccountCreate, db: Session = Depends(database.get_db)):
    account = models.CloudAccount(**data.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


# ── Policy Packs ──────────────────────────────────────────────────────────────
@app.get("/policy-packs")
def list_policy_packs():
    """Return metadata for all built-in policy packs."""
    return [
        {
            "id": k,
            "name": v["version"],
            "jurisdiction": v["jurisdiction"],
            "rule_count": len(v["rules"]),
            "rules": v["rules"],
        }
        for k, v in compliance_engine.POLICY_PACKS.items()
    ]


# ── Core Broker Endpoint ──────────────────────────────────────────────────────
@app.post("/broker/evaluate")
def evaluate(
    request: models.BrokerRequest,
    db: Session = Depends(database.get_db),
):
    """
    Full broker evaluation:
      1. Load company + asset
      2. Run compliance check
      3. Compute migration economics
      4. Create decision record
      5. Write audit log
    """
    # ── Load entities ────────────────────────────────────────────────────────
    company = db.query(models.Company).filter(models.Company.id == request.company_id).first()
    if not company:
        raise HTTPException(404, f"Company {request.company_id} not found")

    asset = db.query(models.DataAsset).filter(models.DataAsset.id == request.data_asset_id).first()
    if not asset:
        raise HTTPException(404, f"Data asset {request.data_asset_id} not found")

    # Find cloud account for the source cloud (to get spend and exit penalty)
    cloud_account = (
        db.query(models.CloudAccount)
        .filter(
            models.CloudAccount.company_id == company.id,
            models.CloudAccount.provider == asset.current_cloud,
        )
        .first()
    )

    current_monthly = cloud_account.monthly_spend_usd if cloud_account else 50000.0
    exit_penalty = cloud_account.early_exit_penalty_usd if cloud_account else 0.0

    audit.log_event(
        db, audit.EVENT_TYPES["BROKER_REQUEST_RECEIVED"],
        payload=request.model_dump(),
        actor="api",
    )

    # ── Compliance ────────────────────────────────────────────────────────────
    comp_result = compliance_engine.run_compliance_check(
        data_class=asset.data_class,
        residency_constraints=asset.residency_constraints or [],
        hq_country=company.headquarters_country,
        operating_regions=company.operating_regions or [],
        target_cloud=asset.target_cloud,
        source_cloud=asset.current_cloud,
    )

    # ── Cost ─────────────────────────────────────────────────────────────────
    cost_result = cost_engine.compute_migration_economics(
        current_monthly_cost=current_monthly,
        volume_gb=asset.volume_gb,
        source_cloud=asset.current_cloud,
        target_cloud=asset.target_cloud,
        early_exit_penalty=exit_penalty,
        engineering_hours=request.engineering_hours_estimate,
        engineering_hourly_rate=request.engineering_hourly_rate,
        downtime_hours=request.downtime_hours_estimate,
        revenue_per_hour=request.revenue_per_hour,
        time_horizon_months=request.time_horizon_months,
        min_savings_threshold_pct=request.min_savings_threshold_pct,
        data_class=asset.data_class,
    )

    audit.log_event(
        db, audit.EVENT_TYPES["COMPLIANCE_CHECK_COMPLETED"],
        payload=comp_result,
        actor="compliance_engine",
    )
    audit.log_event(
        db, audit.EVENT_TYPES["COST_ANALYSIS_COMPLETED"],
        payload={k: v for k, v in cost_result.items() if k != "sensitivity"},
        actor="cost_engine",
    )

    # ── Decision Logic ───────────────────────────────────────────────────────
    if comp_result["status"] == "fail":
        recommendation = "stay"
        rationale = (
            f"Migration blocked: compliance check failed for rule(s) "
            f"{comp_result['blocking_rules']}. "
            f"Data cannot legally move from {asset.current_cloud.upper()} to "
            f"{asset.target_cloud.upper()} under current policy packs "
            f"({', '.join(comp_result['evidence']['active_policy_packs'])})."
        )
    elif cost_result["recommendation"] == "move":
        recommendation = "move"
        rationale = (
            f"Migration recommended. Compliance: {comp_result['status'].upper()} "
            f"({len(comp_result['passing_rules'])} rules passed, "
            f"{len(comp_result['warnings'])} warnings). "
            f"Cost: {cost_result['savings_pct']}% monthly savings "
            f"(${cost_result['monthly_savings']:,.0f}/mo). "
            f"Migration cost ${cost_result['total_migration_cost']:,.0f}, "
            f"breakeven in {cost_result['breakeven_months']} months, "
            f"3-year net benefit ${cost_result['three_year_net']:,.0f}."
        )
    elif cost_result["recommendation"] == "investigate":
        recommendation = "investigate"
        rationale = (
            f"Marginal case. Compliance passes but cost savings of "
            f"{cost_result['savings_pct']}% are below the "
            f"{request.min_savings_threshold_pct}% threshold or "
            f"breakeven exceeds the {request.time_horizon_months}-month horizon. "
            f"Further analysis or renegotiation of exit fees recommended."
        )
    else:
        recommendation = "stay"
        rationale = (
            f"Migration not recommended. "
            f"{'Compliance failed. ' if comp_result['status'] == 'fail' else ''}"
            f"Cost analysis shows no net benefit: "
            f"${cost_result['monthly_savings']:,.0f}/mo savings insufficient to recover "
            f"${cost_result['total_migration_cost']:,.0f} migration cost."
        )

    # ── Persist Decision ─────────────────────────────────────────────────────
    decision_id = str(uuid.uuid4())
    decision = models.Decision(
        id=decision_id,
        company_id=company.id,
        data_asset_id=asset.id,
        source_cloud=asset.current_cloud,
        target_cloud=asset.target_cloud,
        compliance_status=comp_result["status"],
        compliance_summary=comp_result,
        cost_status=cost_result["status"],
        recommendation=recommendation,
        rationale=rationale,
        status="pending" if recommendation == "move" else "reviewed",
    )
    db.add(decision)

    cost_row = models.CostModel(
        id=str(uuid.uuid4()),
        decision_id=decision_id,
        current_monthly_cost=cost_result["current_monthly_cost"],
        target_monthly_cost=cost_result["target_monthly_cost"],
        egress_cost=cost_result["egress_cost"],
        exit_penalty=cost_result["exit_penalty"],
        engineering_effort_cost=cost_result["engineering_effort_cost"],
        downtime_risk_cost=cost_result["downtime_risk_cost"],
        total_migration_cost=cost_result["total_migration_cost"],
        monthly_savings=cost_result["monthly_savings"],
        breakeven_months=cost_result["breakeven_months"],
        three_year_net=cost_result["three_year_net"],
        assumptions={
            **cost_result["assumptions"],
            "compliance_overhead": cost_result.get("compliance_overhead", 0),
            "sensitivity": cost_result.get("sensitivity", []),
        },
    )
    db.add(cost_row)
    db.commit()
    db.refresh(decision)

    audit.log_event(
        db, audit.EVENT_TYPES["DECISION_CREATED"],
        payload={"decision_id": decision_id, "recommendation": recommendation},
        decision_id=decision_id,
        actor="broker",
    )

    return {
        "decision_id": decision_id,
        "recommendation": recommendation,
        "compliance": comp_result,
        "cost": cost_result,
        "rationale": rationale,
        "status": decision.status,
    }


# ── Decisions ─────────────────────────────────────────────────────────────────
@app.get("/decisions")
def list_decisions(
    company_id: str | None = Query(None),
    db: Session = Depends(database.get_db),
):
    q = db.query(models.Decision)
    if company_id:
        q = q.filter(models.Decision.company_id == company_id)
    decisions = q.order_by(models.Decision.created_at.desc()).all()
    result = []
    for d in decisions:
        row = {
            "id": d.id,
            "company_id": d.company_id,
            "data_asset_id": d.data_asset_id,
            "source_cloud": d.source_cloud,
            "target_cloud": d.target_cloud,
            "compliance_status": d.compliance_status,
            "cost_status": d.cost_status,
            "recommendation": d.recommendation,
            "rationale": d.rationale,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "cost_model": None,
        }
        if d.cost_model:
            cm = d.cost_model
            row["cost_model"] = {
                "monthly_savings": cm.monthly_savings,
                "total_migration_cost": cm.total_migration_cost,
                "three_year_net": cm.three_year_net,
                "breakeven_months": cm.breakeven_months,
            }
        result.append(row)
    return result


@app.get("/decisions/{decision_id}")
def get_decision(decision_id: str, db: Session = Depends(database.get_db)):
    d = db.query(models.Decision).filter(models.Decision.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")

    result = {
        "id": d.id,
        "company_id": d.company_id,
        "data_asset_id": d.data_asset_id,
        "source_cloud": d.source_cloud,
        "target_cloud": d.target_cloud,
        "compliance_status": d.compliance_status,
        "compliance_summary": d.compliance_summary,
        "cost_status": d.cost_status,
        "recommendation": d.recommendation,
        "rationale": d.rationale,
        "status": d.status,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }

    if d.cost_model:
        cm = d.cost_model
        result["cost_model"] = {
            "current_monthly_cost": cm.current_monthly_cost,
            "target_monthly_cost": cm.target_monthly_cost,
            "egress_cost": cm.egress_cost,
            "exit_penalty": cm.exit_penalty,
            "engineering_effort_cost": cm.engineering_effort_cost,
            "downtime_risk_cost": cm.downtime_risk_cost,
            "total_migration_cost": cm.total_migration_cost,
            "monthly_savings": cm.monthly_savings,
            "breakeven_months": cm.breakeven_months,
            "three_year_net": cm.three_year_net,
            "assumptions": cm.assumptions,
        }

    return result


# ── Approve / Reject Decision ─────────────────────────────────────────────────
@app.post("/decisions/{decision_id}/approve")
def approve_decision(decision_id: str, db: Session = Depends(database.get_db)):
    d = db.query(models.Decision).filter(models.Decision.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    if d.compliance_status == "fail":
        raise HTTPException(400, "Cannot approve: compliance check failed")
    d.status = "approved"
    d.updated_at = datetime.utcnow()
    db.commit()
    audit.log_event(
        db, audit.EVENT_TYPES["DECISION_APPROVED"],
        payload={"decision_id": decision_id},
        decision_id=decision_id,
        actor="human",
    )
    return {"status": "approved", "decision_id": decision_id}


@app.post("/decisions/{decision_id}/reject")
def reject_decision(decision_id: str, db: Session = Depends(database.get_db)):
    d = db.query(models.Decision).filter(models.Decision.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    d.status = "rejected"
    d.updated_at = datetime.utcnow()
    db.commit()
    audit.log_event(
        db, audit.EVENT_TYPES["DECISION_REJECTED"],
        payload={"decision_id": decision_id},
        decision_id=decision_id,
        actor="human",
    )
    return {"status": "rejected", "decision_id": decision_id}


# ── Provisioning ──────────────────────────────────────────────────────────────
@app.post("/decisions/{decision_id}/provision")
def start_provisioning(decision_id: str, db: Session = Depends(database.get_db)):
    d = db.query(models.Decision).filter(models.Decision.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    if d.status != "approved":
        raise HTTPException(400, "Decision must be approved before provisioning")
    if d.compliance_status == "fail":
        raise HTTPException(400, "Provisioning blocked: compliance check failed")

    asset = db.query(models.DataAsset).filter(models.DataAsset.id == d.data_asset_id).first()
    company = db.query(models.Company).filter(models.Company.id == d.company_id).first()

    result = provisioning_engine.generate_terraform(
        decision_id=decision_id,
        target_cloud=d.target_cloud,
        asset_name=asset.name if asset else "data-asset",
        asset_id=asset.id if asset else "unknown",
        company_id=company.id if company else "unknown",
        data_class=asset.data_class if asset else "unknown",
        hq_country=company.headquarters_country if company else "US",
    )

    job = models.ProvisioningJob(
        id=str(uuid.uuid4()),
        decision_id=decision_id,
        target_cloud=d.target_cloud,
        status="dry_run",
        iac_code=result["iac_code"],
        dry_run_output=result["dry_run_output"],
        execution_log=f"IaC generated at {result['generated_at']}. Awaiting approval.",
    )
    db.add(job)
    d.status = "provisioning"
    db.commit()
    db.refresh(job)

    audit.log_event(
        db, audit.EVENT_TYPES["PROVISIONING_DRY_RUN"],
        payload={"job_id": job.id, "target_cloud": d.target_cloud},
        decision_id=decision_id,
        actor="provisioning_engine",
    )

    return {
        "job_id": job.id,
        "status": "dry_run",
        "dry_run_output": result["dry_run_output"],
        "iac_code": result["iac_code"],
    }


@app.post("/provisioning/{job_id}/apply")
def apply_provisioning(job_id: str, db: Session = Depends(database.get_db)):
    job = db.query(models.ProvisioningJob).filter(models.ProvisioningJob.id == job_id).first()
    if not job:
        raise HTTPException(404, "Provisioning job not found")

    # Simulate apply (in production this would call Terraform CLI or API)
    job.status = "provisioned"
    job.execution_log = (
        job.execution_log + f"\nApply completed at {datetime.utcnow().isoformat()}Z. "
        "All resources created successfully."
    )

    decision = db.query(models.Decision).filter(models.Decision.id == job.decision_id).first()
    if decision:
        decision.status = "provisioned"
        decision.updated_at = datetime.utcnow()

    db.commit()

    audit.log_event(
        db, audit.EVENT_TYPES["PROVISIONING_COMPLETED"],
        payload={"job_id": job_id},
        decision_id=job.decision_id,
        actor="provisioning_engine",
    )

    return {"status": "provisioned", "job_id": job_id}


@app.get("/provisioning/{job_id}")
def get_provisioning_job(job_id: str, db: Session = Depends(database.get_db)):
    job = db.query(models.ProvisioningJob).filter(models.ProvisioningJob.id == job_id).first()
    if not job:
        raise HTTPException(404, "Provisioning job not found")
    return {
        "id": job.id,
        "decision_id": job.decision_id,
        "target_cloud": job.target_cloud,
        "status": job.status,
        "iac_code": job.iac_code,
        "dry_run_output": job.dry_run_output,
        "execution_log": job.execution_log,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }


# ── Audit Logs ────────────────────────────────────────────────────────────────
@app.get("/audit-logs")
def get_audit_logs(
    decision_id: str | None = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(database.get_db),
):
    q = db.query(models.AuditLog)
    if decision_id:
        q = q.filter(models.AuditLog.decision_id == decision_id)
    logs = q.order_by(models.AuditLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "decision_id": l.decision_id,
            "event_type": l.event_type,
            "actor": l.actor,
            "rule_version": l.rule_version,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            "payload": l.payload,
        }
        for l in logs
    ]


# ── Reports ───────────────────────────────────────────────────────────────────
@app.get("/decisions/{decision_id}/report")
def export_report(
    decision_id: str,
    format: str = Query("json", pattern="^(json|pdf)$"),
    db: Session = Depends(database.get_db),
):
    d = db.query(models.Decision).filter(models.Decision.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")

    company = db.query(models.Company).filter(models.Company.id == d.company_id).first()
    asset = db.query(models.DataAsset).filter(models.DataAsset.id == d.data_asset_id).first()
    logs = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.decision_id == decision_id)
        .order_by(models.AuditLog.timestamp)
        .all()
    )

    decision_dict = {
        "id": d.id, "recommendation": d.recommendation, "status": d.status,
        "rationale": d.rationale, "compliance_status": d.compliance_status,
        "cost_status": d.cost_status, "source_cloud": d.source_cloud,
        "target_cloud": d.target_cloud,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "data_asset_id": d.data_asset_id,
    }
    company_dict = {
        "id": company.id if company else "N/A",
        "name": company.name if company else "N/A",
        "industry": company.industry if company else "N/A",
        "headquarters_country": company.headquarters_country if company else "N/A",
    }
    asset_dict = {
        "id": asset.id if asset else "N/A",
        "name": asset.name if asset else "N/A",
        "data_class": asset.data_class if asset else "N/A",
        "sensitivity": asset.sensitivity if asset else "N/A",
        "volume_gb": asset.volume_gb if asset else 0,
    }
    cost_dict = None
    if d.cost_model:
        cm = d.cost_model
        cost_dict = {
                "current_monthly_cost": cm.current_monthly_cost,
                "target_monthly_cost": cm.target_monthly_cost,
                "egress_cost": cm.egress_cost,
                "exit_penalty": cm.exit_penalty,
                "engineering_effort_cost": cm.engineering_effort_cost,
                "downtime_risk_cost": cm.downtime_risk_cost,
                "compliance_overhead": (cm.assumptions or {}).get("compliance_overhead", 0),
                "total_migration_cost": cm.total_migration_cost,
                "monthly_savings": cm.monthly_savings,
                "breakeven_months": cm.breakeven_months,
                "three_year_net": cm.three_year_net,
            }
    logs_list = [
        {
            "id": l.id, "event_type": l.event_type, "actor": l.actor,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
        }
        for l in logs
    ]

    audit.log_event(
        db, audit.EVENT_TYPES["REPORT_EXPORTED"],
        payload={"decision_id": decision_id, "format": format},
        decision_id=decision_id,
        actor="api",
    )

    if format == "json":
        report = build_json_report(
            decision_dict, company_dict, asset_dict,
            cost_dict, d.compliance_summary or {}, logs_list
        )
        return JSONResponse(content=report)
    else:
        pdf_bytes = build_pdf_report(
            decision_dict, company_dict, asset_dict,
            cost_dict, d.compliance_summary or {}, logs_list
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=decision-{decision_id[:8]}.pdf"},
        )


# ── Dashboard Stats ───────────────────────────────────────────────────────────
@app.get("/dashboard/stats")
def dashboard_stats(db: Session = Depends(database.get_db)):
    decisions = db.query(models.Decision).all()
    companies = db.query(models.Company).all()
    assets = db.query(models.DataAsset).all()
    jobs = db.query(models.ProvisioningJob).all()

    total = len(decisions)
    rec_move = sum(1 for d in decisions if d.recommendation == "move")
    rec_stay = sum(1 for d in decisions if d.recommendation == "stay")
    rec_invest = sum(1 for d in decisions if d.recommendation == "investigate")
    comp_pass = sum(1 for d in decisions if d.compliance_status == "pass")
    comp_fail = sum(1 for d in decisions if d.compliance_status == "fail")
    provisioned = sum(1 for d in decisions if d.status == "provisioned")
    total_3yr = sum(
        (d.cost_model.three_year_net or 0) for d in decisions
        if d.cost_model and d.recommendation == "move"
    )

    no_hard_fail = sum(1 for d in decisions if d.compliance_status != "fail")
    return {
        "total_decisions": total,
        "recommendations": {"move": rec_move, "stay": rec_stay, "investigate": rec_invest},
        "compliance": {"pass": comp_pass, "fail": comp_fail, "warn": total - comp_pass - comp_fail},
        "provisioned_count": provisioned,
        "total_companies": len(companies),
        "total_assets": len(assets),
        "total_provisioning_jobs": len(jobs),
        "total_projected_3yr_savings": round(total_3yr, 2),
        "compliance_pass_rate": round(comp_pass / total * 100, 1) if total else 0,
        "no_hard_failures_rate": round(no_hard_fail / total * 100, 1) if total else 0,
    }
