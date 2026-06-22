import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, ChevronRight, CheckCircle, XCircle, AlertTriangle, DollarSign, ArrowRight, Loader2 } from 'lucide-react'
import { getCompanies, getAssets, evaluate, type Company, type DataAsset, type BrokerResult } from '../api'
import StatusBadge from '../components/StatusBadge'
import CloudIcon from '../components/CloudIcon'

const STEPS = ['Company & Asset', 'Parameters', 'Run Evaluation', 'Results']

interface FormState {
  company_id: string
  data_asset_id: string
  time_horizon_months: number
  min_savings_threshold_pct: number
  engineering_hourly_rate: number
  engineering_hours_estimate: number
  downtime_hours_estimate: number
  revenue_per_hour: number
}

export default function Evaluate() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [companies, setCompanies] = useState<Company[]>([])
  const [assets, setAssets] = useState<DataAsset[]>([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<BrokerResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [form, setForm] = useState<FormState>({
    company_id: '',
    data_asset_id: '',
    time_horizon_months: 36,
    min_savings_threshold_pct: 10,
    engineering_hourly_rate: 150,
    engineering_hours_estimate: 200,
    downtime_hours_estimate: 4,
    revenue_per_hour: 50000,
  })

  useEffect(() => { getCompanies().then(setCompanies) }, [])

  useEffect(() => {
    if (form.company_id) getAssets(form.company_id).then(setAssets)
  }, [form.company_id])

  const set = (key: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm(f => ({ ...f, [key]: key === 'company_id' || key === 'data_asset_id' ? e.target.value : Number(e.target.value) }))

  const runEvaluation = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await evaluate(form)
      setResult(res)
      setStep(3)
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string }
      setError(e?.response?.data?.detail || e?.message || 'Evaluation failed')
    } finally {
      setLoading(false)
    }
  }

  const selectedAsset = assets.find(a => a.id === form.data_asset_id)
  const selectedCompany = companies.find(c => c.id === form.company_id)

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Zap size={22} className="text-indigo-600" /> New Evaluation
        </h1>
        <p className="text-slate-600 mt-1">Run the full compliance + cost + provisioning broker workflow</p>
      </div>

      {/* Stepper */}
      <div className="flex items-center gap-2">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              i === step ? 'bg-indigo-600 text-white' :
              i < step ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-slate-200 text-slate-600'
            }`}>
              {i < step ? <CheckCircle size={12} /> : <span className="w-4 h-4 flex items-center justify-center rounded-full bg-current/20 text-[10px]">{i+1}</span>}
              {s}
            </div>
            {i < STEPS.length - 1 && <ChevronRight size={14} className="text-slate-600" />}
          </div>
        ))}
      </div>

      {/* Step 0: Company & Asset */}
      {step === 0 && (
        <div className="card p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Company</label>
            <select
              className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              value={form.company_id}
              onChange={set('company_id')}
            >
              <option value="">Select company…</option>
              {companies.map(c => (
                <option key={c.id} value={c.id}>{c.name} ({c.headquarters_country})</option>
              ))}
            </select>
          </div>

          {form.company_id && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Data Asset</label>
              {assets.length === 0 ? (
                <p className="text-slate-500 text-sm">No assets found for this company.</p>
              ) : (
                <div className="space-y-2">
                  {assets.map(a => (
                    <label
                      key={a.id}
                      className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                        form.data_asset_id === a.id
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-slate-300 hover:border-slate-400'
                      }`}
                    >
                      <input
                        type="radio"
                        name="asset"
                        value={a.id}
                        checked={form.data_asset_id === a.id}
                        onChange={set('data_asset_id')}
                        className="accent-indigo-500"
                      />
                      <div className="flex items-center gap-2 flex-1">
                        <CloudIcon cloud={a.current_cloud} size="sm" />
                        <div>
                          <p className="text-sm font-medium text-slate-900">{a.name}</p>
                          <p className="text-xs text-slate-600">
                            {a.data_class} · {a.sensitivity} · {a.volume_gb.toLocaleString()} GB ·{' '}
                            {a.current_cloud.toUpperCase()} → {a.target_cloud.toUpperCase()}
                          </p>
                        </div>
                      </div>
                      {a.residency_constraints.length > 0 && (
                        <span className="text-xs text-amber-900 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                          {a.residency_constraints.join(', ')}
                        </span>
                      )}
                    </label>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="flex justify-end">
            <button
              disabled={!form.company_id || !form.data_asset_id}
              onClick={() => setStep(1)}
              className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
            >
              Next <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}

      {/* Step 1: Parameters */}
      {step === 1 && (
        <div className="card p-6 space-y-5">
          <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">Economic Parameters</h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { key: 'time_horizon_months', label: 'Time Horizon (months)', min: 12, max: 60, step: 6 },
              { key: 'min_savings_threshold_pct', label: 'Min Savings Threshold (%)', min: 1, max: 30, step: 1 },
              { key: 'engineering_hourly_rate', label: 'Engineering Rate ($/hr)', min: 50, max: 500, step: 25 },
              { key: 'engineering_hours_estimate', label: 'Engineering Hours', min: 40, max: 2000, step: 40 },
              { key: 'downtime_hours_estimate', label: 'Downtime Estimate (hrs)', min: 0, max: 48, step: 1 },
              { key: 'revenue_per_hour', label: 'Revenue at Risk ($/hr)', min: 1000, max: 1000000, step: 5000 },
            ].map(({ key, label, min, max, step: s }) => (
              <div key={key}>
                <label className="block text-xs font-medium text-slate-600 mb-1.5">{label}</label>
                <input
                  type="number"
                  min={min} max={max} step={s}
                  value={form[key as keyof FormState] as number}
                  onChange={set(key as keyof FormState)}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            ))}
          </div>

          <div className="flex justify-between">
            <button onClick={() => setStep(0)} className="px-4 py-2 text-slate-600 hover:text-slate-900 text-sm transition-colors">
              ← Back
            </button>
            <button onClick={() => setStep(2)} className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium flex items-center gap-2 transition-colors">
              Next <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Confirm & Run */}
      {step === 2 && (
        <div className="card p-6 space-y-5">
          <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">Confirm & Run</h3>

          {selectedCompany && selectedAsset && (
            <div className="bg-slate-50 rounded-xl p-4 space-y-3 border border-slate-200">
              <div className="flex items-center gap-3">
                <CloudIcon cloud={selectedAsset.current_cloud} size="md" />
                <ArrowRight size={16} className="text-slate-500" />
                <CloudIcon cloud={selectedAsset.target_cloud} size="md" />
                <div className="ml-2">
                  <p className="font-semibold text-slate-900">{selectedAsset.name}</p>
                  <p className="text-xs text-slate-600">{selectedCompany.name} · {selectedAsset.data_class} · {selectedAsset.volume_gb.toLocaleString()} GB</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="bg-white rounded-lg p-2 border border-slate-200">
                  <p className="text-slate-500">Horizon</p>
                  <p className="text-slate-900 font-medium">{form.time_horizon_months}mo</p>
                </div>
                <div className="bg-white rounded-lg p-2 border border-slate-200">
                  <p className="text-slate-500">Min Savings</p>
                  <p className="text-slate-900 font-medium">{form.min_savings_threshold_pct}%</p>
                </div>
                <div className="bg-white rounded-lg p-2 border border-slate-200">
                  <p className="text-slate-500">Eng Rate</p>
                  <p className="text-slate-900 font-medium">${form.engineering_hourly_rate}/hr</p>
                </div>
              </div>
            </div>
          )}

          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
            <p className="text-xs text-slate-600 font-semibold mb-2 uppercase tracking-wide">What will run:</p>
            <div className="space-y-1.5 text-sm">
              {['1. Compliance: GDPR 2026-v2 · HIPAA · CCPA/CPRA · India DPDP Act 2025 · SOC 2 · PCI DSS v4 · Internal',
                '2. Cost: tiered 2026 egress ($0.09/GB AWS, $0.087/GB Azure) · exit fees · labour · downtime · compliance overhead',
                '3. 3-year TCO: base · optimistic · pessimistic sensitivity scenarios',
                '4. Recommendation with full rationale and policy evidence',
                '5. Immutable audit trail entry with rule version stamps'
              ].map(t => (
                <p key={t} className="text-slate-700 flex gap-2"><CheckCircle size={14} className="text-emerald-600 mt-0.5 shrink-0" />{t}</p>
              ))}
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-800 text-sm flex items-center gap-2">
              <XCircle size={16} /> {error}
            </div>
          )}

          <div className="flex justify-between">
            <button onClick={() => setStep(1)} className="px-4 py-2 text-slate-600 hover:text-slate-900 text-sm transition-colors">
              ← Back
            </button>
            <button
              onClick={runEvaluation}
              disabled={loading}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-sm font-semibold flex items-center gap-2 transition-colors"
            >
              {loading ? <><Loader2 size={14} className="animate-spin" /> Running…</> : <><Zap size={14} /> Run Evaluation</>}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Results */}
      {step === 3 && result && (
        <div className="space-y-5">
          {/* Hero result */}
          <div className={`rounded-xl border p-6 ${
            result.recommendation === 'move' ? 'bg-indigo-50 border-indigo-200' :
            result.recommendation === 'stay' ? 'bg-slate-100 border-slate-300' :
            'bg-amber-50 border-amber-200'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-600 uppercase tracking-widest mb-1">Recommendation</p>
                <p className={`text-4xl font-black uppercase ${
                  result.recommendation === 'move' ? 'text-indigo-700' :
                  result.recommendation === 'stay' ? 'text-slate-700' : 'text-amber-800'
                }`}>
                  {result.recommendation === 'move' ? '🚀 MOVE' :
                   result.recommendation === 'stay' ? '⚓ STAY' : '🔍 INVESTIGATE'}
                </p>
                <p className="text-slate-600 text-sm mt-2 max-w-lg">{result.rationale}</p>
              </div>
              <div className="text-right">
                <StatusBadge value={result.compliance.status} />
                <p className="text-xs text-slate-500 mt-1">Compliance</p>
              </div>
            </div>
          </div>

          {/* Compliance */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide mb-4 flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${result.compliance.status === 'pass' ? 'bg-emerald-500' : result.compliance.status === 'fail' ? 'bg-red-500' : 'bg-amber-500'}`} />
              Compliance — {result.compliance.checks.length} rules evaluated
            </h3>
            <div className="space-y-2">
              {result.compliance.checks.filter(c => c.status !== 'skipped').map(c => (
                <div key={c.rule_id} className="flex items-start gap-3 text-sm">
                  {c.status === 'pass' && <CheckCircle size={14} className="text-emerald-600 mt-0.5 shrink-0" />}
                  {c.status === 'fail' && <XCircle size={14} className="text-red-600 mt-0.5 shrink-0" />}
                  {c.status === 'warn' && <AlertTriangle size={14} className="text-amber-600 mt-0.5 shrink-0" />}
                  <div className="flex-1">
                    <span className="font-mono text-xs text-slate-500 mr-2">{c.rule_id}</span>
                    <span className="text-slate-800">{c.rule_name}</span>
                    <p className="text-xs text-slate-500 mt-0.5">{c.explanation}</p>
                  </div>
                  <span className={`text-xs px-1.5 py-0.5 rounded border shrink-0 ${
                    c.severity === 'hard' ? 'badge-fail' : 'badge-warn'
                  }`}>{c.severity}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Cost */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide mb-4 flex items-center gap-2">
              <DollarSign size={14} className="text-emerald-600" />
              Cost Analysis
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              {[
                { label: 'Current/mo', value: `$${result.cost.current_monthly_cost?.toLocaleString()}` },
                { label: 'Target/mo', value: `$${result.cost.target_monthly_cost?.toLocaleString()}` },
                { label: 'Monthly Savings', value: `$${result.cost.monthly_savings?.toLocaleString()}`, green: true },
                { label: '3-yr Net', value: `$${result.cost.three_year_net?.toLocaleString()}`, green: (result.cost.three_year_net ?? 0) > 0 },
              ].map(({ label, value, green }) => (
                <div key={label} className="bg-slate-100 rounded-lg p-3 border border-slate-200">
                  <p className="text-xs text-slate-600">{label}</p>
                  <p className={`text-lg font-bold ${green ? 'text-emerald-700' : 'text-slate-900'}`}>{value}</p>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs text-slate-600">
              <p>Egress (tiered 2026): <span className="text-slate-900 font-medium">${result.cost.egress_cost?.toLocaleString()}</span></p>
              <p>Exit Penalty: <span className="text-slate-900 font-medium">${result.cost.exit_penalty?.toLocaleString()}</span></p>
              <p>Engineering Labour: <span className="text-slate-900 font-medium">${result.cost.engineering_effort_cost?.toLocaleString()}</span></p>
              <p>Downtime Risk: <span className="text-slate-900 font-medium">${result.cost.downtime_risk_cost?.toLocaleString()}</span></p>
              <p>Compliance Overhead: <span className="text-slate-900 font-medium">${((result.cost as unknown as Record<string, number>).compliance_overhead ?? 0).toLocaleString()}</span></p>
              <p>Total Migration: <span className="text-amber-700 font-semibold">${result.cost.total_migration_cost?.toLocaleString()}</span></p>
              <p>Breakeven: <span className="text-slate-900 font-medium">{result.cost.breakeven_months ?? '∞'} months</span></p>
              <p>Savings %: <span className="text-emerald-700 font-semibold">{result.cost.savings_pct}%</span></p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={() => navigate(`/decisions/${result.decision_id}`)}
              className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold flex items-center justify-center gap-2 transition-colors"
            >
              View Full Decision <ArrowRight size={14} />
            </button>
            <button
              onClick={() => { setResult(null); setStep(0); setForm(f => ({ ...f, data_asset_id: '' })) }}
              className="px-4 py-3 bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-200 rounded-lg text-sm font-medium transition-colors"
            >
              New Evaluation
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
