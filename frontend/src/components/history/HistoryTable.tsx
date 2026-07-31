import { Eye, Trash2, Calendar, Clock, Layers, Zap, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react'
import type { HistoryItemResponse } from '@/services/historyService'
import { SkeletonRow } from '../shared/SkeletonLoader'
import { EmptyState } from '../shared/EmptyState'
import { cn } from '@/utils'

interface HistoryTableProps {
  items: HistoryItemResponse[]
  loading: boolean
  searchQuery?: string
  hasActiveFilters?: boolean
  isSelectionMode?: boolean
  selectedIds?: string[]
  isDeleting?: boolean
  onToggleSelect?: (id: string) => void
  onEnterSelectionMode?: (initialId: string) => void
  onRowClick: (id: string) => void
  onResetFilters?: () => void
}

export function HistoryTable({
  items,
  loading,
  searchQuery,
  hasActiveFilters,
  isSelectionMode = false,
  selectedIds = [],
  isDeleting = false,
  onToggleSelect,
  onEnterSelectionMode,
  onRowClick,
  onResetFilters,
}: Readonly<HistoryTableProps>) {
  const getVerdictBadge = (verdict: string) => {
    switch (verdict.toUpperCase()) {
      case 'PASS':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm">
            <CheckCircle2 className="w-3 h-3" />
            <span>PASS</span>
          </span>
        )
      case 'NEEDS_IMPROVEMENT':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30 shadow-sm">
            <AlertTriangle className="w-3 h-3" />
            <span>NEEDS IMPROVEMENT</span>
          </span>
        )
      case 'FAIL':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30 shadow-sm">
            <XCircle className="w-3 h-3" />
            <span>FAIL</span>
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
            {verdict}
          </span>
        )
    }
  }

  const getSourceBadge = (source: string) => {
    if (source.toUpperCase() === 'BATCH') {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-purple-400 bg-purple-500/10 border border-purple-500/25 px-2.5 py-1 rounded-lg">
          <Layers className="w-3 h-3" />
          <span>Batch</span>
        </span>
      )
    }
    return (
      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-blue-400 bg-blue-500/10 border border-blue-500/25 px-2.5 py-1 rounded-lg">
        <Zap className="w-3 h-3 text-blue-400" />
        <span>Single</span>
      </span>
    )
  }

  const formatStackedDate = (isoString: string) => {
    try {
      const d = new Date(isoString)
      const datePart = d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
      const timePart = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      return { datePart, timePart }
    } catch {
      return { datePart: isoString, timePart: '' }
    }
  }

  if (loading) {
    return (
      <div className="overflow-x-auto rounded-2xl border border-slate-800/80 bg-slate-900/40">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/90 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
              {isSelectionMode && <th className="py-3.5 px-3.5 w-10"></th>}
              <th className="py-3.5 px-4">Question / Prompt</th>
              <th className="py-3.5 px-4">Verdict</th>
              <th className="py-3.5 px-4">Score</th>
              <th className="py-3.5 px-4">Source</th>
              <th className="py-3.5 px-4">Created Date</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: 5 }).map((_, idx) => (
              <SkeletonRow key={idx} />
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  if (items.length === 0) {
    if (searchQuery) {
      return <EmptyState type="search" onAction={onResetFilters} actionText="Clear Search & Filters" />
    }
    if (hasActiveFilters) {
      return <EmptyState type="filter" onAction={onResetFilters} actionText="Reset Filters" />
    }
    return <EmptyState type="empty" />
  }

  return (
    <div className="overflow-x-auto max-h-[68vh] rounded-2xl border border-slate-800/80 bg-slate-900/50 backdrop-blur-md shadow-2xl relative transition-all duration-300">
      <table className="w-full text-left border-collapse text-xs">
        <thead className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur-md border-b border-slate-800/90 shadow-sm">
          <tr className="text-slate-300 uppercase text-[10px] tracking-wider font-bold">
            {isSelectionMode && (
              <th className="py-3.5 px-3.5 w-10 text-center animate-fade-in">
                {/* No Select All checkbox */}
              </th>
            )}
            <th className="py-3.5 px-4 min-w-[260px]">Question / Prompt</th>
            <th className="py-3.5 px-4 min-w-[130px]">Verdict</th>
            <th className="py-3.5 px-4">Score</th>
            <th className="py-3.5 px-4">Source</th>
            <th className="py-3.5 px-4 min-w-[140px]">Created Date</th>
            <th className="py-3.5 px-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {items.map((item) => {
            const { datePart, timePart } = formatStackedDate(item.created_at)
            const isSelected = selectedIds.includes(item.id)

            return (
              <tr
                key={item.id}
                onClick={() => onRowClick(item.id)}
                className={cn(
                  'transition-all duration-150 cursor-pointer group',
                  isSelected ? 'bg-amber-500/10 hover:bg-amber-500/15' : 'hover:bg-slate-800/60'
                )}
              >
                {/* Selection Mode Checkbox */}
                {isSelectionMode && (
                  <td className="py-3.5 px-3.5 text-center animate-fade-in" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      disabled={isDeleting}
                      onChange={() => onToggleSelect?.(item.id)}
                      aria-label={`Select evaluation ${item.id}`}
                      className="w-4 h-4 rounded border-slate-700 bg-slate-950 text-amber-500 focus:ring-amber-500/30 cursor-pointer disabled:cursor-not-allowed"
                    />
                  </td>
                )}

                <td className="py-3.5 px-4 font-medium text-slate-200">
                  <span className="line-clamp-2 leading-snug group-hover:text-amber-300 transition-colors duration-150">
                    {item.question}
                  </span>
                </td>

                <td className="py-3.5 px-4 whitespace-nowrap">{getVerdictBadge(item.verdict)}</td>

                <td className="py-3.5 px-4 whitespace-nowrap">
                  <span className="font-extrabold text-slate-100 text-sm">
                    {item.overall_score !== undefined ? item.overall_score.toFixed(1) : '-'}
                  </span>
                  <span className="text-[10px] text-slate-500 font-medium"> / 5.0</span>
                </td>

                <td className="py-3.5 px-4 whitespace-nowrap">{getSourceBadge(item.source_type)}</td>

                <td className="py-3.5 px-4 whitespace-nowrap">
                  <div className="flex flex-col text-[11px] leading-tight">
                    <div className="flex items-center gap-1 font-semibold text-slate-200">
                      <Calendar className="w-3 h-3 text-amber-400" />
                      <span>{datePart}</span>
                    </div>
                    {timePart && (
                      <div className="flex items-center gap-1 text-[10px] text-slate-400 mt-0.5">
                        <Clock className="w-2.5 h-2.5 text-slate-500" />
                        <span>{timePart}</span>
                      </div>
                    )}
                  </div>
                </td>

                <td className="py-3.5 px-4 whitespace-nowrap text-right" onClick={(e) => e.stopPropagation()}>
                  <div className="flex items-center justify-end gap-1.5">
                    <button
                      type="button"
                      onClick={() => onRowClick(item.id)}
                      className="p-1.5 text-slate-400 hover:text-amber-400 hover:bg-slate-800 rounded-lg transition-colors duration-150 cursor-pointer"
                      title="View Full Evaluation Details"
                      aria-label="View evaluation detail"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        if (isSelectionMode) {
                          onToggleSelect?.(item.id)
                        } else {
                          onEnterSelectionMode?.(item.id)
                        }
                      }}
                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors duration-150 cursor-pointer"
                      title="Select for deletion"
                      aria-label="Select evaluation record for deletion"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
