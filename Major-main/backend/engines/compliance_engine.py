"""
Compliance Engine  — updated with real 2026 regulatory data
─────────────────────────────────────────────────────────────
Sources (April 2026):
  GDPR adequacy list : ec.europa.eu/info/law/law-topic/data-protection (incl. Brazil draft,
                       UK renewed Dec 2025, US via DPF)
  India DPDP Act 2023 + Rules 2025 : notified Nov 13, 2025 — NO mandatory localisation,
                       "permitted unless restricted" default; core obligations kick in
                       May 2027 (18 months from notification). Treat as WARN not hard block.
  HIPAA (US)         : PHI must stay in BAA-covered US regions; AWS + Azure both offer BAAs
  CCPA (US-CA)       : Disclosure obligations for CA PII; no transfer block
  SOC 2 Type II      : AZ redundancy, access controls, encryption standards
  EU AI Act (2025)   : High-risk AI data must stay in EU/adequate — flagged as warn for IP
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

# ── Versioned policy packs ────────────────────────────────────────────────────

POLICY_PACKS: dict[str, dict] = {

    "GDPR": {
        "version": "2026-v2",
        "jurisdiction": "EU",
        "rules": [
            {
                "id": "GDPR-01",
                "name": "EU Data Residency / Adequacy",
                "description": (
                    "Personal data of EU residents must be stored within the EEA or in a country "
                    "with an EU adequacy decision. Updated Dec 2025: UK renewed, Brazil in final stages."
                ),
                "severity": "hard",
                "applies_to_data_classes": ["PII"],
                "allowed_target_regions": [
                    # EEA members
                    "EU", "DE", "FR", "NL", "IE", "SE", "PL", "IT", "ES", "BE", "AT",
                    "DK", "FI", "PT", "LU", "CZ", "HU", "RO", "HR", "BG", "SK", "SI",
                    "EE", "LV", "LT", "CY", "MT", "GR",
                    # Adequacy decisions (EU Commission, Apr 2026)
                    "UK",   # renewed Dec 2025
                    "US",   # via EU-US Data Privacy Framework (DPF, 2023)
                    "CA",   # PIPEDA-covered commercial orgs
                    "JP",   # with complementary safeguards
                    "KR",   # South Korea
                    "NZ",
                    "CH",   # Switzerland
                    "AR",   # Argentina
                    "UY",   # Uruguay
                    "IL",   # Israel
                    "BR",   # Brazil — adequacy in final stages (EDPB opinion Nov 2025)
                    "AD",   # Andorra
                    "GG", "JE", "IM",   # Crown dependencies
                    "FO",               # Faroe Islands
                ],
                "condition": "target_region_in_allowed_list",
            },
            {
                "id": "GDPR-02",
                "name": "Standard Contractual Clauses (SCCs)",
                "description": (
                    "Transfers to non-adequate countries require SCCs (2021 version) or BCRs. "
                    "SCCs must be signed before transfer commences."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["PII"],
                "condition": "scc_present_or_target_adequate",
            },
            {
                "id": "GDPR-03",
                "name": "Data Processing Agreement (DPA)",
                "description": (
                    "A DPA compliant with Art. 28 GDPR must exist between the controller and "
                    "the target cloud processor. Both AWS and Azure offer standard DPAs."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["PII"],
                "condition": "always_warn",
            },
            {
                "id": "GDPR-04",
                "name": "EU AI Act — High-Risk AI Data",
                "description": (
                    "Under the EU AI Act (in force Aug 2024, obligations from 2025-2026), "
                    "training/validation data for high-risk AI systems must meet GDPR obligations "
                    "including residency. Flagged as informational warning for IP data."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["IP"],
                "condition": "always_warn",
            },
        ],
    },

    "HIPAA": {
        "version": "2026-v1",
        "jurisdiction": "US",
        "rules": [
            {
                "id": "HIPAA-01",
                "name": "PHI Must Stay in BAA-Covered US Jurisdiction",
                "description": (
                    "Protected Health Information (ePHI) must remain within the US or in regions "
                    "covered by a Business Associate Agreement. Both AWS and Azure offer BAAs "
                    "for US regions (GovCloud and commercial US). "
                    "HHS Office for Civil Rights enforces HIPAA — violations up to $1.9M/year per category."
                ),
                "severity": "hard",
                "applies_to_data_classes": ["PHI"],
                "allowed_target_regions": ["US"],
                "condition": "target_region_in_allowed_list",
            },
            {
                "id": "HIPAA-02",
                "name": "Business Associate Agreement Required",
                "description": (
                    "A signed BAA must exist with the target cloud provider. "
                    "AWS (aws.amazon.com/compliance/hipaa-eligible-services-reference) "
                    "and Azure (microsoft.com/en-us/trust-center/compliance/hipaa) both "
                    "provide standard BAAs at no additional cost."
                ),
                "severity": "hard",
                "applies_to_data_classes": ["PHI"],
                "condition": "baa_required",
                "baa_providers": ["aws", "azure"],
            },
            {
                "id": "HIPAA-03",
                "name": "Encryption In Transit and At Rest (AES-256 / TLS 1.2+)",
                "description": (
                    "HIPAA Security Rule requires encryption for ePHI in transit (TLS 1.2 minimum) "
                    "and at rest (AES-256). Generated IaC enforces both via KMS/customer-managed keys."
                ),
                "severity": "hard",
                "applies_to_data_classes": ["PHI"],
                "condition": "always_pass",
            },
            {
                "id": "HIPAA-04",
                "name": "Audit Controls and Access Logging",
                "description": (
                    "HIPAA 164.312(b) requires hardware, software, and procedural mechanisms "
                    "to record and examine activity in systems containing ePHI. "
                    "AWS CloudTrail / Azure Monitor must be enabled."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["PHI"],
                "condition": "always_warn",
            },
        ],
    },

    "CCPA": {
        "version": "2026-v1",
        "jurisdiction": "US-CA",
        "rules": [
            {
                "id": "CCPA-01",
                "name": "CPRA Privacy Notice Update Required",
                "description": (
                    "CCPA as amended by CPRA (2023) requires updating privacy notices when "
                    "data is moved to a new service provider. Consumers must be notified of "
                    "new data-sharing arrangements."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["PII"],
                "condition": "always_warn",
            },
            {
                "id": "CCPA-02",
                "name": "Service Provider Obligation Clauses",
                "description": (
                    "Target cloud provider must sign CPRA-compliant service provider contracts "
                    "restricting use of personal data solely for contracted purposes. "
                    "AWS and Azure provide standard CCPA addenda."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["PII"],
                "condition": "always_warn",
            },
            {
                "id": "CCPA-03",
                "name": "No Sale / Sharing of Personal Data Without Opt-Out",
                "description": (
                    "Migrating data to a new cloud provider does not constitute a 'sale' "
                    "under CCPA as long as use is limited to service provision."
                ),
                "severity": "hard",
                "applies_to_data_classes": ["PII"],
                "condition": "always_pass",
            },
        ],
    },

    "DPDP": {
        "version": "2026-v1",
        "jurisdiction": "IN",
        "rules": [
            {
                "id": "DPDP-01",
                "name": "India DPDP Act 2023 — Cross-Border Transfer (No Mandatory Localisation)",
                "description": (
                    "DPDP Rules 2025 (notified Nov 13, 2025): India adopts 'permitted unless "
                    "restricted' model — no mandatory localisation as of Apr 2026. "
                    "Government may notify restricted jurisdictions in future. "
                    "Core obligations (consent, security, breach reporting) apply from May 2027. "
                    "Design for unpredictability: ensure data can be recalled to IN if needed."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["PII", "PHI", "Financial"],
                "applies_to_regions": ["IN"],
                "condition": "always_warn",
            },
            {
                "id": "DPDP-02",
                "name": "Data Fiduciary Registration (>10M records)",
                "description": (
                    "Significant Data Fiduciaries processing data of >10 million users must "
                    "register with the Data Protection Board of India. Triggers enhanced audit "
                    "and localisation requirements once rules are fully notified."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["PII"],
                "applies_to_regions": ["IN"],
                "condition": "always_warn",
            },
        ],
    },

    "PDPB_LEGACY": {
        "version": "2026-deprecated",
        "jurisdiction": "IN-LEGACY",
        "rules": [
            {
                "id": "PDPB-LEGACY-01",
                "name": "India PDPB — Superseded by DPDP Act 2023",
                "description": (
                    "The Personal Data Protection Bill (PDPB) was withdrawn in August 2022. "
                    "It has been replaced by the Digital Personal Data Protection (DPDP) Act 2023. "
                    "This rule is archived for historical audit trail purposes."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["all"],
                "condition": "always_warn",
            },
        ],
    },

    "SOC2": {
        "version": "2026-v1",
        "jurisdiction": "global",
        "rules": [
            {
                "id": "SOC2-01",
                "name": "Multi-AZ Redundancy (Availability Criterion CC9.1)",
                "description": (
                    "SOC 2 Type II requires replication across at least two availability zones. "
                    "Both AWS S3 (11 9s durability) and Azure GRS (geo-redundant) satisfy this. "
                    "Confirm target region supports multi-AZ."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["all"],
                "condition": "always_warn",
            },
            {
                "id": "SOC2-02",
                "name": "Encryption Key Management (CC6.1)",
                "description": (
                    "Customer-managed keys (CMK/BYOK) required for SOC 2 CC6.1 compliance. "
                    "Generated Terraform uses AWS KMS with auto-rotation / Azure Key Vault HSM."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["PII", "PHI", "Financial", "IP"],
                "condition": "always_pass",
            },
            {
                "id": "SOC2-03",
                "name": "Logical Access Controls (CC6.2 / CC6.3)",
                "description": (
                    "IAM roles with least-privilege policies must be defined. "
                    "Generated IaC includes role-based access; periodic review cadence must be set."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["all"],
                "condition": "always_warn",
            },
        ],
    },

    "INTERNAL": {
        "version": "2026-v1",
        "jurisdiction": "internal",
        "rules": [
            {
                "id": "INT-01",
                "name": "Approved Cloud Providers (AWS and Azure Only)",
                "description": (
                    "Only AWS and Azure are approved for production workloads per internal policy. "
                    "GCP and on-prem migrations require a separate waiver process."
                ),
                "severity": "hard",
                "applies_to_data_classes": ["all"],
                "approved_providers": ["aws", "azure"],
                "condition": "target_in_approved_providers",
            },
            {
                "id": "INT-02",
                "name": "IP / Trade Secret — Provider Data-Ownership Clause",
                "description": (
                    "Intellectual property must only be hosted with cloud providers whose ToS "
                    "do not claim data ownership. Both AWS (s.a. 5) and Azure (s.a. 6) "
                    "explicitly disclaim ownership of customer data."
                ),
                "severity": "hard",
                "applies_to_data_classes": ["IP"],
                "approved_providers": ["aws", "azure"],
                "condition": "target_in_approved_providers",
            },
            {
                "id": "INT-03",
                "name": "Minimum TLS Version (TLS 1.2+)",
                "description": (
                    "All data in transit must use TLS 1.2 or higher. "
                    "AWS and Azure enforce this by default. "
                    "Generated Terraform sets `min_tls_version = TLS1_2`."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["all"],
                "condition": "always_pass",
            },
        ],
    },

    "PCI_DSS": {
        "version": "2026-v1",
        "jurisdiction": "global",
        "rules": [
            {
                "id": "PCI-01",
                "name": "Cardholder Data Environment (CDE) Isolation",
                "description": (
                    "PCI DSS v4.0 (effective Apr 2024) requires the CDE to be isolated in a "
                    "network segment. Financial data moving to a new cloud must replicate "
                    "network segmentation controls (VPC/VNet + security groups/NSGs)."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["Financial"],
                "condition": "always_warn",
            },
            {
                "id": "PCI-02",
                "name": "PCI DSS v4.0 — Qualified Security Assessor Review",
                "description": (
                    "Any change to the CDE — including cloud migration — requires a QSA review "
                    "and updated Report on Compliance (ROC) or Self-Assessment Questionnaire (SAQ). "
                    "Budget for QSA fees ($15K-$60K) in migration cost."
                ),
                "severity": "warn",
                "applies_to_data_classes": ["Financial"],
                "condition": "always_warn",
            },
        ],
    },
}

# ── Region → Country → Adequacy mapping ───────────────────────────────────────

COUNTRY_REGION_MAP = {
    # EU member states
    "DE": "EU", "FR": "EU", "NL": "EU", "IE": "EU", "SE": "EU",
    "PL": "EU", "IT": "EU", "ES": "EU", "BE": "EU", "AT": "EU",
    "DK": "EU", "FI": "EU", "PT": "EU", "LU": "EU", "CZ": "EU",
    "HU": "EU", "RO": "EU", "HR": "EU", "BG": "EU", "SK": "EU",
    "SI": "EU", "EE": "EU", "LV": "EU", "LT": "EU", "CY": "EU",
    "MT": "EU", "GR": "EU",
    # Non-EU adequacy
    "GB": "UK", "UK": "UK",
    "US": "US", "CA": "CA", "JP": "JP", "KR": "KR",
    "NZ": "NZ", "CH": "CH", "AR": "AR", "UY": "UY",
    "IL": "IL", "BR": "BR",
    "AD": "AD", "GG": "GG", "JE": "JE", "IM": "IM", "FO": "FO",
    # Other
    "IN": "IN", "SG": "SG", "AU": "AU", "AE": "AE", "ZA": "ZA",
    "CN": "CN", "RU": "RU",
}

ADEQUACY_COUNTRIES = {
    "EU", "UK", "US", "CA", "JP", "KR", "NZ", "CH", "AR", "UY",
    "IL", "BR", "AD", "GG", "JE", "IM", "FO",
    "DE", "FR", "NL", "IE", "SE", "PL", "IT", "ES", "BE", "AT",
    "DK", "FI", "PT", "LU", "CZ", "HU", "RO", "HR", "BG", "SK",
    "SI", "EE", "LV", "LT", "CY", "MT", "GR",
}


@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    severity: str
    status: str     # pass / fail / warn / skipped
    explanation: str
    evidence: dict = field(default_factory=dict)


def _evaluate_rule(
    rule: dict,
    data_class: str,
    residency_constraints: list[str],
    hq_country: str,
    target_cloud: str,
    source_cloud: str,
) -> RuleResult:
    rid      = rule["id"]
    rname    = rule["name"]
    severity = rule["severity"]
    cond     = rule["condition"]
    applies  = rule.get("applies_to_data_classes", ["all"])

    # Applicability check
    if applies != ["all"] and data_class not in applies:
        return RuleResult(rid, rname, severity, "skipped",
                          f"Rule does not apply to data class '{data_class}'.")

    if cond == "always_pass":
        return RuleResult(rid, rname, severity, "pass",
                          "Condition is always satisfied by platform controls.")

    if cond == "always_warn":
        return RuleResult(rid, rname, severity, "warn", rule["description"])

    if cond == "target_region_in_allowed_list":
        allowed = set(rule.get("allowed_target_regions", []))
        violated = [
            c for c in residency_constraints
            if COUNTRY_REGION_MAP.get(c.upper(), c.upper()) not in allowed
            and c.upper() not in allowed
        ]
        if violated:
            return RuleResult(rid, rname, severity, "fail",
                              f"Residency constraints {violated} are NOT in the allowed target "
                              f"regions for {rid}. Allowed: {sorted(allowed)[:8]}…",
                              {"violated_constraints": violated,
                               "allowed_regions": sorted(allowed)})
        return RuleResult(rid, rname, severity, "pass",
                          "All residency constraints are satisfied by the target cloud region.",
                          {"residency_constraints": residency_constraints,
                           "allowed_regions": sorted(allowed)[:8]})

    if cond == "baa_required":
        providers = rule.get("baa_providers", [])
        if target_cloud.lower() in providers:
            return RuleResult(rid, rname, severity, "pass",
                              f"{target_cloud.upper()} provides a signed BAA for PHI at no cost.")
        return RuleResult(rid, rname, severity, "fail",
                          f"{target_cloud.upper()} does not offer a pre-signed BAA.")

    if cond == "scc_present_or_target_adequate":
        all_adequate = all(
            COUNTRY_REGION_MAP.get(c.upper(), c.upper()) in ADEQUACY_COUNTRIES
            or c.upper() in ADEQUACY_COUNTRIES
            for c in residency_constraints
        )
        if all_adequate:
            return RuleResult(rid, rname, severity, "pass",
                              "Target regions are in EU-adequate jurisdictions; SCCs not required.")
        return RuleResult(rid, rname, severity, "warn",
                          "Some target regions lack adequacy decisions — ensure 2021 SCCs or BCRs are in place.")

    if cond == "target_in_approved_providers":
        approved = rule.get("approved_providers", [])
        if target_cloud.lower() in approved:
            return RuleResult(rid, rname, severity, "pass",
                              f"{target_cloud.upper()} is an approved cloud provider.")
        return RuleResult(rid, rname, severity, "fail",
                          f"{target_cloud.upper()} is not in the approved list: {approved}.")

    return RuleResult(rid, rname, severity, "warn",
                      f"Condition '{cond}' is not implemented — manual review required.")


def run_compliance_check(
    data_class: str,
    residency_constraints: list[str],
    hq_country: str,
    operating_regions: list[str],
    target_cloud: str,
    source_cloud: str,
) -> dict[str, Any]:
    """
    Run all applicable policy packs and return a structured compliance result.
    Pack selection is based on data class, operating regions, and HQ country.
    """
    all_results: list[RuleResult] = []
    active_packs: set[str] = set()

    # Internal always
    active_packs.add("INTERNAL")

    # SOC 2 always
    active_packs.add("SOC2")

    # GDPR — any EU operation, EU HQ, or EU residency constraint
    eu_set = {"EU", "DE", "FR", "NL", "IE", "SE", "PL", "IT", "ES", "BE", "AT",
              "DK", "FI", "PT", "LU", "CZ", "HU", "RO", "HR", "BG", "SK",
              "SI", "EE", "LV", "LT", "CY", "MT", "GR"}
    all_regions = set(r.upper() for r in operating_regions + residency_constraints + [hq_country])
    mapped_regions = {COUNTRY_REGION_MAP.get(r, r) for r in all_regions}
    if mapped_regions & eu_set or all_regions & eu_set:
        active_packs.add("GDPR")

    # HIPAA — PHI data class AND the company has US operations or US HQ
    # HIPAA is a US federal law; UK/EU companies managing PHI are governed by UK GDPR / EEA rules
    us_presence = "US" in all_regions or "US" == hq_country.upper()
    if data_class == "PHI" and us_presence:
        active_packs.add("HIPAA")

    # CCPA — US operations + PII
    if "US" in all_regions and data_class == "PII":
        active_packs.add("CCPA")

    # DPDP — India HQ or operating region (replaces old PDPB)
    if any(r in {"IN", "INDIA"} for r in all_regions):
        active_packs.add("DPDP")

    # PCI DSS — Financial data class
    if data_class == "Financial":
        active_packs.add("PCI_DSS")

    # Evaluate
    for pack_id in sorted(active_packs):
        pack = POLICY_PACKS[pack_id]
        for rule in pack["rules"]:
            result = _evaluate_rule(
                rule=rule,
                data_class=data_class,
                residency_constraints=residency_constraints,
                hq_country=hq_country,
                target_cloud=target_cloud,
                source_cloud=source_cloud,
            )
            all_results.append(result)

    hard_failures = [r for r in all_results if r.status == "fail" and r.severity == "hard"]
    soft_failures = [r for r in all_results if r.status == "fail" and r.severity != "hard"]
    warnings      = [r for r in all_results if r.status == "warn"]
    passing       = [r for r in all_results if r.status == "pass"]
    skipped       = [r for r in all_results if r.status == "skipped"]

    if hard_failures:
        overall = "fail"
    elif soft_failures or warnings:
        overall = "warn"
    else:
        overall = "pass"

    checks = [
        {
            "rule_id":     r.rule_id,
            "rule_name":   r.rule_name,
            "severity":    r.severity,
            "status":      r.status,
            "explanation": r.explanation,
            "evidence":    r.evidence,
        }
        for r in all_results
    ]

    return {
        "status":          overall,
        "checks":          checks,
        "blocking_rules":  [r.rule_id for r in hard_failures],
        "passing_rules":   [r.rule_id for r in passing],
        "warnings":        [r.explanation for r in warnings],
        "evidence": {
            "active_policy_packs":   sorted(active_packs),
            "policy_versions":       {k: POLICY_PACKS[k]["version"] for k in sorted(active_packs)},
            "regulatory_update_date": "2026-04-14",
            "total_rules_evaluated": len(all_results),
            "hard_failures":         len(hard_failures),
            "soft_failures":         len(soft_failures),
            "warnings":              len(warnings),
            "passed":                len(passing),
            "skipped":               len(skipped),
        },
    }
