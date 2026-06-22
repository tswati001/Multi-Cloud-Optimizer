import { useEffect, useState } from 'react'
import { Database, Plus, ArrowRight } from 'lucide-react'
import { getAssets, getCompanies, createAsset, type DataAsset, type Company } from '../api'
import CloudIcon from '../components/CloudIcon'
import StatusBadge from '../components/StatusBadge'

const DATA_CLASSES = ['PII', 'PHI', 'Financial', 'IP', 'Public']
const SENSITIVITIES = ['critical', 'high', 'medium', 'low']
const CLOUDS = ['aws', 'azure', 'gcp', 'on-prem']

/** Alternate approved cloud for broker (not shown in UI — set from current only). */
function inferredTargetCloud(current: string): string {
  if (current === 'aws') return 'azure'
  if (current === 'azure') return 'aws'
  if (current === 'gcp') return 'aws'
  return 'aws'
}

export default function Assets() {
  const [assets, setAssets] = useState<DataAsset[]>([])
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({
    id: '', company_id: '', name: '', data_class: 'PII', sensitivity: 'high',
    residency_constraints: '', volume_gb: 100, current_cloud: 'aws',
  })

  const reload = () =>
    Promise.all([getAssets(), getCompanies()]).then(([a, c]) => { setAssets(a); setCompanies(c) }).finally(() => setLoading(false))

  useEffect(() => { reload() }, [])

  const save = async () => {
    setSaving(true)
    try {
      await createAsset({
        ...form,
        target_cloud: inferredTargetCloud(form.current_cloud),
        volume_gb: Number(form.volume_gb),
        residency_constraints: form.residency_constraints ? form.residency_constraints.split(',').map(r => r.trim()) : [],
      })
      setShowForm(false)
      reload()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Database size={22} className="text-indigo-600" /> Data Assets
          </h1>
          <p className="text-slate-600 mt-1">{assets.length} data assets</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={14} /> Add Asset
        </button>
      </div>

      {showForm && (
        <div className="card p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-800">New Data Asset</h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { key: 'id', label: 'Asset ID', placeholder: 'asset-001' },
              { key: 'name', label: 'Asset Name', placeholder: 'Customer Records DB' },
            ].map(({ key, label, placeholder }) => (
              <div key={key}>
                <label className="block text-xs font-medium text-slate-600 mb-1.5">{label}</label>
                <input value={form[key as keyof typeof form]} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                  placeholder={placeholder}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" />
              </div>
            ))}
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">Company</label>
              <select value={form.company_id} onChange={e => setForm(f => ({ ...f, company_id: e.target.value }))}
                className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500">
                <option value="">Select…</option>
                {companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">Data Class</label>
              <select value={form.data_class} onChange={e => setForm(f => ({ ...f, data_class: e.target.value }))}
                className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500">
                {DATA_CLASSES.map(d => <option key={d}>{d}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">Sensitivity</label>
              <select value={form.sensitivity} onChange={e => setForm(f => ({ ...f, sensitivity: e.target.value }))}
                className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500">
                {SENSITIVITIES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">Volume (GB)</label>
              <input type="number" value={form.volume_gb} onChange={e => setForm(f => ({ ...f, volume_gb: Number(e.target.value) }))}
                className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">Residency Constraints (comma-sep)</label>
              <input value={form.residency_constraints} onChange={e => setForm(f => ({ ...f, residency_constraints: e.target.value }))}
                placeholder="US, EU"
                className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-medium text-slate-600 mb-1.5">Current Cloud</label>
              <select value={form.current_cloud} onChange={e => setForm(f => ({ ...f, current_cloud: e.target.value }))}
                className="w-full max-w-md bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500">
                {CLOUDS.map(c => <option key={c}>{c}</option>)}
              </select>
              <p className="text-xs text-slate-500 mt-1">
                Migration target is set automatically to the alternate primary provider ({inferredTargetCloud(form.current_cloud).toUpperCase()}) for evaluation.
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={save} disabled={saving || !form.id || !form.name || !form.company_id}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-lg text-sm font-medium transition-colors">
              {saving ? 'Saving…' : 'Save'}
            </button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 text-slate-600 hover:text-slate-900 text-sm transition-colors">Cancel</button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500" />
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                {['Name', 'Class', 'Sensitivity', 'Volume', 'Migration', 'Constraints'].map(h => (
                  <th key={h} className="text-left px-5 py-3 text-xs font-semibold text-slate-600 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {assets.map(a => (
                <tr key={a.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3.5">
                    <p className="font-medium text-slate-900">{a.name}</p>
                    <p className="text-xs text-slate-500 font-mono">{a.id}</p>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="text-xs bg-slate-100 text-slate-700 border border-slate-200 px-2 py-0.5 rounded-full">{a.data_class}</span>
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge value={a.sensitivity === 'critical' || a.sensitivity === 'high' ? 'fail' : a.sensitivity === 'medium' ? 'warn' : 'pass'} />
                  </td>
                  <td className="px-5 py-3.5 text-slate-700 font-mono text-xs">{a.volume_gb.toLocaleString()} GB</td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-1">
                      <CloudIcon cloud={a.current_cloud} size="sm" />
                      <ArrowRight size={10} className="text-slate-600" />
                      <CloudIcon cloud={a.target_cloud} size="sm" />
                    </div>
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex gap-1 flex-wrap">
                      {a.residency_constraints.length > 0 ? a.residency_constraints.map(r => (
                        <span key={r} className="text-xs bg-amber-50 text-amber-900 border border-amber-200 px-1.5 py-0.5 rounded-full">{r}</span>
                      )) : <span className="text-slate-600 text-xs">none</span>}
                    </div>
                  </td>
                </tr>
              ))}
              {assets.length === 0 && (
                <tr><td colSpan={6} className="px-5 py-12 text-center text-slate-500">No data assets.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
