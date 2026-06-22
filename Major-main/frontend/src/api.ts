import axios from 'axios'

const API_BASE_URL = (
  // Vite exposes env vars prefixed with VITE_ via import.meta.env
  // Falls back to localhost for development
  (import.meta as any).env?.VITE_API_BASE || 'http://127.0.0.1:8000'
)

const api = axios.create({ baseURL: API_BASE_URL })

export interface Company {
  id: string
  name: string
  industry: string
  headquarters_country: string
  operating_regions: string[]
  ownership_structure: string
}

export interface DataAsset {
  id: string
  company_id: string
  name: string
  data_class: string
  sensitivity: string
  residency_constraints: string[]
  volume_gb: number
  current_cloud: string
  target_cloud: string
}

export interface CostModel {
  current_monthly_cost: number
  target_monthly_cost: number
  egress_cost: number
  exit_penalty: number
  engineering_effort_cost: number
  downtime_risk_cost: number
  compliance_overhead?: number
  total_migration_cost: number
  monthly_savings: number
  breakeven_months: number | null
  three_year_net: number
  assumptions?: Record<string, unknown>
}

export interface ComplianceCheck {
  rule_id: string
  rule_name: string
  severity: string
  status: string
  explanation: string
  evidence: Record<string, unknown>
}

export interface ComplianceSummary {
  status: string
  checks: ComplianceCheck[]
  blocking_rules: string[]
  passing_rules: string[]
  warnings: string[]
  evidence: Record<string, unknown>
}

export interface Decision {
  id: string
  company_id: string
  data_asset_id: string
  source_cloud: string
  target_cloud: string
  compliance_status: string
  compliance_summary?: ComplianceSummary
  cost_status: string
  recommendation: string
  rationale: string
  status: string
  created_at: string
  cost_model?: CostModel | null
}

export interface BrokerRequest {
  company_id: string
  data_asset_id: string
  time_horizon_months: number
  min_savings_threshold_pct: number
  engineering_hourly_rate: number
  engineering_hours_estimate: number
  downtime_hours_estimate: number
  revenue_per_hour: number
}

export interface BrokerResult {
  decision_id: string
  recommendation: string
  compliance: ComplianceSummary
  cost: CostModel & { sensitivity: Array<Record<string, unknown>>; recommendation: string; savings_pct: number }
  rationale: string
  status: string
}

export interface ProvisioningJob {
  id: string
  decision_id: string
  target_cloud: string
  status: string
  iac_code: string
  dry_run_output: string
  execution_log: string
  created_at: string
}

export interface AuditLog {
  id: string
  decision_id: string | null
  event_type: string
  actor: string
  rule_version: string
  timestamp: string
  payload: Record<string, unknown>
}

export interface DashboardStats {
  total_decisions: number
  recommendations: { move: number; stay: number; investigate: number }
  compliance: { pass: number; fail: number; warn: number }
  provisioned_count: number
  total_companies: number
  total_assets: number
  total_provisioning_jobs: number
  total_projected_3yr_savings: number
  compliance_pass_rate: number
  no_hard_failures_rate: number
}

// ── API calls ─────────────────────────────────────────────────────────────────

export const getStats = () => api.get<DashboardStats>('/dashboard/stats').then(r => r.data)
export const getCompanies = () => api.get<Company[]>('/companies').then(r => r.data)
export const getCompany = (id: string) => api.get<Company>(`/companies/${id}`).then(r => r.data)
export const createCompany = (data: Omit<Company, 'id'> & { id: string }) =>
  api.post<Company>('/companies', data).then(r => r.data)

export const getAssets = (companyId?: string) =>
  api.get<DataAsset[]>('/assets', { params: companyId ? { company_id: companyId } : {} }).then(r => r.data)
export const getAsset = (id: string) => api.get<DataAsset>(`/assets/${id}`).then(r => r.data)
export const createAsset = (data: DataAsset) => api.post<DataAsset>('/assets', data).then(r => r.data)

export const getCloudAccounts = (companyId?: string) =>
  api.get('/cloud-accounts', { params: companyId ? { company_id: companyId } : {} }).then(r => r.data)
export const createCloudAccount = (data: object) =>
  api.post('/cloud-accounts', data).then(r => r.data)

export const getPolicyPacks = () => api.get('/policy-packs').then(r => r.data)

export const evaluate = (request: BrokerRequest) =>
  api.post<BrokerResult>('/broker/evaluate', request).then(r => r.data)

export const getDecisions = (companyId?: string) =>
  api.get<Decision[]>('/decisions', { params: companyId ? { company_id: companyId } : {} }).then(r => r.data)
export const getDecision = (id: string) => api.get<Decision>(`/decisions/${id}`).then(r => r.data)
export const approveDecision = (id: string) =>
  api.post(`/decisions/${id}/approve`).then(r => r.data)
export const rejectDecision = (id: string) =>
  api.post(`/decisions/${id}/reject`).then(r => r.data)
export const startProvisioning = (id: string) =>
  api.post<ProvisioningJob>(`/decisions/${id}/provision`).then(r => r.data)

export const getProvisioningJob = (id: string) =>
  api.get<ProvisioningJob>(`/provisioning/${id}`).then(r => r.data)
export const applyProvisioning = (id: string) =>
  api.post(`/provisioning/${id}/apply`).then(r => r.data)

export const getAuditLogs = (decisionId?: string, limit = 50) =>
  api.get<AuditLog[]>('/audit-logs', {
    params: { ...(decisionId ? { decision_id: decisionId } : {}), limit },
  }).then(r => r.data)

export const getReport = (id: string, format: 'json' | 'pdf') =>
  api.get(`/decisions/${id}/report`, {
    params: { format },
    responseType: format === 'pdf' ? 'blob' : 'json',
  }).then(r => r.data)

export default api
