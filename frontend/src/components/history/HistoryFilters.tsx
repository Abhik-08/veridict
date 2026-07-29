import { Filter, RotateCcw, X, ArrowRight } from 'lucide-react'

interface HistoryFiltersProps {
  verdict: string
  sourceType: string
  scoreMin?: number
  scoreMax?: number
  dateFrom: string
  dateTo: string
  onVerdictChange: (val: string) => void
  onSourceTypeChange: (val: string) => void
  onScoreMinChange: (val: number | undefined) => void
  onScoreMaxChange: (val: number | undefined) => void
  onDateFromChange: (val: string) => void
  onDateToChange: (val: string) => void
  onReset: () => void
}

export function HistoryFilters({
  verdict,
  sourceType,
  scoreMin,
  scoreMax,
  dateFrom,
  dateTo,
  onVerdictChange,
  onSourceTypeChange,
  onScoreMinChange,
  onScoreMaxChange,
  onDateFromChange,
  onDateToChange,
  onReset,
}: Readonly<HistoryFiltersProps>) {
  const hasActiveFilters =
    verdict !== 'ALL' ||
    sourceType !== 'ALL' ||
    scoreMin !== undefined ||
    scoreMax !== undefined ||
    dateFrom !== '' ||
    dateTo !== ''

  return (
    <div className="space-y-3">
      {/* Filter Control Bar */}
      <div className="flex flex-wrap items-center gap-3.5 bg-slate-900/80 p-4 rounded-2xl border border-slate-800/90 shadow-sm backdrop-blur-md">
        {/* Header Indicator */}
        <div className="flex items-center gap-2 text-xs text-amber-400 font-bold tracking-wide uppercase pr-2 border-r border-slate-800/80">
          <Filter className="w-4 h-4" />
          <span>Filters</span>
        </div>

        {/* Verdict Filter */}
        <div className="flex flex-col gap-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Verdict
          </span>
          <select
            value={verdict}
            onChange={(e) => onVerdictChange(e.target.value)}
            aria-label="Filter by verdict"
            className="bg-slate-950 text-xs font-medium text-slate-200 border border-slate-800 rounded-xl px-3 py-1.5 outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/80 cursor-pointer transition-all duration-150"
          >
            <option value="ALL">All Verdicts</option>
            <option value="PASS">PASS</option>
            <option value="NEEDS_IMPROVEMENT">NEEDS IMPROVEMENT</option>
            <option value="FAIL">FAIL</option>
          </select>
        </div>

        {/* Source Type Filter */}
        <div className="flex flex-col gap-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Source
          </span>
          <select
            value={sourceType}
            onChange={(e) => onSourceTypeChange(e.target.value)}
            aria-label="Filter by source type"
            className="bg-slate-950 text-xs font-medium text-slate-200 border border-slate-800 rounded-xl px-3 py-1.5 outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/80 cursor-pointer transition-all duration-150"
          >
            <option value="ALL">All Sources</option>
            <option value="SINGLE">⚡ Single Prompt</option>
            <option value="BATCH">📦 Batch Dataset</option>
          </select>
        </div>

        {/* Score Range Filters */}
        <div className="flex flex-col gap-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Score Range
          </span>
          <div className="flex items-center gap-1.5">
            <input
              type="number"
              step="0.1"
              min="0"
              max="5"
              placeholder="Min"
              value={scoreMin ?? ''}
              onChange={(e) => onScoreMinChange(e.target.value ? Number.parseFloat(e.target.value) : undefined)}
              aria-label="Minimum score"
              className="w-16 bg-slate-950 text-xs font-medium text-slate-200 border border-slate-800 rounded-xl px-2.5 py-1.5 outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/80 transition-all duration-150 text-center"
            />
            <span className="text-slate-600 text-xs font-bold">—</span>
            <input
              type="number"
              step="0.1"
              min="0"
              max="5"
              placeholder="Max"
              value={scoreMax ?? ''}
              onChange={(e) => onScoreMaxChange(e.target.value ? Number.parseFloat(e.target.value) : undefined)}
              aria-label="Maximum score"
              className="w-16 bg-slate-950 text-xs font-medium text-slate-200 border border-slate-800 rounded-xl px-2.5 py-1.5 outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/80 transition-all duration-150 text-center"
            />
          </div>
        </div>

        {/* Date Range Filters */}
        <div className="flex flex-col gap-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Date Range
          </span>
          <div className="flex items-center gap-1.5">
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => onDateFromChange(e.target.value)}
              aria-label="From Date"
              className="bg-slate-950 text-xs font-medium text-slate-200 border border-slate-800 rounded-xl px-2.5 py-1.5 outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/80 cursor-pointer transition-all duration-150"
            />
            <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
            <input
              type="date"
              value={dateTo}
              onChange={(e) => onDateToChange(e.target.value)}
              aria-label="To Date"
              className="bg-slate-950 text-xs font-medium text-slate-200 border border-slate-800 rounded-xl px-2.5 py-1.5 outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/80 cursor-pointer transition-all duration-150"
            />
          </div>
        </div>

        {/* Reset Filters Button */}
        <div className="flex items-end ml-auto">
          <button
            type="button"
            onClick={onReset}
            disabled={!hasActiveFilters}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-800 disabled:opacity-40 border border-slate-700/60 rounded-xl transition-all duration-150 cursor-pointer disabled:cursor-not-allowed"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Filters</span>
          </button>
        </div>
      </div>

      {/* Active Filter Chips */}
      {hasActiveFilters && (
        <div className="flex flex-wrap items-center gap-2 pt-1 animate-fade-in">
          <span className="text-[11px] font-semibold text-slate-400">Active Filters:</span>

          {verdict !== 'ALL' && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 shadow-sm">
              <span>Verdict: {verdict}</span>
              <button
                type="button"
                onClick={() => onVerdictChange('ALL')}
                className="hover:text-white transition-colors cursor-pointer"
                aria-label="Remove verdict filter"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}

          {sourceType !== 'ALL' && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 shadow-sm">
              <span>Source: {sourceType}</span>
              <button
                type="button"
                onClick={() => onSourceTypeChange('ALL')}
                className="hover:text-white transition-colors cursor-pointer"
                aria-label="Remove source filter"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}

          {scoreMin !== undefined && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 shadow-sm">
              <span>Min Score: {scoreMin}</span>
              <button
                type="button"
                onClick={() => onScoreMinChange(undefined)}
                className="hover:text-white transition-colors cursor-pointer"
                aria-label="Remove min score filter"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}

          {scoreMax !== undefined && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 shadow-sm">
              <span>Max Score: {scoreMax}</span>
              <button
                type="button"
                onClick={() => onScoreMaxChange(undefined)}
                className="hover:text-white transition-colors cursor-pointer"
                aria-label="Remove max score filter"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}

          {dateFrom && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 shadow-sm">
              <span>From: {dateFrom}</span>
              <button
                type="button"
                onClick={() => onDateFromChange('')}
                className="hover:text-white transition-colors cursor-pointer"
                aria-label="Remove start date filter"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}

          {dateTo && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 shadow-sm">
              <span>To: {dateTo}</span>
              <button
                type="button"
                onClick={() => onDateToChange('')}
                className="hover:text-white transition-colors cursor-pointer"
                aria-label="Remove end date filter"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
        </div>
      )}
    </div>
  )
}
