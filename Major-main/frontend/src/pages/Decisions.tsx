import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ClipboardList, Search, ArrowRight } from 'lucide-react'
import { getDecisions, type Decision } from '../api'
import StatusBadge from '../components/StatusBadge'
import CloudIcon from '../components/CloudIcon'

export default function Decisions() {
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')

  useEffect(() => {
    getDecisions().then(setDecisions).finally(() => setLoading(false))
  }, [])

  const filtered = decisions.filter(d =>
    d.id.toLowerCase().includes(query.toLowerCase()) ||
    d.recommendation?.toLowerCase().includes(query.toLowerCase()) ||
    d.source_cloud?.toLowerCase().includes(query.toLowerCase()) ||
    d.target_cloud?.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <ClipboardList size={22} className="text-indigo-600" /> Decisions
          </h1>
          <p className="text-slate-600 mt-1">{decisions.length} decisions · all migration evaluations</p>
        </div>
        <Link
          to="/evaluate"
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          + New Evaluation
        </Link>
      </div>

      {/* Search */}
      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search by ID, recommendation, cloud…"
          className="w-full bg-white border border-slate-300 rounded-lg pl-9 pr-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-600 uppercase tracking-wide">Decision ID</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase tracking-wide">Migration</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase tracking-wide">Compliance</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase tracking-wide">Cost</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase tracking-wide">Recommendation</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase tracking-wide">Status</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-600 uppercase tracking-wide">Date</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {loading ? (
              <tr>
                <td colSpan={8} className="px-5 py-12 text-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500 mx-auto" />
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-5 py-12 text-center text-slate-500">
                  No decisions found.
                </td>
              </tr>
            ) : (
              filtered.map(d => (
                <tr key={d.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-5 py-3.5 font-mono text-xs text-slate-700">{d.id.slice(0, 8)}…</td>
                  <td className="px-4 py-3.5">
                    <div className="flex items-center gap-1.5">
                      <CloudIcon cloud={d.source_cloud} size="sm" />
                      <ArrowRight size={10} className="text-slate-600" />
                      <CloudIcon cloud={d.target_cloud} size="sm" />
                    </div>
                  </td>
                  <td className="px-4 py-3.5"><StatusBadge value={d.compliance_status} /></td>
                  <td className="px-4 py-3.5">
                    <div>
                      <StatusBadge value={d.cost_status} />
                      {d.cost_model?.monthly_savings != null && (
                        <p className="text-xs text-emerald-700 font-mono mt-1">
                          ${d.cost_model.monthly_savings.toLocaleString()}/mo
                        </p>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3.5"><StatusBadge value={d.recommendation} /></td>
                  <td className="px-4 py-3.5"><StatusBadge value={d.status} /></td>
                  <td className="px-4 py-3.5 text-xs text-slate-500">
                    {new Date(d.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3.5">
                    <Link
                      to={`/decisions/${d.id}`}
                      className="text-indigo-600 hover:text-indigo-800 text-xs flex items-center gap-1"
                    >
                      View <ArrowRight size={10} />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
