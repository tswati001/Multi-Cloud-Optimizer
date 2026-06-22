# Cloud Agility Broker

An automated decision engine that determines whether a company's data should stay on AWS, move to Azure, or remain where it is — based on legal eligibility and total migration economics.

## Architecture

```
frontend/   React + TypeScript + Tailwind + Recharts (port 5173)
backend/    FastAPI + SQLAlchemy + SQLite            (port 8000)
```

### Core Engines

| Engine | What it does |
|--------|-------------|
| **Compliance Engine** | Evaluates data movement against GDPR, HIPAA, CCPA, PDPB, SOC 2, and Internal policy packs |
| **Cost Engine** | Computes egress, exit penalties, engineering effort, downtime risk, and 3-year TCO |
| **Provisioning Engine** | Generates Terraform HCL for AWS (S3 + KMS + IAM) or Azure (Storage + Key Vault + RBAC) |
| **Audit Module** | Immutable append-only event trail for every check and action |
| **Report Generator** | PDF and JSON decision reports |

---

## Running Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

### Seed Demo Data

```bash
cd backend
python seed_extra.py
```

This populates 3 companies, 5 data assets, 3 cloud accounts, and 7 migration decisions.

---

## Demo Scenarios

| Company | Asset | Move | Why |
|---------|-------|------|-----|
| HealthBridge Analytics | Patient Records DB (PHI, US) | Investigate | HIPAA passes, marginal savings |
| EuroFinance GmbH | EU Customer PII (GDPR) | Stay | AWS costs more for this workload |
| EuroFinance GmbH | Transaction Ledger | Stay | Downtime risk exceeds savings |
| TechStream India | Product Analytics (Public) | **MOVE** | 8% savings, breakeven <3yr |
| TechStream India | Indian User PII | Investigate | PDPB constraints |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/broker/evaluate` | Full broker evaluation |
| GET | `/decisions` | List all decisions |
| GET | `/decisions/{id}` | Decision detail |
| POST | `/decisions/{id}/approve` | Approve migration |
| POST | `/decisions/{id}/provision` | Generate + dry-run Terraform |
| POST | `/provisioning/{id}/apply` | Apply infrastructure |
| GET | `/decisions/{id}/report?format=pdf\|json` | Export report |
| GET | `/dashboard/stats` | KPI summary |
| GET | `/policy-packs` | Active compliance rules |
| GET | `/audit-logs` | Immutable event log |

Interactive API docs: **http://localhost:8000/docs**

---

## Data Model

- **Company** — profile, regions, industry, ownership
- **DataAsset** — class (PII/PHI/Financial/IP/Public), sensitivity, residency constraints
- **CloudAccount** — source cloud spend, contract terms, exit penalties
- **PolicyPack** — 6 built-in rule sets, versioned
- **CostModel** — migration economics assumptions and outputs
- **Decision** — final recommendation with rationale
- **ProvisioningJob** — IaC code, dry-run output, execution log
- **AuditLog** — immutable event trail

---

## Policy Packs (MVP)

- **GDPR** — EU data residency, SCCs, DPAs
- **HIPAA** — PHI US residency, Business Associate Agreements
- **CCPA** — California consumer rights disclosure
- **PDPB** — India data localisation
- **SOC 2** — availability zone redundancy
- **Internal** — approved cloud providers, IP ownership

---

*Built for the Cloud Agility Broker PRD · MVP scope: AWS + Azure · Terraform-based provisioning*
