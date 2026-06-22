import { CheckCircle, XCircle, AlertTriangle, ArrowRight, Minus, Search, Rocket } from 'lucide-react'

interface Props {
  value: string
  type?: 'recommendation' | 'compliance' | 'cost' | 'status'
}

const configs: Record<string, { cls: string; icon: React.ReactNode; label: string }> = {
  // compliance
  pass:        { cls: 'badge-pass', icon: <CheckCircle size={12} />, label: 'PASS' },
  fail:        { cls: 'badge-fail', icon: <XCircle size={12} />, label: 'FAIL' },
  warn:        { cls: 'badge-warn', icon: <AlertTriangle size={12} />, label: 'WARN' },
  skipped:     { cls: 'badge-stay', icon: <Minus size={12} />, label: 'SKIP' },
  // recommendation
  move:        { cls: 'badge-move', icon: <ArrowRight size={12} />, label: 'MOVE' },
  stay:        { cls: 'badge-stay', icon: <Minus size={12} />, label: 'STAY' },
  investigate: { cls: 'badge-investigate', icon: <Search size={12} />, label: 'INVESTIGATE' },
  // cost
  justified:     { cls: 'badge-pass', icon: <CheckCircle size={12} />, label: 'JUSTIFIED' },
  not_justified: { cls: 'badge-fail', icon: <XCircle size={12} />, label: 'NOT JUSTIFIED' },
  marginal:      { cls: 'badge-warn', icon: <AlertTriangle size={12} />, label: 'MARGINAL' },
  // status
  pending:      { cls: 'badge-warn', icon: <AlertTriangle size={12} />, label: 'PENDING' },
  approved:     { cls: 'badge-pass', icon: <CheckCircle size={12} />, label: 'APPROVED' },
  rejected:     { cls: 'badge-fail', icon: <XCircle size={12} />, label: 'REJECTED' },
  provisioning: { cls: 'badge-move', icon: <Rocket size={12} />, label: 'PROVISIONING' },
  provisioned:  { cls: 'badge-pass', icon: <Rocket size={12} />, label: 'PROVISIONED' },
  reviewed:     { cls: 'badge-stay', icon: <Minus size={12} />, label: 'REVIEWED' },
  dry_run:      { cls: 'badge-warn', icon: <AlertTriangle size={12} />, label: 'DRY RUN' },
  failed:       { cls: 'badge-fail', icon: <XCircle size={12} />, label: 'FAILED' },
  hard:         { cls: 'badge-fail', icon: <XCircle size={12} />, label: 'HARD' },
}

export default function StatusBadge({ value }: Props) {
  const cfg = configs[value?.toLowerCase()] ?? {
    cls: 'badge-stay', icon: <Minus size={12} />, label: (value || '—').toUpperCase(),
  }
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${cfg.cls}`}>
      {cfg.icon} {cfg.label}
    </span>
  )
}
