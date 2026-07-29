import { Inbox, SearchX, FilterX } from 'lucide-react'

interface EmptyStateProps {
  type?: 'empty' | 'search' | 'filter'
  title?: string
  description?: string
  actionText?: string
  onAction?: () => void
}

export function EmptyState({
  type = 'empty',
  title,
  description,
  actionText,
  onAction,
}: Readonly<EmptyStateProps>) {
  const getIcon = () => {
    switch (type) {
      case 'search':
        return <SearchX className="w-10 h-10 text-amber-400/80" />
      case 'filter':
        return <FilterX className="w-10 h-10 text-amber-400/80" />
      default:
        return <Inbox className="w-10 h-10 text-amber-400/80" />
    }
  }

  const getDefaultTitle = () => {
    if (type === 'search') return 'No Search Results Found'
    if (type === 'filter') return 'No Matching Evaluations Found'
    return 'No Evaluation History Yet'
  }

  const getDefaultDescription = () => {
    if (type === 'search') return 'Try adjusting your search terms or clearing your search query.'
    if (type === 'filter') return 'No evaluation records matched your active filters. Try changing your filters or run a new evaluation.'
    return 'Run your first single prompt or batch evaluation to begin building permanent evaluation history.'
  }

  return (
    <div className="flex flex-col items-center justify-center p-10 text-center bg-slate-900/40 rounded-2xl border border-slate-800/80 my-4 shadow-sm">
      <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 mb-4">
        {getIcon()}
      </div>
      <h3 className="text-base font-bold text-slate-100">{title || getDefaultTitle()}</h3>
      <p className="mt-1.5 text-xs text-slate-400 max-w-md leading-relaxed">
        {description || getDefaultDescription()}
      </p>

      {onAction && actionText && (
        <button
          type="button"
          onClick={onAction}
          className="mt-5 px-4 py-2 text-xs font-bold text-slate-950 bg-amber-500 hover:bg-amber-400 rounded-xl transition-all duration-150 shadow-md cursor-pointer"
        >
          {actionText}
        </button>
      )}
    </div>
  )
}
