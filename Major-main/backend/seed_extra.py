"""Run remaining evaluations after initial seed."""
import urllib.request
import json
import urllib.error


def post(path, data=None):
    req = urllib.request.Request(
        f"http://localhost:8000{path}",
        data=json.dumps(data or {}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        r = urllib.request.urlopen(req, timeout=30)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  WARN {path}: {e.code} {body[:80]}")
        return None


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

for ev in evaluations:
    r = post("/broker/evaluate", ev)
    if r:
        did = r.get("decision_id")
        rec = r.get("recommendation")
        print(f"  Decision: {did[:8]} -> {rec}")
        if rec == "move":
            post(f"/decisions/{did}/approve")
            prov = post(f"/decisions/{did}/provision")
            if prov:
                jid = prov["job_id"]
                post(f"/provisioning/{jid}/apply")
                print(f"    Provisioned job {jid[:8]}")

print("Done!")
