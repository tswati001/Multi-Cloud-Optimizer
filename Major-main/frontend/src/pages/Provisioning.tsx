import { useEffect, useState } from 'react'
import { Server } from 'lucide-react'
import { getDecisions, type Decision } from '../api'
import { Link } from 'react-router-dom'
import StatusBadge from '../components/StatusBadge'
import CloudIcon from '../components/CloudIcon'

export default function Provisioning() {
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDecisions().then(d => setDecisions(d)).finally(() => setLoading(false))
  }, [])

  const actionable = decisions.filter(d =>
    ['approved', 'provisioning', 'provisioned'].includes(d.status)
  )

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Server size={22} className="text-indigo-600" /> Provisioning
        </h1>
        <p className="text-slate-600 mt-1">Infrastructure provisioning jobs and Terraform IaC status</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500" />
        </div>
      ) : actionable.length === 0 ? (
        <div className="card p-12 text-center">
          <Server size={40} className="mx-auto mb-4 text-slate-600" />
          <p className="text-slate-600">No provisioning jobs yet.</p>
          <p className="text-slate-500 text-sm mt-1">Approve a migration decision to start provisioning.</p>
          <Link to="/decisions" className="mt-4 inline-block text-indigo-600 hover:text-indigo-800 text-sm">
            View Decisions →
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {actionable.map(d => (
            <div key={d.id} className="card p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <CloudIcon cloud={d.source_cloud} size="md" />
                  <span className="text-slate-600">→</span>
                  <CloudIcon cloud={d.target_cloud} size="md" />
                  <div>
                    <p className="font-mono text-xs text-slate-600">{d.id.slice(0, 8)}…</p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {d.source_cloud?.toUpperCase()} → {d.target_cloud?.toUpperCase()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge value={d.status} />
                  <Link
                    to={`/decisions/${d.id}`}
                    className="text-indigo-700 hover:text-indigo-900 text-xs px-3 py-1.5 bg-indigo-50 border border-indigo-200 rounded-lg"
                  >
                    Manage →
                  </Link>
                </div>
              </div>

              {d.status === 'provisioned' && (
                <div className="mt-3 bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-emerald-800 text-xs font-semibold">
                  ✅ Infrastructure provisioned — Terraform applied successfully
                </div>
              )}
              {d.status === 'provisioning' && (
                <div className="mt-3 bg-indigo-50 border border-indigo-200 rounded-lg p-3 text-indigo-800 text-xs">
                  IaC generated. Dry run complete. Awaiting apply confirmation.
                </div>
              )}
              {d.status === 'approved' && (
                <div className="mt-3 bg-slate-50 border border-slate-200 rounded-lg p-3 text-slate-600 text-xs">
                  Decision approved. Click Manage to generate Terraform and run dry run.
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
