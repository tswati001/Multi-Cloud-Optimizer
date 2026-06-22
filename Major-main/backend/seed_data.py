"""
Seed demo data for the Cloud Agility Broker.
Run once to populate the SQLite database with realistic scenarios.
"""

import requests
import sys

BASE = "http://localhost:8000"


def post(path, data):
    r = requests.post(f"{BASE}{path}", json=data)
    if r.status_code not in (200, 201):
        print(f"  WARN {path}: {r.status_code} {r.text[:120]}")
        return None
    return r.json()


def seed():
    print("Seeding demo data...")

    # ── Companies ─────────────────────────────────────────────────────────────
    companies = [
        {
            "id": "comp-001",
            "name": "HealthBridge Analytics",
            "industry": "Healthcare",
            "headquarters_country": "US",
            "operating_regions": ["US", "CA"],
            "ownership_structure": "private",
        },
        {
            "id": "comp-002",
            "name": "EuroFinance GmbH",
            "industry": "Financial Services",
            "headquarters_country": "DE",
            "operating_regions": ["DE", "FR", "NL", "UK"],
            "ownership_structure": "private",
        },
        {
            "id": "comp-003",
            "name": "TechStream India Pvt Ltd",
            "industry": "SaaS",
            "headquarters_country": "IN",
            "operating_regions": ["IN", "SG", "US"],
            "ownership_structure": "subsidiary",
        },
    ]
    for c in companies:
        r = post("/companies", c)
        print(f"  Company: {c['name']} — {r and 'OK' or 'SKIP'}")

    # ── Data Assets ───────────────────────────────────────────────────────────
    assets = [
        {
            "id": "asset-001",
            "company_id": "comp-001",
            "name": "Patient Records DB",
            "data_class": "PHI",
            "sensitivity": "critical",
            "residency_constraints": ["US"],
            "volume_gb": 2048,
            "current_cloud": "aws",
            "target_cloud": "azure",
        },
        {
            "id": "asset-002",
            "company_id": "comp-002",
            "name": "EU Customer PII Store",
            "data_class": "PII",
            "sensitivity": "high",
            "residency_constraints": ["EU", "DE"],
            "volume_gb": 500,
            "current_cloud": "azure",
            "target_cloud": "aws",
        },
        {
            "id": "asset-003",
            "company_id": "comp-002",
            "name": "Transaction Ledger",
            "data_class": "Financial",
            "sensitivity": "critical",
            "residency_constraints": ["EU"],
            "volume_gb": 1200,
            "current_cloud": "azure",
            "target_cloud": "aws",
        },
        {
            "id": "asset-004",
            "company_id": "comp-003",
            "name": "Product Analytics Events",
            "data_class": "Public",
            "sensitivity": "low",
            "residency_constraints": [],
            "volume_gb": 8000,
            "current_cloud": "aws",
            "target_cloud": "azure",
        },
        {
            "id": "asset-005",
            "company_id": "comp-003",
            "name": "Indian User PII",
            "data_class": "PII",
            "sensitivity": "high",
            "residency_constraints": ["IN"],
            "volume_gb": 300,
            "current_cloud": "aws",
            "target_cloud": "azure",
        },
    ]
    for a in assets:
        r = post("/assets", a)
        print(f"  Asset: {a['name']} — {r and 'OK' or 'SKIP'}")

    # ── Cloud Accounts ─────────────────────────────────────────────────────────
    accounts = [
        {
            "id": "acct-001",
            "company_id": "comp-001",
            "provider": "aws",
            "account_id": "123456789012",
            "region": "us-east-1",
            "monthly_spend_usd": 85000,
            "contract_end_date": "2025-12-31",
            "early_exit_penalty_usd": 45000,
        },
        {
            "id": "acct-002",
            "company_id": "comp-002",
            "provider": "azure",
            "account_id": "sub-eur-001",
            "region": "westeurope",
            "monthly_spend_usd": 120000,
            "contract_end_date": "2025-06-30",
            "early_exit_penalty_usd": 30000,
        },
        {
            "id": "acct-003",
            "company_id": "comp-003",
            "provider": "aws",
            "account_id": "987654321098",
            "region": "ap-south-1",
            "monthly_spend_usd": 40000,
            "contract_end_date": "2026-03-31",
            "early_exit_penalty_usd": 0,
        },
    ]
    for a in accounts:
        r = post("/cloud-accounts", a)
        print(f"  Account: {a['provider'].upper()} — {r and 'OK' or 'SKIP'}")

    # ── Broker Evaluations ─────────────────────────────────────────────────────
    evaluations = [
        {
            "company_id": "comp-001",
            "data_asset_id": "asset-001",
            "time_horizon_months": 36,
            "min_savings_threshold_pct": 8.0,
            "engineering_hourly_rate": 175.0,
            "engineering_hours_estimate": 250.0,
            "downtime_hours_estimate": 6.0,
            "revenue_per_hour": 80000.0,
        },
        {
            "company_id": "comp-002",
            "data_asset_id": "asset-002",
            "time_horizon_months": 36,
            "min_savings_threshold_pct": 10.0,
            "engineering_hourly_rate": 150.0,
            "engineering_hours_estimate": 200.0,
            "downtime_hours_estimate": 4.0,
            "revenue_per_hour": 60000.0,
        },
        {
            "company_id": "comp-002",
            "data_asset_id": "asset-003",
            "time_horizon_months": 36,
            "min_savings_threshold_pct": 10.0,
            "engineering_hourly_rate": 150.0,
            "engineering_hours_estimate": 300.0,
            "downtime_hours_estimate": 8.0,
            "revenue_per_hour": 100000.0,
        },
        {
            "company_id": "comp-003",
            "data_asset_id": "asset-004",
            "time_horizon_months": 36,
            "min_savings_threshold_pct": 5.0,
            "engineering_hourly_rate": 120.0,
            "engineering_hours_estimate": 150.0,
            "downtime_hours_estimate": 2.0,
            "revenue_per_hour": 20000.0,
        },
        {
            "company_id": "comp-003",
            "data_asset_id": "asset-005",
            "time_horizon_months": 36,
            "min_savings_threshold_pct": 10.0,
            "engineering_hourly_rate": 120.0,
            "engineering_hours_estimate": 180.0,
            "downtime_hours_estimate": 3.0,
            "revenue_per_hour": 20000.0,
        },
    ]
    decision_ids = []
    for ev in evaluations:
        r = post("/broker/evaluate", ev)
        if r:
            did = r.get("decision_id")
            rec = r.get("recommendation")
            print(f"  Decision: {did[:8]}... -> {rec.upper()}")
            decision_ids.append((did, rec))

    # Approve and provision the "move" decisions
    for did, rec in decision_ids:
        if rec == "move":
            ra = requests.post(f"{BASE}/decisions/{did}/approve")
            if ra.status_code == 200:
                rp = requests.post(f"{BASE}/decisions/{did}/provision")
                if rp.status_code == 200:
                    job_id = rp.json().get("job_id")
                    # Auto-apply first one for demo
                    requests.post(f"{BASE}/provisioning/{job_id}/apply")
                    print(f"  Provisioned: {did[:8]}...")

    print("\nSeed complete!")


if __name__ == "__main__":
    seed()
