import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'

interface HistorySortingProps {
  sortBy: string
  sortOrder: 'ASC' | 'DESC'
  onSortByChange: (val: string) => void
  onSortOrderChange: (val: 'ASC' | 'DESC') => void
}

export function HistorySorting({
  sortBy,
  sortOrder,
  onSortByChange,
  onSortOrderChange,
}: Readonly<HistorySortingProps>) {
  const toggleOrder = () => {
    onSortOrderChange(sortOrder === 'ASC' ? 'DESC' : 'ASC')
  }

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
        <ArrowUpDown className="w-3.5 h-3.5 text-amber-400" />
        <span>Sort:</span>
      </div>

      <select
        value={sortBy}
        onChange={(e) => onSortByChange(e.target.value)}
        className="bg-slate-900 text-xs font-medium text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 outline-none focus:border-amber-500/80 cursor-pointer"
      >
        <option value="created_at">Date Created</option>
        <option value="overall_score">Overall Score</option>
        <option value="question">Question</option>
        <option value="verdict">Verdict</option>
      </select>

      <button
        onClick={toggleOrder}
        className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 rounded-lg border border-slate-800 transition-colors cursor-pointer"
        title={`Sort direction: ${sortOrder}`}
      >
        {sortOrder === 'ASC' ? (
          <>
            <ArrowUp className="w-3.5 h-3.5 text-emerald-400" />
            <span>ASC</span>
          </>
        ) : (
          <>
            <ArrowDown className="w-3.5 h-3.5 text-amber-400" />
            <span>DESC</span>
          </>
        )}
      </button>
    </div>
  )
}
