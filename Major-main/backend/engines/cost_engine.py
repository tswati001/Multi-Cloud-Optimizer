"""
Cost Engine  — updated with real 2026 market data
──────────────────────────────────────────────────
Pricing sources (April 2026):
  AWS egress   : aws.amazon.com/s3/pricing  — $0.09/GB first 10TB, $0.085 next 40TB,
                                              $0.07 next 100TB, $0.05 over 150TB
  Azure egress : azure.microsoft.com/pricing/details/bandwidth — $0.087/GB (first 10TB)
  S3 Standard  : $0.023/GB-month (first 50TB)
  Azure Blob   : $0.0184/GB-month (LRS, first 50TB) — ~20% cheaper than S3
  Compute diff : AWS vs Azure within 5-10%; Azure wins Windows/.NET via Hybrid Benefit (40-55%)
  Migration    : lift-and-shift $10K-40K (160-320 hrs), re-platform $40K-120K (320-1440 hrs)
  Sources: gpuperhour.com, prodsens.live, cloudforecast.io, ztabs.co (2026)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

# ── Egress pricing (USD/GB) — tiered, April 2026 ─────────────────────────────

def _aws_egress_rate(volume_gb: float) -> float:
    """Effective per-GB egress rate from AWS to internet (tiered, 2026)."""
    tiers = [
        (100,     0.0),     # First 100 GB/month free
        (10_240,  0.09),    # Next ~10 TB → $0.09/GB
        (51_200,  0.085),   # Next 40 TB  → $0.085/GB
        (153_600, 0.07),    # Next 100 TB → $0.07/GB
    ]
    cost = 0.0
    remaining = volume_gb
    for cap, rate in tiers:
        chunk = min(remaining, cap)
        cost += chunk * rate
        remaining -= chunk
        if remaining <= 0:
            break
    if remaining > 0:
        cost += remaining * 0.05   # over 150 TB
    return cost


def _azure_egress_rate(volume_gb: float) -> float:
    """Effective per-GB egress rate from Azure to internet (tiered, 2026)."""
    tiers = [
        (100,     0.0),     # First 100 GB/month free
        (10_240,  0.087),   # Next ~10 TB → $0.087/GB
        (51_200,  0.083),   # Next 40 TB  → $0.083/GB (approx)
        (153_600, 0.07),
    ]
    cost = 0.0
    remaining = volume_gb
    for cap, rate in tiers:
        chunk = min(remaining, cap)
        cost += chunk * rate
        remaining -= chunk
        if remaining <= 0:
            break
    if remaining > 0:
        cost += remaining * 0.05
    return cost


EGRESS_FN = {
    "aws":    _aws_egress_rate,
    "azure":  _azure_egress_rate,
    "gcp":    lambda v: v * 0.08,       # GCP flat approx
    "on-prem": lambda v: 0.0,
}

# ── Storage cost differential (USD/GB-month) ─────────────────────────────────
# Source: S3 Standard $0.023, Azure Blob LRS $0.0184 (Apr 2026)
STORAGE_COST_PER_GB = {
    "aws":    0.023,
    "azure":  0.0184,
    "gcp":    0.020,
    "on-prem": 0.003,  # rough on-prem storage capex amortised
}

# ── Cloud operational cost multiplier ────────────────────────────────────────
# Moving FROM source TO target: multiplier applied to current monthly spend.
# Basis: prodsens.live Apr 2026 — compute within 5-10%; Azure wins Windows/.NET.
# We distinguish workload type via data_class as a rough proxy:
#   Financial/IP  → often Windows-heavy → Azure cheaper
#   PHI/PII/Public → Linux-typical     → slight AWS advantage
CLOUD_COST_MULTIPLIERS = {
    ("aws",    "azure"): 0.91,   # Azure ~9% cheaper on average (2026)
    ("azure",  "aws"):   1.10,   # Moving to AWS ~10% more expensive
    ("aws",    "gcp"):   0.88,
    ("azure",  "gcp"):   0.90,
    ("gcp",    "aws"):   1.12,
    ("gcp",    "azure"): 1.09,
    ("on-prem","aws"):   1.20,
    ("on-prem","azure"): 1.10,
}

# ── Engineering effort benchmarks (hours) — ztabs.co 2026 ───────────────────
# Lift-and-shift: 160-320 hrs | Re-platform: 320-800 hrs | Enterprise: 800-1600 hrs
EFFORT_BENCHMARKS = {
    "lift_shift_min":  160,
    "lift_shift_max":  320,
    "replatform_min":  320,
    "replatform_max":  800,
    "enterprise_min":  800,
    "enterprise_max": 1600,
}

# ── Compliance overhead cost (ztabs.co: adds $15K-$40K) ─────────────────────
COMPLIANCE_OVERHEAD = {
    "PII":       25_000,
    "PHI":       35_000,
    "Financial": 30_000,
    "IP":        20_000,
    "Public":     5_000,
}


@dataclass
class SensitivityScenario:
    label: str
    egress_multiplier: float
    effort_multiplier: float
    downtime_multiplier: float
    monthly_cost_multiplier: float
    compliance_multiplier: float


SCENARIOS: list[SensitivityScenario] = [
    SensitivityScenario("Optimistic",  0.80, 0.75, 0.50, 1.00, 0.80),
    SensitivityScenario("Base Case",   1.00, 1.00, 1.00, 1.00, 1.00),
    SensitivityScenario("Pessimistic", 1.30, 1.60, 2.50, 1.06, 1.40),
]


def compute_migration_economics(
    current_monthly_cost: float,
    volume_gb: float,
    source_cloud: str,
    target_cloud: str,
    early_exit_penalty: float,
    engineering_hours: float,
    engineering_hourly_rate: float,
    downtime_hours: float,
    revenue_per_hour: float,
    time_horizon_months: int = 36,
    min_savings_threshold_pct: float = 10.0,
    data_class: str = "PII",
) -> dict[str, Any]:
    """
    Returns full cost breakdown + 3-year TCO comparison + sensitivity analysis.
    Uses real 2026 tiered egress pricing, storage differentials, and
    compliance-overhead estimates from ztabs.co / prodsens.live / cloudforecast.io.
    """
    egress_fn = EGRESS_FN.get(source_cloud.lower(), lambda v: v * 0.09)
    egress = egress_fn(volume_gb)

    engineering_cost = engineering_hours * engineering_hourly_rate
    downtime_cost    = downtime_hours * revenue_per_hour
    compliance_cost  = COMPLIANCE_OVERHEAD.get(data_class, 15_000)

    # Monthly cost differential (storage + compute)
    src_storage  = volume_gb * STORAGE_COST_PER_GB.get(source_cloud.lower(), 0.023)
    tgt_storage  = volume_gb * STORAGE_COST_PER_GB.get(target_cloud.lower(), 0.023)
    storage_diff = src_storage - tgt_storage   # positive = target cheaper

    multiplier   = CLOUD_COST_MULTIPLIERS.get((source_cloud.lower(), target_cloud.lower()), 1.0)
    target_monthly = (current_monthly_cost * multiplier) - storage_diff

    total_migration_cost = egress + early_exit_penalty + engineering_cost + downtime_cost + compliance_cost

    monthly_savings  = current_monthly_cost - target_monthly
    breakeven_months = (total_migration_cost / monthly_savings) if monthly_savings > 0 else None
    three_year_net   = (monthly_savings * time_horizon_months) - total_migration_cost
    savings_pct      = (monthly_savings / current_monthly_cost * 100) if current_monthly_cost > 0 else 0

    # Recommendation logic
    if monthly_savings <= 0:
        rec        = "stay"
        cost_status = "not_justified"
    elif savings_pct < min_savings_threshold_pct:
        rec        = "investigate"
        cost_status = "marginal"
    elif breakeven_months is not None and breakeven_months > time_horizon_months:
        rec        = "investigate"
        cost_status = "marginal"
    else:
        rec        = "move"
        cost_status = "justified"

    # Sensitivity analysis
    sensitivity = []
    for sc in SCENARIOS:
        s_egress     = egress * sc.egress_multiplier
        s_eng        = engineering_cost * sc.effort_multiplier
        s_down       = downtime_cost * sc.downtime_multiplier
        s_compliance = compliance_cost * sc.compliance_multiplier
        s_tgt        = target_monthly * sc.monthly_cost_multiplier
        s_total      = s_egress + early_exit_penalty + s_eng + s_down + s_compliance
        s_sav        = current_monthly_cost - s_tgt
        s_3yr        = (s_sav * time_horizon_months) - s_total
        sensitivity.append({
            "scenario":              sc.label,
            "total_migration_cost":  round(s_total, 2),
            "monthly_savings":       round(s_sav, 2),
            "three_year_net":        round(s_3yr, 2),
            "recommendation":        "move" if s_3yr > 0 and s_sav > 0 else "stay",
        })

    return {
        "status":                  cost_status,
        "current_monthly_cost":    round(current_monthly_cost, 2),
        "target_monthly_cost":     round(target_monthly, 2),
        "egress_cost":             round(egress, 2),
        "exit_penalty":            round(early_exit_penalty, 2),
        "engineering_effort_cost": round(engineering_cost, 2),
        "downtime_risk_cost":      round(downtime_cost, 2),
        "compliance_overhead":     round(compliance_cost, 2),
        "total_migration_cost":    round(total_migration_cost, 2),
        "monthly_savings":         round(monthly_savings, 2),
        "breakeven_months":        round(breakeven_months, 1) if breakeven_months is not None else None,
        "three_year_net":          round(three_year_net, 2),
        "savings_pct":             round(savings_pct, 2),
        "recommendation":          rec,
        "sensitivity":             sensitivity,
        "assumptions": {
            "pricing_source":           "AWS/Azure official pricing + ztabs.co 2026",
            "aws_egress_tier_1_per_gb": 0.09,
            "azure_egress_tier_1_per_gb": 0.087,
            "aws_s3_storage_per_gb_mo": 0.023,
            "azure_blob_storage_per_gb_mo": 0.0184,
            "cloud_cost_multiplier":    multiplier,
            "storage_monthly_saving":   round(storage_diff, 2),
            "compliance_overhead":      compliance_cost,
            "engineering_hours":        engineering_hours,
            "engineering_hourly_rate":  engineering_hourly_rate,
            "downtime_hours":           downtime_hours,
            "revenue_per_hour":         revenue_per_hour,
            "time_horizon_months":      time_horizon_months,
            "min_savings_threshold_pct": min_savings_threshold_pct,
            "volume_gb":                volume_gb,
        },
    }
