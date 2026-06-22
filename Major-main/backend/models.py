from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime,
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from database import Base


# ── SQLAlchemy ORM ────────────────────────────────────────────────────────────

class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    industry = Column(String)
    headquarters_country = Column(String)
    operating_regions = Column(JSON)   # list[str]
    ownership_structure = Column(String)  # public / private / subsidiary
    created_at = Column(DateTime, default=datetime.utcnow)

    data_assets = relationship("DataAsset", back_populates="company")
    cloud_accounts = relationship("CloudAccount", back_populates="company")
    decisions = relationship("Decision", back_populates="company")


class DataAsset(Base):
    __tablename__ = "data_assets"
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))
    name = Column(String, nullable=False)
    data_class = Column(String)          # PII / PHI / Financial / IP / Public
    sensitivity = Column(String)         # critical / high / medium / low
    residency_constraints = Column(JSON) # list[str] — required countries/regions
    volume_gb = Column(Float)
    current_cloud = Column(String)       # aws / azure / gcp / on-prem
    target_cloud = Column(String)

    company = relationship("Company", back_populates="data_assets")


class CloudAccount(Base):
    __tablename__ = "cloud_accounts"
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))
    provider = Column(String)            # aws / azure
    account_id = Column(String)
    region = Column(String)
    monthly_spend_usd = Column(Float)
    contract_end_date = Column(String)
    early_exit_penalty_usd = Column(Float)

    company = relationship("Company", back_populates="cloud_accounts")


class PolicyPack(Base):
    __tablename__ = "policy_packs"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    jurisdiction = Column(String)        # GDPR / CCPA / HIPAA / PDPB / custom
    version = Column(String)
    rules = Column(JSON)                 # list[rule dicts]
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CostModel(Base):
    __tablename__ = "cost_models"
    id = Column(String, primary_key=True)
    decision_id = Column(String, ForeignKey("decisions.id"))
    current_monthly_cost = Column(Float)
    target_monthly_cost = Column(Float)
    egress_cost = Column(Float)
    exit_penalty = Column(Float)
    engineering_effort_cost = Column(Float)
    downtime_risk_cost = Column(Float)
    total_migration_cost = Column(Float)
    monthly_savings = Column(Float)
    breakeven_months = Column(Float)
    three_year_net = Column(Float)
    assumptions = Column(JSON)

    decision = relationship("Decision", back_populates="cost_model")


class Decision(Base):
    __tablename__ = "decisions"
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"))
    data_asset_id = Column(String, ForeignKey("data_assets.id"))
    source_cloud = Column(String)
    target_cloud = Column(String)
    compliance_status = Column(String)   # pass / fail / warn
    compliance_summary = Column(JSON)
    cost_status = Column(String)         # justified / not_justified / marginal
    recommendation = Column(String)      # move / stay / investigate
    rationale = Column(Text)
    status = Column(String, default="pending")  # pending / approved / rejected / provisioned
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="decisions")
    cost_model = relationship("CostModel", back_populates="decision", uselist=False)
    provisioning_jobs = relationship("ProvisioningJob", back_populates="decision")
    audit_logs = relationship("AuditLog", back_populates="decision")


class ProvisioningJob(Base):
    __tablename__ = "provisioning_jobs"
    id = Column(String, primary_key=True)
    decision_id = Column(String, ForeignKey("decisions.id"))
    target_cloud = Column(String)
    status = Column(String, default="pending")  # pending / dry_run / approved / provisioned / failed / rolled_back
    iac_code = Column(Text)
    execution_log = Column(Text)
    dry_run_output = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    decision = relationship("Decision", back_populates="provisioning_jobs")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True)
    decision_id = Column(String, ForeignKey("decisions.id"), nullable=True)
    event_type = Column(String)
    actor = Column(String)
    payload = Column(JSON)
    rule_version = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    decision = relationship("Decision", back_populates="audit_logs")


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class CompanyCreate(BaseModel):
    id: str
    name: str
    industry: str
    headquarters_country: str
    operating_regions: list[str]
    ownership_structure: str = "private"


class DataAssetCreate(BaseModel):
    id: str
    company_id: str
    name: str
    data_class: str
    sensitivity: str
    residency_constraints: list[str]
    volume_gb: float
    current_cloud: str
    target_cloud: str


class CloudAccountCreate(BaseModel):
    id: str
    company_id: str
    provider: str
    account_id: str
    region: str
    monthly_spend_usd: float
    contract_end_date: str
    early_exit_penalty_usd: float


class BrokerRequest(BaseModel):
    company_id: str
    data_asset_id: str
    time_horizon_months: int = 36
    min_savings_threshold_pct: float = 10.0
    engineering_hourly_rate: float = 150.0
    engineering_hours_estimate: float = 200.0
    downtime_hours_estimate: float = 4.0
    revenue_per_hour: float = 50000.0


class ComplianceResult(BaseModel):
    status: str
    checks: list[dict[str, Any]]
    blocking_rules: list[str]
    passing_rules: list[str]
    warnings: list[str]
    evidence: dict[str, Any]


class CostResult(BaseModel):
    status: str
    current_monthly_cost: float
    target_monthly_cost: float
    egress_cost: float
    exit_penalty: float
    engineering_effort_cost: float
    downtime_risk_cost: float
    total_migration_cost: float
    monthly_savings: float
    breakeven_months: float
    three_year_net: float
    savings_pct: float
    recommendation: str


class DecisionOut(BaseModel):
    id: str
    company_id: str
    data_asset_id: str
    source_cloud: str
    target_cloud: str
    compliance_status: str
    compliance_summary: dict[str, Any]
    cost_status: str
    recommendation: str
    rationale: str
    status: str
    created_at: datetime
    cost_model: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True
