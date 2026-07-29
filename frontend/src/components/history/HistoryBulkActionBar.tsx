import { Trash2, X, CheckSquare } from 'lucide-react'
import { cn } from '@/utils'

interface HistoryBulkActionBarProps {
  selectedCount: number
  onDeleteClick: () => void
  onCancel: () => void
  disabled?: boolean
}

export function HistoryBulkActionBar({
  selectedCount,
  onDeleteClick,
  onCancel,
  disabled = false,
}: Readonly<HistoryBulkActionBarProps>) {
  const isVisible = selectedCount > 0

  return (
    <div
      className={cn(
        'w-full transition-all duration-300 ease-in-out transform origin-top',
        isVisible
          ? 'opacity-100 max-h-20 py-3.5 px-5 my-2 border border-slate-700/80 bg-slate-900/90 backdrop-blur-md rounded-2xl shadow-xl flex items-center justify-between gap-4'
          : 'opacity-0 max-h-0 py-0 my-0 border-0 overflow-hidden pointer-events-none'
      )}
      aria-hidden={!isVisible}
    >
      <div className="flex items-center gap-2.5 text-xs font-bold text-slate-100">
        <CheckSquare className="w-4 h-4 text-amber-400 shrink-0" />
        <span>
          <strong className="text-amber-400 font-extrabold text-sm">{selectedCount}</strong> Selected
        </span>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onDeleteClick}
          disabled={disabled || !isVisible}
          className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold text-white bg-rose-600 hover:bg-rose-500 disabled:opacity-50 rounded-xl transition-all duration-150 shadow-md cursor-pointer disabled:cursor-not-allowed"
          aria-label="Delete selected evaluations"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Delete Selected</span>
        </button>

        <button
          type="button"
          onClick={onCancel}
          disabled={disabled || !isVisible}
          className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl transition-all duration-150 cursor-pointer disabled:opacity-50"
          aria-label="Clear selection"
        >
          <X className="w-3.5 h-3.5" />
          <span>Clear Selection</span>
        </button>
      </div>
    </div>
  )
}
