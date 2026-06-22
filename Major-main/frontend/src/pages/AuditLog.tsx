import { useEffect, useState } from 'react'
import { ScrollText, Search, Filter } from 'lucide-react'
import { getAuditLogs, type AuditLog } from '../api'

const EVENT_COLORS: Record<string, string> = {
  broker_request_received: 'bg-blue-500',
  compliance_check_completed: 'bg-purple-500',
  cost_analysis_completed: 'bg-emerald-500',
  decision_created: 'bg-indigo-500',
  decision_approved: 'bg-emerald-500',
  decision_rejected: 'bg-red-500',
  provisioning_started: 'bg-orange-500',
  provisioning_dry_run: 'bg-yellow-500',
  provisioning_approved: 'bg-indigo-500',
  provisioning_completed: 'bg-emerald-500',
  provisioning_failed: 'bg-red-500',
  report_exported: 'bg-slate-500',
}

export default function AuditLogPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    getAuditLogs(undefined, 200).then(setLogs).finally(() => setLoading(false))
  }, [])

  const filtered = logs.filter(l =>
    l.event_type.toLowerCase().includes(query.toLowerCase()) ||
    l.actor.toLowerCase().includes(query.toLowerCase()) ||
    (l.decision_id || '').includes(query)
  )

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <ScrollText size={22} className="text-indigo-600" /> Audit Log
        </h1>
        <p className="text-slate-600 mt-1">Immutable event trail — {logs.length} entries</p>
      </div>

      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search events, actors, decision IDs…"
          className="w-full bg-white border border-slate-300 rounded-lg pl-9 pr-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500" />
        </div>
      ) : (
        <div className="card divide-y divide-slate-200">
          {filtered.length === 0 && (
            <div className="p-12 text-center text-slate-500">No audit entries found.</div>
          )}
          {filtered.map(l => (
            <div key={l.id} className="px-5 py-3.5 hover:bg-slate-50 transition-colors cursor-pointer" onClick={() => setExpanded(expanded === l.id ? null : l.id)}>
              <div className="flex items-start gap-3">
                <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${EVENT_COLORS[l.event_type] || 'bg-slate-500'}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-medium text-slate-900">
                      {l.event_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                    </span>
                    <span className="text-xs text-slate-500">by <span className="text-slate-700">{l.actor}</span></span>
                    {l.decision_id && (
                      <span className="text-xs font-mono text-indigo-800 bg-indigo-50 border border-indigo-200 px-1.5 py-0.5 rounded">
                        {l.decision_id.slice(0, 8)}…
                      </span>
                    )}
                    <span className="text-xs text-slate-700 bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded">
                      v{l.rule_version}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {new Date(l.timestamp).toLocaleString()}
                  </p>
                  {expanded === l.id && (
                    <pre className="mt-2 text-xs bg-slate-100 rounded-lg p-3 text-slate-800 overflow-auto max-h-48 border border-slate-200">
                      {JSON.stringify(l.payload, null, 2)}
                    </pre>
                  )}
                </div>
                <Filter size={10} className={`text-slate-600 mt-1 transition-transform ${expanded === l.id ? 'rotate-180' : ''}`} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
