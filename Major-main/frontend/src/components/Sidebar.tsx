import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Zap, ClipboardList, Server, ScrollText,
  Shield, Building2, Database
} from 'lucide-react'

const links = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/evaluate', icon: Zap, label: 'New Evaluation' },
  { to: '/decisions', icon: ClipboardList, label: 'Decisions' },
  { to: '/provisioning', icon: Server, label: 'Provisioning' },
  { to: '/audit', icon: ScrollText, label: 'Audit Log' },
  { to: '/policies', icon: Shield, label: 'Policy Packs' },
  { to: '/companies', icon: Building2, label: 'Companies' },
  { to: '/assets', icon: Database, label: 'Data Assets' },
]

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 bg-white border-r border-slate-200 flex flex-col min-h-screen shadow-sm">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <Zap size={16} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-900 leading-tight">Cloud Agility</p>
            <p className="text-xs text-indigo-600 leading-tight font-medium">Broker</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-transparent'
              }`
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-slate-200">
        <div className="text-xs text-slate-500">
          <p className="font-semibold text-slate-700">Cloud Agility Broker</p>
          <p>v1.0.0 · MVP</p>
          <p className="mt-1">AWS · Azure · 6 Policy Packs</p>
        </div>
      </div>
    </aside>
  )
}
