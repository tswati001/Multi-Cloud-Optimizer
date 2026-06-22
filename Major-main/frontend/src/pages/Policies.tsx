import { useEffect, useState } from 'react'
import { Shield, ChevronDown, ChevronUp, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { getPolicyPacks } from '../api'

interface Rule {
  id: string
  name: string
  description: string
  severity: string
  applies_to_data_classes: string[]
  condition: string
}

interface Pack {
  id: string
  name: string
  jurisdiction: string
  rule_count: number
  rules: Rule[]
}

const JURISDICTION_COLORS: Record<string, string> = {
  EU: 'bg-blue-50 text-blue-800 border-blue-200',
  US: 'bg-red-50 text-red-800 border-red-200',
  'US-CA': 'bg-red-50 text-red-800 border-red-200',
  IN: 'bg-orange-50 text-orange-900 border-orange-200',
  global: 'bg-purple-50 text-purple-900 border-purple-200',
  internal: 'bg-slate-100 text-slate-800 border-slate-200',
}

export default function Policies() {
  const [packs, setPacks] = useState<Pack[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    getPolicyPacks().then(setPacks).finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Shield size={22} className="text-indigo-600" /> Policy Packs
        </h1>
        <p className="text-slate-600 mt-1">Active compliance rule sets used in evaluations</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500" />
        </div>
      ) : (
        <div className="space-y-4">
          {packs.map(pack => (
            <div key={pack.id} className="card overflow-hidden">
              <button
                onClick={() => setExpanded(expanded === pack.id ? null : pack.id)}
                className="w-full flex items-center justify-between px-6 py-4 hover:bg-slate-50 transition-colors text-left"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center">
                    <Shield size={16} className="text-indigo-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-slate-900">{pack.id}</h3>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${JURISDICTION_COLORS[pack.jurisdiction] || JURISDICTION_COLORS.global}`}>
                        {pack.jurisdiction}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {pack.rule_count} rules · version {pack.name}
                    </p>
                  </div>
                </div>
                {expanded === pack.id ? <ChevronUp size={16} className="text-slate-500" /> : <ChevronDown size={16} className="text-slate-500" />}
              </button>

              {expanded === pack.id && (
                <div className="border-t border-slate-200 divide-y divide-slate-200">
                  {pack.rules.map(rule => (
                    <div key={rule.id} className="px-6 py-3.5 hover:bg-slate-50">
                      <div className="flex items-start gap-3">
                        {rule.severity === 'hard' ? (
                          <XCircle size={14} className="text-red-600 mt-0.5 shrink-0" />
                        ) : (
                          <AlertTriangle size={14} className="text-amber-600 mt-0.5 shrink-0" />
                        )}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-mono text-xs text-slate-500">{rule.id}</span>
                            <span className="text-sm font-medium text-slate-900">{rule.name}</span>
                            <span className={`text-xs px-1.5 py-0.5 rounded-full border font-semibold ${
                              rule.severity === 'hard' ? 'badge-fail' : 'badge-warn'
                            }`}>
                              {rule.severity}
                            </span>
                          </div>
                          <p className="text-xs text-slate-600 mt-1">{rule.description}</p>
                          <div className="flex gap-1 mt-1.5 flex-wrap">
                            {rule.applies_to_data_classes.map(dc => (
                              <span key={dc} className="text-xs bg-slate-100 text-slate-700 border border-slate-200 px-1.5 py-0.5 rounded">
                                {dc}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="card p-5 border-indigo-200 bg-indigo-50/80">
        <h3 className="text-sm font-semibold text-indigo-800 mb-2 flex items-center gap-2">
          <CheckCircle size={14} /> 2026 Regulatory Data Sources
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-700">
          {[
            'GDPR 2026-v2: UK adequacy renewed Dec 2025; Brazil draft (EDPB Nov 2025); US via EU-US DPF',
            'HIPAA 2026-v1: US-presence trigger; AWS + Azure BAA verified at no cost',
            'CCPA/CPRA 2026-v1: Updated service-provider contract obligations (CPRA 2023)',
            'India DPDP Act 2023 + Rules 2025 (notified Nov 13, 2025): no mandatory localisation',
            'PCI DSS v4.0 (Apr 2024): CDE isolation + QSA review ($15K-$60K budget)',
            'SOC 2 Type II: Multi-AZ; CMK auto-applied in Terraform (SOC2-02 always-pass)',
            'Egress: AWS tiered $0.09→$0.05/GB; Azure $0.087→$0.05/GB (cloudforecast.io Apr 2026)',
            'Storage: S3 Standard $0.023/GB-mo; Azure Blob LRS $0.0184/GB-mo (prodsens.live Apr 2026)',
            'Migration cost: lift-and-shift $10K-40K (160-320 hrs) — ztabs.co 2026',
          ].map(p => <p key={p} className="flex items-center gap-1.5"><CheckCircle size={10} className="text-emerald-600 shrink-0" />{p}</p>)}
        </div>
      </div>
    </div>
  )
}
