import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import {
  Shield, Server, DollarSign, Zap,
  ArrowRight, CheckCircle, XCircle, AlertTriangle
} from 'lucide-react'
import { getStats, getDecisions, type DashboardStats, type Decision } from '../api'

const COLORS = { pass: '#10b981', fail: '#ef4444', warn: '#f59e0b', move: '#6366f1', stay: '#64748b', investigate: '#eab308' }

function StatCard({ label, value, sub, icon: Icon, color }: {
  label: string; value: string | number; sub?: string;
  icon: React.ElementType; color: string
}) {
  return (
    <div className="card p-5 flex items-start gap-4">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${color}`}>
        <Icon size={18} />
      </div>
      <div>
        <p className="text-2xl font-bold text-slate-900">{value}</p>
        <p className="text-sm text-slate-600 mt-0.5">{label}</p>
        {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getStats(), getDecisions()])
      .then(([s, d]) => { setStats(s); setDecisions(d) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
    </div>
  )

  const recData = stats ? [
    { name: 'Move', value: stats.recommendations.move, color: COLORS.move },
    { name: 'Stay', value: stats.recommendations.stay, color: COLORS.stay },
    { name: 'Investigate', value: stats.recommendations.investigate, color: COLORS.investigate },
  ] : []

  const compData = stats ? [
    { name: 'Pass', value: stats.compliance.pass },
    { name: 'Fail', value: stats.compliance.fail },
    { name: 'Warn', value: stats.compliance.warn },
  ] : []

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-600 mt-1">Cloud Agility Broker — automated migration decision engine</p>
        </div>
        <Link
          to="/evaluate"
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Zap size={14} /> New Evaluation
        </Link>
      </div>

      {/* KPI Cards */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Total Decisions"
            value={stats.total_decisions}
            sub={`${stats.total_companies} companies · ${stats.total_assets} assets`}
            icon={CheckCircle}
            color="bg-indigo-50 text-indigo-700"
          />
          <StatCard
            label="No Hard Failures"
            value={`${stats.no_hard_failures_rate ?? stats.compliance_pass_rate}%`}
            sub={`${stats.compliance.fail} blocked · ${stats.compliance.warn} with warnings`}
            icon={Shield}
            color="bg-emerald-50 text-emerald-700"
          />
          <StatCard
            label="Provisioned Migrations"
            value={stats.provisioned_count}
            sub={`${stats.total_provisioning_jobs} total jobs`}
            icon={Server}
            color="bg-blue-50 text-blue-700"
          />
          <StatCard
            label="Projected 3-yr Savings"
            value={`$${(stats.total_projected_3yr_savings / 1_000_000).toFixed(2)}M`}
            sub="on approved move decisions"
            icon={DollarSign}
            color="bg-emerald-50 text-emerald-700"
          />
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recommendation breakdown */}
        <div className="card p-6">
          <h2 className="text-sm font-semibold text-slate-700 mb-4 uppercase tracking-wide">
            Recommendations
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={recData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                {recData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Legend />
              <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, color: '#0f172a' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Compliance breakdown */}
        <div className="card p-6">
          <h2 className="text-sm font-semibold text-slate-700 mb-4 uppercase tracking-wide">
            Compliance Results
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={compData} barSize={36}>
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, color: '#0f172a' }} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {compData.map((_, i) => (
                  <Cell key={i} fill={[COLORS.pass, COLORS.fail, COLORS.warn][i]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Decisions */}
      <div className="card">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">Recent Decisions</h2>
          <Link to="/decisions" className="text-indigo-600 text-sm hover:text-indigo-800 flex items-center gap-1">
            View all <ArrowRight size={12} />
          </Link>
        </div>
        <div className="divide-y divide-slate-200">
          {decisions.slice(0, 6).map(d => (
            <Link
              key={d.id}
              to={`/decisions/${d.id}`}
              className="flex items-center justify-between px-6 py-4 hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${
                  d.recommendation === 'move' ? 'bg-indigo-500' :
                  d.recommendation === 'stay' ? 'bg-slate-400' : 'bg-yellow-500'
                }`} />
                <div>
                  <p className="text-sm font-medium text-slate-900">{d.id.slice(0, 8)}…</p>
                  <p className="text-xs text-slate-500">
                    {d.source_cloud?.toUpperCase()} → {d.target_cloud?.toUpperCase()} ·{' '}
                    {new Date(d.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
                  d.compliance_status === 'pass' ? 'badge-pass' :
                  d.compliance_status === 'fail' ? 'badge-fail' : 'badge-warn'
                }`}>
                  {d.compliance_status === 'pass' ? <CheckCircle size={10} className="inline mr-1" /> :
                   d.compliance_status === 'fail' ? <XCircle size={10} className="inline mr-1" /> :
                   <AlertTriangle size={10} className="inline mr-1" />}
                  {d.compliance_status?.toUpperCase()}
                </span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
                  d.recommendation === 'move' ? 'badge-move' :
                  d.recommendation === 'stay' ? 'badge-stay' : 'badge-investigate'
                }`}>
                  {d.recommendation?.toUpperCase()}
                </span>
                {d.cost_model?.monthly_savings != null && (
                  <span className="text-xs text-emerald-700 font-mono">
                    ${d.cost_model.monthly_savings.toLocaleString()}/mo
                  </span>
                )}
              </div>
            </Link>
          ))}
          {decisions.length === 0 && (
            <div className="px-6 py-12 text-center text-slate-500">
              <Zap size={32} className="mx-auto mb-3 opacity-30" />
              <p>No decisions yet. Run your first evaluation.</p>
              <Link to="/evaluate" className="mt-3 inline-block text-indigo-600 hover:text-indigo-800 text-sm">
                Start Evaluation →
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
