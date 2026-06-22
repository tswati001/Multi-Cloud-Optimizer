import { useEffect, useState } from 'react'
import { Building2, Plus, Globe } from 'lucide-react'
import { getCompanies, createCompany, type Company } from '../api'

const INDUSTRIES = ['Healthcare', 'Financial Services', 'SaaS', 'Retail', 'Manufacturing', 'Government', 'Education', 'Media', 'Other']
const COUNTRIES = ['US', 'DE', 'FR', 'GB', 'IN', 'SG', 'AU', 'JP', 'CA', 'NL', 'IE']

export default function Companies() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ id: '', name: '', industry: 'Healthcare', headquarters_country: 'US', operating_regions: 'US', ownership_structure: 'private' })
  const [saving, setSaving] = useState(false)

  const reload = () => getCompanies().then(setCompanies).finally(() => setLoading(false))
  useEffect(() => { reload() }, [])

  const save = async () => {
    setSaving(true)
    try {
      await createCompany({
        ...form,
        operating_regions: form.operating_regions.split(',').map(r => r.trim()),
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
            <Building2 size={22} className="text-indigo-600" /> Companies
          </h1>
          <p className="text-slate-600 mt-1">{companies.length} companies registered</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={14} /> Add Company
        </button>
      </div>

      {showForm && (
        <div className="card p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-800">New Company</h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { key: 'id', label: 'ID', placeholder: 'comp-001' },
              { key: 'name', label: 'Company Name', placeholder: 'Acme Corp' },
            ].map(({ key, label, placeholder }) => (
              <div key={key}>
                <label className="block text-xs font-medium text-slate-600 mb-1.5">{label}</label>
                <input
                  value={form[key as keyof typeof form]}
                  onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                  placeholder={placeholder}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            ))}
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">Industry</label>
              <select value={form.industry} onChange={e => setForm(f => ({ ...f, industry: e.target.value }))}
                className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500">
                {INDUSTRIES.map(i => <option key={i}>{i}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">HQ Country</label>
              <select value={form.headquarters_country} onChange={e => setForm(f => ({ ...f, headquarters_country: e.target.value }))}
                className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500">
                {COUNTRIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1.5">Operating Regions (comma-separated)</label>
              <input value={form.operating_regions} onChange={e => setForm(f => ({ ...f, operating_regions: e.target.value }))}
                placeholder="US, EU, IN"
                className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500" />
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={save} disabled={saving || !form.id || !form.name}
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {companies.map(c => (
            <div key={c.id} className="card p-5">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center text-lg font-bold text-indigo-800 shrink-0">
                  {c.name[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-slate-900 truncate">{c.name}</p>
                  <p className="text-xs text-slate-500">{c.industry}</p>
                  <div className="flex items-center gap-1 mt-1.5 flex-wrap">
                    <Globe size={10} className="text-slate-500" />
                    {(c.operating_regions || []).map(r => (
                      <span key={r} className="text-xs bg-slate-100 text-slate-700 border border-slate-200 px-1.5 py-0.5 rounded">{r}</span>
                    ))}
                  </div>
                  <p className="text-xs text-slate-600 mt-1 font-mono">{c.id}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
