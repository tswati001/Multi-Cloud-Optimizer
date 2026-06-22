interface Props {
  cloud: string
  size?: 'sm' | 'md' | 'lg'
}

const sizes = { sm: 'w-6 h-6 text-xs', md: 'w-8 h-8 text-sm', lg: 'w-12 h-12 text-base' }

export default function CloudIcon({ cloud, size = 'md' }: Props) {
  const s = sizes[size]
  if (cloud?.toLowerCase() === 'aws') {
    return (
      <span className={`${s} rounded-lg bg-orange-50 border border-orange-200 flex items-center justify-center font-bold text-orange-700`}>
        AWS
      </span>
    )
  }
  if (cloud?.toLowerCase() === 'azure') {
    return (
      <span className={`${s} rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center font-bold text-blue-700`}>
        AZ
      </span>
    )
  }
  if (cloud?.toLowerCase() === 'gcp') {
    return (
      <span className={`${s} rounded-lg bg-green-50 border border-green-200 flex items-center justify-center font-bold text-green-700`}>
        GCP
      </span>
    )
  }
  return (
    <span className={`${s} rounded-lg bg-slate-100 border border-slate-300 flex items-center justify-center font-bold text-slate-600`}>
      {(cloud || '?').toUpperCase().slice(0, 2)}
    </span>
  )
}
