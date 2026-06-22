"""
Full demo seed — 2026 realistic scenarios
==========================================
8 companies · 14 data assets · 8 cloud accounts · 14 broker evaluations
Covers every compliance outcome: PASS, WARN, FAIL, and edge cases.
"""

import urllib.request
import json
import urllib.error
import time

BASE = "http://localhost:8000"


def post(path: str, data: dict | None = None, retries: int = 3) -> dict | None:
    for attempt in range(retries):
        req = urllib.request.Request(
            f"{BASE}{path}",
            data=json.dumps(data or {}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            r = urllib.request.urlopen(req, timeout=30)
            return json.loads(r.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"  WARN {path} [{e.code}]: {body[:100]}")
            return None
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"  ERROR {path}: {e}")
                return None
    return None


def ok(result, name: str) -> bool:
    if result:
        print(f"  [OK]  {name}")
        return True
    print(f"  [SKIP] {name}")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# COMPANIES
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== Companies ===")

COMPANIES = [
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
    {
        "id": "comp-004",
        "name": "MediCore UK Ltd",
        "industry": "Healthcare",
        "headquarters_country": "UK",
        "operating_regions": ["UK", "EU", "AU"],
        "ownership_structure": "public",
    },
    {
        "id": "comp-005",
        "name": "Samba Fintech Brasil",
        "industry": "Financial Services",
        "headquarters_country": "BR",
        "operating_regions": ["BR", "AR", "US"],
        "ownership_structure": "private",
    },
    {
        "id": "comp-006",
        "name": "NovaTech Singapore Pte Ltd",
        "industry": "Technology",
        "headquarters_country": "SG",
        "operating_regions": ["SG", "AU", "JP"],
        "ownership_structure": "private",
    },
    {
        "id": "comp-007",
        "name": "GlobalRetail Corp",
        "industry": "Retail",
        "headquarters_country": "US",
        "operating_regions": ["US", "CA", "MX", "UK"],
        "ownership_structure": "public",
    },
    {
        "id": "comp-008",
        "name": "AeroData Systems",
        "industry": "Aerospace",
        "headquarters_country": "DE",
        "operating_regions": ["DE", "FR", "US"],
        "ownership_structure": "subsidiary",
    },
]
for c in COMPANIES:
    ok(post("/companies", c), c["name"])


# ─────────────────────────────────────────────────────────────────────────────
# DATA ASSETS
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== Data Assets ===")

ASSETS = [
    # HealthBridge — PHI US, HIPAA block on out-of-US move
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
    # HealthBridge — analytics (non-PHI), free to move
    {
        "id": "asset-002",
        "company_id": "comp-001",
        "name": "Clinical Analytics Warehouse",
        "data_class": "Public",
        "sensitivity": "low",
        "residency_constraints": [],
        "volume_gb": 12000,
        "current_cloud": "aws",
        "target_cloud": "azure",
    },
    # EuroFinance — EU PII, GDPR strict
    {
        "id": "asset-003",
        "company_id": "comp-002",
        "name": "EU Customer PII Store",
        "data_class": "PII",
        "sensitivity": "high",
        "residency_constraints": ["EU", "DE"],
        "volume_gb": 500,
        "current_cloud": "azure",
        "target_cloud": "aws",
    },
    # EuroFinance — financial ledger, PCI DSS
    {
        "id": "asset-004",
        "company_id": "comp-002",
        "name": "Transaction Ledger",
        "data_class": "Financial",
        "sensitivity": "critical",
        "residency_constraints": ["EU"],
        "volume_gb": 1800,
        "current_cloud": "azure",
        "target_cloud": "aws",
    },
    # TechStream — product analytics, no constraints, big volume
    {
        "id": "asset-005",
        "company_id": "comp-003",
        "name": "Product Analytics Events",
        "data_class": "Public",
        "sensitivity": "low",
        "residency_constraints": [],
        "volume_gb": 15000,
        "current_cloud": "aws",
        "target_cloud": "azure",
    },
    # TechStream — Indian user PII, DPDP Act (warn not block)
    {
        "id": "asset-006",
        "company_id": "comp-003",
        "name": "Indian User PII",
        "data_class": "PII",
        "sensitivity": "high",
        "residency_constraints": ["IN"],
        "volume_gb": 420,
        "current_cloud": "aws",
        "target_cloud": "azure",
    },
    # MediCore UK — PHI UK/EU, HIPAA doesn't apply (UK company) but GDPR does
    {
        "id": "asset-007",
        "company_id": "comp-004",
        "name": "UK Patient Health Records",
        "data_class": "PHI",
        "sensitivity": "critical",
        "residency_constraints": ["UK", "EU"],
        "volume_gb": 3500,
        "current_cloud": "azure",
        "target_cloud": "aws",
    },
    # MediCore UK — IP/research data
    {
        "id": "asset-008",
        "company_id": "comp-004",
        "name": "Clinical Trial IP Dataset",
        "data_class": "IP",
        "sensitivity": "high",
        "residency_constraints": ["UK"],
        "volume_gb": 800,
        "current_cloud": "azure",
        "target_cloud": "aws",
    },
    # Samba Fintech — Brazil PII, Brazil now has EU adequacy (draft)
    {
        "id": "asset-009",
        "company_id": "comp-005",
        "name": "Brazil Customer PII",
        "data_class": "PII",
        "sensitivity": "high",
        "residency_constraints": ["BR"],
        "volume_gb": 650,
        "current_cloud": "aws",
        "target_cloud": "azure",
    },
    # Samba — financial transactions
    {
        "id": "asset-010",
        "company_id": "comp-005",
        "name": "Payment Transaction Records",
        "data_class": "Financial",
        "sensitivity": "critical",
        "residency_constraints": ["BR"],
        "volume_gb": 950,
        "current_cloud": "aws",
        "target_cloud": "azure",
    },
    # NovaTech SG — Public data lake, large volume
    {
        "id": "asset-011",
        "company_id": "comp-006",
        "name": "APAC Data Lake",
        "data_class": "Public",
        "sensitivity": "low",
        "residency_constraints": [],
        "volume_gb": 25000,
        "current_cloud": "azure",
        "target_cloud": "aws",
    },
    # GlobalRetail — customer PII, US + UK cross-border
    {
        "id": "asset-012",
        "company_id": "comp-007",
        "name": "Global Customer Profiles",
        "data_class": "PII",
        "sensitivity": "high",
        "residency_constraints": ["US", "UK"],
        "volume_gb": 1200,
        "current_cloud": "aws",
        "target_cloud": "azure",
    },
    # AeroData — IP/trade secrets
    {
        "id": "asset-013",
        "company_id": "comp-008",
        "name": "Aircraft Design IP",
        "data_class": "IP",
        "sensitivity": "critical",
        "residency_constraints": ["DE", "FR", "US"],
        "volume_gb": 2200,
        "current_cloud": "aws",
        "target_cloud": "azure",
    },
    # AeroData — PHI (aerospace medical fitness data) — will be blocked (PHI must stay US, but DE company)
    {
        "id": "asset-014",
        "company_id": "comp-008",
        "name": "Pilot Health Compliance Data",
        "data_class": "PHI",
        "sensitivity": "critical",
        "residency_constraints": ["DE"],  # This will FAIL HIPAA-01 (PHI must stay US, but constrained to DE)
        "volume_gb": 120,
        "current_cloud": "aws",
        "target_cloud": "azure",
    },
]
for a in ASSETS:
    ok(post("/assets", a), a["name"])


# ─────────────────────────────────────────────────────────────────────────────
# CLOUD ACCOUNTS (source cloud spend + exit terms)
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== Cloud Accounts ===")

ACCOUNTS = [
    {
        "id": "acct-001",
        "company_id": "comp-001",
        "provider": "aws",
        "account_id": "123456789012",
        "region": "us-east-1",
        "monthly_spend_usd": 98000,
        "contract_end_date": "2026-12-31",
        "early_exit_penalty_usd": 58000,
    },
    {
        "id": "acct-002",
        "company_id": "comp-002",
        "provider": "azure",
        "account_id": "sub-eur-2024",
        "region": "germanywestcentral",
        "monthly_spend_usd": 145000,
        "contract_end_date": "2026-09-30",
        "early_exit_penalty_usd": 40000,
    },
    {
        "id": "acct-003",
        "company_id": "comp-003",
        "provider": "aws",
        "account_id": "987654321098",
        "region": "ap-south-1",
        "monthly_spend_usd": 52000,
        "contract_end_date": "2027-03-31",
        "early_exit_penalty_usd": 0,
    },
    {
        "id": "acct-004",
        "company_id": "comp-004",
        "provider": "azure",
        "account_id": "sub-uk-2024",
        "region": "uksouth",
        "monthly_spend_usd": 210000,
        "contract_end_date": "2027-01-31",
        "early_exit_penalty_usd": 75000,
    },
    {
        "id": "acct-005",
        "company_id": "comp-005",
        "provider": "aws",
        "account_id": "555777888999",
        "region": "sa-east-1",
        "monthly_spend_usd": 38000,
        "contract_end_date": "2026-06-30",
        "early_exit_penalty_usd": 0,
    },
    {
        "id": "acct-006",
        "company_id": "comp-006",
        "provider": "azure",
        "account_id": "sub-apac-2024",
        "region": "southeastasia",
        "monthly_spend_usd": 67000,
        "contract_end_date": "2026-11-30",
        "early_exit_penalty_usd": 15000,
    },
    {
        "id": "acct-007",
        "company_id": "comp-007",
        "provider": "aws",
        "account_id": "111222333444",
        "region": "us-east-1",
        "monthly_spend_usd": 180000,
        "contract_end_date": "2027-06-30",
        "early_exit_penalty_usd": 90000,
    },
    {
        "id": "acct-008",
        "company_id": "comp-008",
        "provider": "aws",
        "account_id": "444555666777",
        "region": "eu-central-1",
        "monthly_spend_usd": 75000,
        "contract_end_date": "2026-08-31",
        "early_exit_penalty_usd": 20000,
    },
]
for a in ACCOUNTS:
    ok(post("/cloud-accounts", a), f"{a['provider'].upper()} / {a['company_id']}")


# ─────────────────────────────────────────────────────────────────────────────
# BROKER EVALUATIONS
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== Broker Evaluations ===")

EVALUATIONS = [
    # 1. PHI US → Azure US (should PASS HIPAA, WARN on SOC2/CCPA) — investigate due to high exit fee
    {
        "company_id": "comp-001", "data_asset_id": "asset-001",
        "time_horizon_months": 36, "min_savings_threshold_pct": 8.0,
        "engineering_hourly_rate": 175.0, "engineering_hours_estimate": 320.0,
        "downtime_hours_estimate": 6.0, "revenue_per_hour": 90000.0,
    },
    # 2. Clinical analytics (Public) AWS → Azure — large volume, should recommend MOVE
    {
        "company_id": "comp-001", "data_asset_id": "asset-002",
        "time_horizon_months": 36, "min_savings_threshold_pct": 5.0,
        "engineering_hourly_rate": 150.0, "engineering_hours_estimate": 200.0,
        "downtime_hours_estimate": 2.0, "revenue_per_hour": 40000.0,
    },
    # 3. EU PII Azure → AWS — GDPR OK (AWS EU regions), should MOVE
    {
        "company_id": "comp-002", "data_asset_id": "asset-003",
        "time_horizon_months": 36, "min_savings_threshold_pct": 8.0,
        "engineering_hourly_rate": 160.0, "engineering_hours_estimate": 240.0,
        "downtime_hours_estimate": 4.0, "revenue_per_hour": 65000.0,
    },
    # 4. Financial ledger Azure → AWS — PCI DSS warns, high exit penalty, STAY
    {
        "company_id": "comp-002", "data_asset_id": "asset-004",
        "time_horizon_months": 36, "min_savings_threshold_pct": 10.0,
        "engineering_hourly_rate": 160.0, "engineering_hours_estimate": 400.0,
        "downtime_hours_estimate": 8.0, "revenue_per_hour": 120000.0,
    },
    # 5. TechStream public analytics AWS → Azure — 15TB, no constraints, MOVE
    {
        "company_id": "comp-003", "data_asset_id": "asset-005",
        "time_horizon_months": 36, "min_savings_threshold_pct": 5.0,
        "engineering_hourly_rate": 120.0, "engineering_hours_estimate": 160.0,
        "downtime_hours_estimate": 2.0, "revenue_per_hour": 20000.0,
    },
    # 6. Indian PII AWS → Azure — DPDP WARN (not block), investigate savings
    {
        "company_id": "comp-003", "data_asset_id": "asset-006",
        "time_horizon_months": 36, "min_savings_threshold_pct": 10.0,
        "engineering_hourly_rate": 120.0, "engineering_hours_estimate": 200.0,
        "downtime_hours_estimate": 3.0, "revenue_per_hour": 25000.0,
    },
    # 7. UK PHI Azure → AWS — HIPAA doesn't apply (UK co, not US PHI), GDPR warn, MOVE
    {
        "company_id": "comp-004", "data_asset_id": "asset-007",
        "time_horizon_months": 36, "min_savings_threshold_pct": 7.0,
        "engineering_hourly_rate": 180.0, "engineering_hours_estimate": 350.0,
        "downtime_hours_estimate": 8.0, "revenue_per_hour": 150000.0,
    },
    # 8. Clinical Trial IP Azure → AWS — internal check passes, MOVE
    {
        "company_id": "comp-004", "data_asset_id": "asset-008",
        "time_horizon_months": 36, "min_savings_threshold_pct": 6.0,
        "engineering_hourly_rate": 180.0, "engineering_hours_estimate": 200.0,
        "downtime_hours_estimate": 4.0, "revenue_per_hour": 80000.0,
    },
    # 9. Brazil PII AWS → Azure — BR now in GDPR adequacy draft, investigate
    {
        "company_id": "comp-005", "data_asset_id": "asset-009",
        "time_horizon_months": 36, "min_savings_threshold_pct": 8.0,
        "engineering_hourly_rate": 130.0, "engineering_hours_estimate": 180.0,
        "downtime_hours_estimate": 3.0, "revenue_per_hour": 30000.0,
    },
    # 10. Brazil Financial AWS → Azure — PCI DSS warns, INVESTIGATE
    {
        "company_id": "comp-005", "data_asset_id": "asset-010",
        "time_horizon_months": 36, "min_savings_threshold_pct": 10.0,
        "engineering_hourly_rate": 130.0, "engineering_hours_estimate": 300.0,
        "downtime_hours_estimate": 6.0, "revenue_per_hour": 50000.0,
    },
    # 11. APAC Data Lake Azure → AWS — 25TB, no constraints, MOVE
    {
        "company_id": "comp-006", "data_asset_id": "asset-011",
        "time_horizon_months": 36, "min_savings_threshold_pct": 5.0,
        "engineering_hourly_rate": 140.0, "engineering_hours_estimate": 180.0,
        "downtime_hours_estimate": 2.0, "revenue_per_hour": 35000.0,
    },
    # 12. GlobalRetail PII AWS → Azure — US + UK constraints, both adequate, MOVE
    {
        "company_id": "comp-007", "data_asset_id": "asset-012",
        "time_horizon_months": 36, "min_savings_threshold_pct": 8.0,
        "engineering_hourly_rate": 165.0, "engineering_hours_estimate": 280.0,
        "downtime_hours_estimate": 5.0, "revenue_per_hour": 100000.0,
    },
    # 13. AeroData IP AWS → Azure — EU adequacy OK, MOVE with GDPR warns
    {
        "company_id": "comp-008", "data_asset_id": "asset-013",
        "time_horizon_months": 36, "min_savings_threshold_pct": 7.0,
        "engineering_hourly_rate": 170.0, "engineering_hours_estimate": 320.0,
        "downtime_hours_estimate": 6.0, "revenue_per_hour": 70000.0,
    },
    # 14. AeroData Pilot PHI — DE constraint FAILS HIPAA-01 (PHI must stay US) → STAY/BLOCKED
    {
        "company_id": "comp-008", "data_asset_id": "asset-014",
        "time_horizon_months": 36, "min_savings_threshold_pct": 5.0,
        "engineering_hourly_rate": 170.0, "engineering_hours_estimate": 160.0,
        "downtime_hours_estimate": 2.0, "revenue_per_hour": 50000.0,
    },
]

decision_ids: list[tuple[str, str]] = []
for i, ev in enumerate(EVALUATIONS, 1):
    r = post("/broker/evaluate", ev)
    if r:
        did = r.get("decision_id", "")
        rec = r.get("recommendation", "")
        comp = r.get("compliance", {}).get("status", "")
        print(f"  [{i:02d}] {did[:8]} | {rec.upper():12s} | compliance={comp.upper()} | "
              f"asset={ev['data_asset_id']}")
        decision_ids.append((did, rec))
    time.sleep(0.2)  # avoid hammering the DB


# ─────────────────────────────────────────────────────────────────────────────
# APPROVE + PROVISION move decisions
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== Provisioning ===")
provisioned = 0
for did, rec in decision_ids:
    if rec == "move":
        ra = post(f"/decisions/{did}/approve")
        if ra:
            rp = post(f"/decisions/{did}/provision")
            if rp:
                jid = rp.get("job_id", "")
                ra2 = post(f"/provisioning/{jid}/apply")
                if ra2:
                    print(f"  [OK]  Provisioned: {did[:8]} (job {jid[:8]})")
                    provisioned += 1
        time.sleep(0.3)


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
import urllib.request as ur

r = ur.urlopen(f"{BASE}/dashboard/stats", timeout=10)
stats = json.loads(r.read())
print("\n=== Seed Complete ===")
print(f"  Companies          : {stats['total_companies']}")
print(f"  Data Assets        : {stats['total_assets']}")
print(f"  Total Decisions    : {stats['total_decisions']}")
print(f"  MOVE decisions     : {stats['recommendations']['move']}")
print(f"  STAY decisions     : {stats['recommendations']['stay']}")
print(f"  INVESTIGATE        : {stats['recommendations']['investigate']}")
print(f"  Compliance FAIL    : {stats['compliance']['fail']}")
print(f"  Compliance WARN    : {stats['compliance']['warn']}")
print(f"  No-Hard-Fail rate  : {stats.get('no_hard_failures_rate', 'N/A')}%")
print(f"  Provisioned        : {stats['provisioned_count']}")
print(f"  3-yr savings proj  : ${stats['total_projected_3yr_savings']:,.0f}")
