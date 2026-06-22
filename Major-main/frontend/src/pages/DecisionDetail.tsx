import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  CheckCircle, XCircle, AlertTriangle, ArrowRight, Download,
  Server, FileJson, Loader2, ChevronDown, ChevronUp
} from 'lucide-react'
import {
  getDecision, getAuditLogs, approveDecision, rejectDecision,
  startProvisioning, applyProvisioning, getReport,
  type Decision, type AuditLog, type ProvisioningJob,
} from '../api'
import StatusBadge from '../components/StatusBadge'
import CloudIcon from '../components/CloudIcon'

export default function DecisionDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [decision, setDecision] = useState<Decision | null>(null)
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [job, setJob] = useState<ProvisioningJob | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [showIac, setShowIac] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const reload = () => {
    if (!id) return
    Promise.all([getDecision(id), getAuditLogs(id)]).then(([d, l]) => {
      setDecision(d)
      setLogs(l)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { reload() }, [id])

  const action = async (fn: () => Promise<unknown>, msg?: string) => {
    setActionLoading(true)
    setError(null)
    try {
      const result = await fn() as { job_id?: string; iac_code?: string; dry_run_output?: string }
      if (result?.job_id) {
        setJob({ id: result.job_id, iac_code: result.iac_code || '', dry_run_output: result.dry_run_output || '', decision_id: id!, target_cloud: decision?.target_cloud || '', status: 'dry_run', execution_log: '', created_at: new Date().toISOString() })
      }
      reload()
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      setError(e?.response?.data?.detail || msg || 'Action failed')
    } finally {
      setActionLoading(false)
    }
  }

  const downloadPdf = async () => {
    if (!id) return
    const blob = await getReport(id, 'pdf')
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `decision-${id.slice(0, 8)}.pdf`; a.click()
  }

  const downloadJson = async () => {
    if (!id) return
    const data = await getReport(id, 'json')
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `decision-${id.slice(0, 8)}.json`; a.click()
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
    </div>
  )
  if (!decision) return <div className="p-8 text-slate-600">Decision not found.</div>

  const cm = decision.cost_model
  const cs = decision.compliance_summary

  return (
    <div className="p-8 space-y-6 max-w-4xl">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <button onClick={() => navigate('/decisions')} className="hover:text-slate-800">Decisions</button>
        <ChevronDown size={12} className="-rotate-90" />
        <span className="text-slate-800 font-mono">{decision.id.slice(0, 8)}…</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <CloudIcon cloud={decision.source_cloud} size="md" />
            <ArrowRight size={16} className="text-slate-500" />
            <CloudIcon cloud={decision.target_cloud} size="md" />
            <StatusBadge value={decision.recommendation} />
            <StatusBadge value={decision.status} />
          </div>
          <p className="text-xs text-slate-500 font-mono">{decision.id}</p>
        </div>

        <div className="flex gap-2">
          <button onClick={downloadJson} className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition-colors border border-slate-200">
            <FileJson size={12} /> JSON
          </button>
          <button onClick={downloadPdf} className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition-colors border border-slate-200">
            <Download size={12} /> PDF Report
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-800 text-sm">
          {error}
        </div>
      )}

      {/* Rationale */}
      <div className="card p-5">
        <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-2">Rationale</h3>
        <p className="text-slate-700 text-sm leading-relaxed">{decision.rationale}</p>
      </div>

      {/* Compliance */}
      {cs && (
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide">
              Compliance — {cs.checks?.length} rules
            </h3>
            <StatusBadge value={cs.status} />
          </div>

          {cs.blocking_rules?.length > 0 && (
            <div className="mb-3 bg-red-50 border border-red-200 rounded-lg p-3 text-red-800 text-xs">
              <strong>Blocking rules:</strong> {cs.blocking_rules.join(', ')}
            </div>
          )}

          <div className="space-y-2">
            {cs.checks?.map(c => (
              <div key={c.rule_id} className={`flex items-start gap-3 text-sm p-2.5 rounded-lg ${
                c.status === 'fail' ? 'bg-red-500/5' :
                c.status === 'warn' ? 'bg-amber-500/5' :
                c.status === 'skipped' ? 'opacity-40' : 'bg-emerald-500/5'
              }`}>
                {c.status === 'pass' && <CheckCircle size={14} className="text-emerald-600 mt-0.5 shrink-0" />}
                {c.status === 'fail' && <XCircle size={14} className="text-red-600 mt-0.5 shrink-0" />}
                {c.status === 'warn' && <AlertTriangle size={14} className="text-amber-600 mt-0.5 shrink-0" />}
                {c.status === 'skipped' && <div className="w-3.5 h-3.5 rounded-full border border-slate-400 mt-0.5 shrink-0" />}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-slate-500">{c.rule_id}</span>
                    <span className="text-slate-800 text-xs font-medium">{c.rule_name}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{c.explanation}</p>
                </div>
                <StatusBadge value={c.severity} />
              </div>
            ))}
          </div>

          {/* Policy packs */}
          {Array.isArray(cs.evidence?.active_policy_packs) && (
            <div className="mt-3 pt-3 border-t border-slate-200 flex flex-wrap gap-1">
              <span className="text-xs text-slate-500">Policy packs:</span>
              {(cs.evidence.active_policy_packs as string[]).map(p => (
                <span key={p} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full border border-slate-200">{p}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Cost */}
      {cm && (
        <div className="card p-5">
          <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-4">Cost Analysis</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
            {[
              { label: 'Current/mo', value: `$${cm.current_monthly_cost?.toLocaleString()}`, color: 'text-slate-900' },
              { label: 'Target/mo', value: `$${cm.target_monthly_cost?.toLocaleString()}`, color: 'text-slate-900' },
              { label: 'Monthly Savings', value: `$${cm.monthly_savings?.toLocaleString()}`, color: cm.monthly_savings > 0 ? 'text-emerald-700' : 'text-red-700' },
              { label: '3-yr Net', value: `$${cm.three_year_net?.toLocaleString()}`, color: cm.three_year_net > 0 ? 'text-emerald-700' : 'text-red-700' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-slate-100 rounded-lg p-3 border border-slate-200">
                <p className="text-xs text-slate-500">{label}</p>
                <p className={`text-xl font-bold font-mono ${color}`}>{value}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-3 text-xs">
            {[
              { label: 'Data Egress', value: cm.egress_cost },
              { label: 'Exit Penalty', value: cm.exit_penalty },
              { label: 'Engineering', value: cm.engineering_effort_cost },
              { label: 'Downtime Risk', value: cm.downtime_risk_cost },
              { label: 'Compliance Overhead', value: cm.compliance_overhead ?? 0 },
              { label: 'Total Migration Cost', value: cm.total_migration_cost },
              { label: 'Breakeven', value: null, text: cm.breakeven_months ? `${cm.breakeven_months} months` : '∞' },
            ].map(({ label, value, text }) => (
              <div key={label} className="flex justify-between bg-slate-50 rounded px-2.5 py-2 border border-slate-100">
                <span className="text-slate-600">{label}</span>
                <span className="text-slate-900 font-mono font-medium">
                  {text ?? `$${(value ?? 0).toLocaleString()}`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Approval Actions */}
      {(decision.status === 'pending' || decision.status === 'reviewed') && (
        <div className="card p-5">
          <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-4">Action Required</h3>
          <div className="flex gap-3">
            {decision.compliance_status !== 'fail' && (
              <button
                disabled={actionLoading}
                onClick={() => action(() => approveDecision(decision.id))}
                className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold transition-colors"
              >
                {actionLoading ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle size={14} />}
                Approve
              </button>
            )}
            <button
              disabled={actionLoading}
              onClick={() => action(() => rejectDecision(decision.id))}
              className="flex items-center gap-2 px-4 py-2.5 bg-red-50 hover:bg-red-100 text-red-800 border border-red-200 rounded-lg text-sm font-semibold transition-colors"
            >
              <XCircle size={14} /> Reject
            </button>
          </div>
        </div>
      )}

      {/* Provisioning */}
      {decision.status === 'approved' && (
        <div className="card p-5">
          <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-4 flex items-center gap-2">
            <Server size={13} /> Provisioning
          </h3>
          <p className="text-slate-600 text-sm mb-4">
            Decision approved. Generate Terraform IaC and execute a dry run for {decision.target_cloud?.toUpperCase()}.
          </p>
          <button
            disabled={actionLoading}
            onClick={() => action(() => startProvisioning(decision.id))}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold transition-colors"
          >
            {actionLoading ? <Loader2 size={14} className="animate-spin" /> : <Server size={14} />}
            Generate & Dry Run
          </button>
        </div>
      )}

      {/* IaC Viewer */}
      {job && (
        <div className="card p-5">
          <button
            onClick={() => setShowIac(!showIac)}
            className="flex items-center justify-between w-full text-left"
          >
            <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide flex items-center gap-2">
              <Server size={13} /> Terraform IaC — {job.target_cloud?.toUpperCase()} · <StatusBadge value={job.status} />
            </h3>
            {showIac ? <ChevronUp size={14} className="text-slate-500" /> : <ChevronDown size={14} className="text-slate-500" />}
          </button>

          {showIac && (
            <div className="mt-4 space-y-4">
              <div className="bg-slate-100 rounded-lg p-4 text-xs font-mono text-slate-800 whitespace-pre-wrap overflow-auto max-h-64 border border-slate-200">
                {job.dry_run_output}
              </div>
              <details className="group">
                <summary className="cursor-pointer text-xs text-slate-600 hover:text-slate-900">
                  Show full Terraform code
                </summary>
                <div className="mt-2 bg-slate-100 rounded-lg p-4 text-xs font-mono text-slate-800 whitespace-pre-wrap overflow-auto max-h-96 border border-slate-200">
                  {job.iac_code}
                </div>
              </details>
              <button
                disabled={actionLoading}
                onClick={() => action(() => applyProvisioning(job.id))}
                className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold transition-colors"
              >
                {actionLoading ? <Loader2 size={14} className="animate-spin" /> : <Server size={14} />}
                Apply (Provision Infrastructure)
              </button>
            </div>
          )}
        </div>
      )}

      {/* Audit Log */}
      <div className="card p-5">
        <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-4">Audit Trail</h3>
        <div className="space-y-2">
          {logs.map(l => (
            <div key={l.id} className="flex items-start gap-3 text-xs">
              <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
              <div>
                <span className="text-slate-500 font-mono">{new Date(l.timestamp).toLocaleString()}</span>
                <span className="text-slate-800 ml-2 font-medium">{l.event_type.replace(/_/g, ' ')}</span>
                <span className="text-slate-500 ml-1">by {l.actor}</span>
                <span className="text-slate-600 ml-1">· v{l.rule_version}</span>
              </div>
            </div>
          ))}
          {logs.length === 0 && <p className="text-slate-500 text-xs">No audit entries yet.</p>}
        </div>
      </div>
    </div>
  )
}
