"""Quick end-to-end verification of all major API endpoints."""
import urllib.request
import json


def get(path):
    r = urllib.request.urlopen(f"http://localhost:8000{path}", timeout=10)
    return json.loads(r.read())


print("=== Dashboard Stats ===")
stats = get("/dashboard/stats")
for k, v in stats.items():
    print(f"  {k}: {v}")

print("\n=== Decisions ===")
decisions = get("/decisions")
for d in decisions:
    cm = d.get("cost_model") or {}
    did = d["id"][:8]
    src = d["source_cloud"].upper()
    tgt = d["target_cloud"].upper()
    comp = d["compliance_status"]
    rec = d["recommendation"]
    sav = cm.get("monthly_savings", 0) or 0
    print(f"  {did} | {src}->{tgt} | comp={comp} | rec={rec} | savings=${sav:,.0f}/mo")

print("\n=== Policy Packs ===")
packs = get("/policy-packs")
for p in packs:
    pid = p["id"]
    jur = p["jurisdiction"]
    cnt = p["rule_count"]
    ver = p["name"]
    print(f"  {pid:12s} | {jur:8s} | {cnt} rules | v{ver}")

print("\n=== Provisioning Jobs ===")
for d in decisions:
    if d["status"] == "provisioned":
        print(f"  Decision {d['id'][:8]} -> provisioned ({d['target_cloud'].upper()})")

print("\n=== Audit Log Sample ===")
logs = get("/audit-logs?limit=5")
for log in logs:
    ts = log["timestamp"][:19]
    et = log["event_type"]
    ac = log["actor"]
    rv = log["rule_version"]
    print(f"  {ts} | {et} | {ac} | v{rv}")

print("\n=== Health ===")
health = get("/health")
print(f"  status={health['status']} version={health['version']}")

print("\n=== Compliance Check on a FAIL decision ===")
fail_decisions = [d for d in decisions if d["compliance_status"] == "fail"]
if fail_decisions:
    fd = get(f"/decisions/{fail_decisions[0]['id']}")
    cs = fd.get("compliance_summary", {})
    blocking = cs.get("blocking_rules", [])
    print(f"  Decision: {fd['id'][:8]} | Blocking rules: {blocking}")
    for check in cs.get("checks", []):
        if check["status"] == "fail":
            print(f"    FAIL: {check['rule_id']} - {check['explanation'][:80]}")

print("\nAll checks passed!")
