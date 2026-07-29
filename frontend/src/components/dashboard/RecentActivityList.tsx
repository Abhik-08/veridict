import { Clock, CheckCircle2, AlertTriangle, XCircle, Eye } from 'lucide-react'
import type { HistoryItemResponse } from '@/services/historyService'
import { cn } from '@/utils'

interface RecentActivityListProps {
  items: HistoryItemResponse[]
  loading: boolean
  onItemClick: (id: string) => void
}

export function RecentActivityList({ items, loading, onItemClick }: Readonly<RecentActivityListProps>) {
  const getVerdictBadge = (verdict: string) => {
    switch (verdict.toUpperCase()) {
      case 'PASS':
        return (
          <span className={cn('inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30')}>
            <CheckCircle2 className="w-3 h-3" />
            <span>PASS</span>
          </span>
        )
      case 'NEEDS_IMPROVEMENT':
        return (
          <span className={cn('inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30')}>
            <AlertTriangle className="w-3 h-3" />
            <span>NEEDS IMPROVEMENT</span>
          </span>
        )
      case 'FAIL':
        return (
          <span className={cn('inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30')}>
            <XCircle className="w-3 h-3" />
            <span>FAIL</span>
          </span>
        )
      default:
        return (
          <span className={cn('inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300')}>
            {verdict}
          </span>
        )
    }
  }

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString)
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } catch {
      return isoString
    }
  }

  const renderContent = () => {
    if (loading) {
      return (
        <div className={cn('space-y-3')}>
          {Array.from({ length: 5 }).map((_, idx) => (
            <div key={idx} className={cn('animate-pulse h-12 bg-slate-800/60 rounded-xl')} />
          ))}
        </div>
      )
    }

    if (items.length === 0) {
      return (
        <div className={cn('text-center py-8 text-xs text-slate-500')}>
          No recent evaluations recorded.
        </div>
      )
    }

    return (
      <div className={cn('divide-y divide-slate-800/60')}>
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onItemClick(item.id)}
            className={cn('w-full text-left py-3 px-2 flex items-center justify-between gap-4 hover:bg-slate-800/40 rounded-xl transition-colors cursor-pointer group')}
          >
            <div className={cn('flex-1 min-w-0')}>
              <p className={cn('text-xs font-medium text-slate-200 truncate group-hover:text-amber-300 transition-colors')}>
                {item.question}
              </p>
              <div className={cn('mt-1 flex items-center gap-2.5 text-[11px] text-slate-400')}>
                <span>Score: <strong className={cn('text-slate-200')}>{item.overall_score.toFixed(1)}</strong></span>
                <span>•</span>
                <span>{formatDate(item.created_at)}</span>
              </div>
            </div>

            <div className={cn('flex items-center gap-3')}>
              {getVerdictBadge(item.verdict)}
              <Eye className="w-4 h-4 text-slate-500 group-hover:text-amber-400 transition-colors" />
            </div>
          </button>
        ))}
      </div>
    )
  }

  return (
    <div className={cn('p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-md shadow-xl space-y-4')}>
      <div className={cn('flex items-center justify-between border-b border-slate-800/80 pb-3.5')}>
        <div className={cn('flex items-center gap-2')}>
          <Clock className="w-4 h-4 text-amber-400" />
          <h2 className={cn('text-sm font-bold text-slate-100 uppercase tracking-wide')}>
            Recent Evaluation Feed
          </h2>
        </div>
        <span className={cn('text-xs text-slate-400 font-medium')}>
          Latest {items.length} records
        </span>
      </div>

      {renderContent()}
    </div>
  )
}
