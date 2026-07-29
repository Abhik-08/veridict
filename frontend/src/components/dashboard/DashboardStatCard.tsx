import type React from 'react'

interface DashboardStatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  accentColor?: 'amber' | 'emerald' | 'rose' | 'blue' | 'purple' | 'slate'
}

export function DashboardStatCard({
  title,
  value,
  subtitle,
  icon,
  accentColor = 'amber',
}: Readonly<DashboardStatCardProps>) {
  const getBadgeStyle = () => {
    switch (accentColor) {
      case 'emerald':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25'
      case 'rose':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/25'
      case 'blue':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/25'
      case 'purple':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/25'
      case 'slate':
        return 'bg-slate-800 text-slate-300 border-slate-700'
      default:
        return 'bg-amber-500/10 text-amber-400 border-amber-500/25'
    }
  }

  return (
    <div className="p-5 sm:p-6 rounded-2xl bg-slate-900/70 border border-slate-800/90 backdrop-blur-md shadow-xl hover:border-amber-500/30 hover:shadow-glow-sm transition-all duration-200 flex flex-col justify-between group">
      <div className="flex items-center justify-between gap-3">
        <span className="text-[11px] font-bold text-slate-400 tracking-wider uppercase group-hover:text-slate-300 transition-colors">
          {title}
        </span>
        <div className={`p-2.5 rounded-xl border ${getBadgeStyle()} transition-transform duration-200 group-hover:scale-105`}>
          {icon}
        </div>
      </div>

      <div className="mt-4">
        <div className="text-2xl sm:text-3xl font-black text-slate-100 tracking-tight group-hover:text-amber-300 transition-colors">
          {value}
        </div>
        {subtitle && (
          <p className="mt-1 text-[11px] text-slate-400 font-medium leading-normal">{subtitle}</p>
        )}
      </div>
    </div>
  )
}
