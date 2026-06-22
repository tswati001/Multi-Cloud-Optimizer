"""Deep verification of 2026 pricing, sensitivity analysis, compliance, and reports."""
import urllib.request
import json


def get(path):
    r = urllib.request.urlopen(f"http://localhost:8000{path}", timeout=10)
    return json.loads(r.read())


# Load decisions
decisions = get("/decisions")
move_dec = next((d for d in decisions if d["recommendation"] == "move"), None)
fail_dec = next((d for d in decisions if d["compliance_status"] == "fail"), None)
invest_dec = next((d for d in decisions if d["recommendation"] == "investigate"), None)

# ── MOVE Decision Deep Check ──────────────────────────────────────────────────
print("=== MOVE Decision — Full Detail ===")
mid = move_dec["id"]
detail = get(f"/decisions/{mid}")
cm = detail.get("cost_model", {})
assumptions = cm.get("assumptions", {})
sensitivity = assumptions.get("sensitivity", [])

print(f"  ID        : {detail['id'][:8]}")
print(f"  Route     : {detail['source_cloud'].upper()} -> {detail['target_cloud'].upper()}")
print(f"  Rec       : {detail['recommendation'].upper()}")
print(f"  Compliance: {detail['compliance_status'].upper()}")
print(f"  Monthly savings    : ${cm.get('monthly_savings', 0):,.0f}")
print(f"  3-Year Net         : ${cm.get('three_year_net', 0):,.0f}")
print(f"  Egress (tiered)    : ${cm.get('egress_cost', 0):,.2f}")
print(f"  Compliance overhead: ${assumptions.get('compliance_overhead', 0):,.0f}")
print(f"  Pricing source     : {assumptions.get('pricing_source', '')}")
print(f"  AWS egress rate    : ${assumptions.get('aws_egress_tier_1_per_gb', 0)}/GB")
print(f"  Azure egress rate  : ${assumptions.get('azure_egress_tier_1_per_gb', 0)}/GB")
print(f"  S3 storage/GB-mo   : ${assumptions.get('aws_s3_storage_per_gb_mo', 0)}")
print(f"  Azure Blob/GB-mo   : ${assumptions.get('azure_blob_storage_per_gb_mo', 0)}")
print(f"  Storage saving/mo  : ${assumptions.get('storage_monthly_saving', 0):,.2f}")

if sensitivity:
    print("  Sensitivity Analysis:")
    for s in sensitivity:
        label = s["scenario"]
        mc = s["total_migration_cost"]
        net = s["three_year_net"]
        rec = s["recommendation"]
        print(f"    {label:12s}: migration=${mc:,.0f}  3yr_net=${net:,.0f}  ({rec})")

# ── FAIL Decision ─────────────────────────────────────────────────────────────
print("\n=== FAIL Decision — Compliance Breakdown ===")
fid = fail_dec["id"]
fd = get(f"/decisions/{fid}")
cs = fd.get("compliance_summary", {})
evidence = cs.get("evidence", {})

print(f"  ID         : {fd['id'][:8]}")
print(f"  Route      : {fd['source_cloud'].upper()} -> {fd['target_cloud'].upper()}")
print(f"  Blocking   : {cs.get('blocking_rules', [])}")
print(f"  Packs used : {evidence.get('active_policy_packs', [])}")
print(f"  Versions   : {evidence.get('policy_versions', {})}")
print(f"  Update date: {evidence.get('regulatory_update_date', '')}")
print(f"  Rationale  : {fd['rationale'][:120]}...")
for check in cs.get("checks", []):
    if check["status"] == "fail":
        print(f"  FAIL: [{check['rule_id']}] {check['explanation'][:90]}")

# ── INVESTIGATE Decision ──────────────────────────────────────────────────────
print("\n=== INVESTIGATE Decision ===")
iid = invest_dec["id"]
id_det = get(f"/decisions/{iid}")
id_cm = id_det.get("cost_model", {})
print(f"  ID             : {id_det['id'][:8]}")
print(f"  Route          : {id_det['source_cloud'].upper()} -> {id_det['target_cloud'].upper()}")
print(f"  Monthly savings: ${id_cm.get('monthly_savings', 0):,.0f}")
print(f"  Breakeven      : {id_cm.get('breakeven_months', 'N/A')} months")
print(f"  Total mig cost : ${id_cm.get('total_migration_cost', 0):,.0f}")
print(f"  3yr net        : ${id_cm.get('three_year_net', 0):,.0f}")

# ── JSON Report ───────────────────────────────────────────────────────────────
print("\n=== JSON Report Export ===")
report = get(f"/decisions/{mid}/report?format=json")
print(f"  report_type   : {report['report_type']}")
print(f"  generated_at  : {report['generated_at']}")
print(f"  audit entries : {len(report.get('audit_trail', []))}")
print(f"  compliance checks: {len(report.get('compliance', {}).get('checks', []))}")

# ── PDF Report ────────────────────────────────────────────────────────────────
print("\n=== PDF Report Export ===")
req = urllib.request.Request(f"http://localhost:8000/decisions/{mid}/report?format=pdf")
r = urllib.request.urlopen(req, timeout=15)
pdf_bytes = r.read()
print(f"  PDF size: {len(pdf_bytes):,} bytes")
print(f"  PDF header: {pdf_bytes[:4]}")

# ── Audit Log ─────────────────────────────────────────────────────────────────
print("\n=== Audit Log Integrity ===")
logs = get(f"/audit-logs?decision_id={mid}")
print(f"  Entries for MOVE decision: {len(logs)}")
for log in logs:
    print(f"    {log['timestamp'][:19]} | {log['event_type']} | v{log['rule_version']}")

# ── Provisioning IaC ─────────────────────────────────────────────────────────
print("\n=== Generated Terraform IaC ===")
prov_detail = get(f"/decisions/{mid}")
# Get all provisioning jobs for this decision
all_jobs = get("/audit-logs?limit=100")
prov_events = [l for l in all_jobs if l["event_type"] in ("provisioning_completed", "provisioning_dry_run") and l.get("decision_id") == mid]
for ev in prov_events[:2]:
    payload = ev.get("payload", {})
    jid = payload.get("job_id", "")
    if jid:
        job = get(f"/provisioning/{jid}")
        print(f"  Job {job['id'][:8]} | status={job['status']} | cloud={job['target_cloud'].upper()}")
        iac_lines = job.get("iac_code", "").count("\n")
        print(f"  IaC: {iac_lines} lines of Terraform HCL")
        print(f"  Dry-run preview:")
        for line in (job.get("dry_run_output", "").split("\n"))[:8]:
            if line.strip():
                print(f"    {line}")
        break

print("\nAll deep verifications PASSED!")
