import { Search, X } from 'lucide-react'

interface HistorySearchBarProps {
  value: string
  onChange: (val: string) => void
  placeholder?: string
}

export function HistorySearchBar({
  value,
  onChange,
  placeholder = 'Search by question, AI response, ground truth, or reasoning...',
}: Readonly<HistorySearchBarProps>) {
  return (
    <div className="relative w-full max-w-xl">
      <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none transition-colors group-focus-within:text-amber-400" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label="Search evaluation history"
        className="w-full pl-10 pr-9 py-2.5 bg-slate-950/70 text-xs font-medium text-slate-100 placeholder-slate-500 rounded-xl border border-slate-800/90 focus:border-amber-500/80 focus:ring-2 focus:ring-amber-500/20 outline-none transition-all duration-150 shadow-sm"
      />
      {value && (
        <button
          type="button"
          onClick={() => onChange('')}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-200 bg-slate-800/60 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
          title="Clear search"
          aria-label="Clear search text"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  )
}
