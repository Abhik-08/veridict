import React from 'react'
import type { AvailableFilterMetadata, AnalyticsFilterParams } from '@/services/dashboardService'
import { Filter, RotateCcw, Calendar, Cpu, Layers, ShieldCheck } from 'lucide-react'

interface AnalyticsFilterBarProps {
  metadata?: AvailableFilterMetadata
  filters: AnalyticsFilterParams
  onFilterChange: (newFilters: AnalyticsFilterParams) => void
  onReset: () => void
  loading?: boolean
}

export const AnalyticsFilterBar: React.FC<AnalyticsFilterBarProps> = ({
  metadata,
  filters,
  onFilterChange,
  onReset,
  loading = false,
}) => {
  const hasActiveFilters = Boolean(
    filters.date_from ||
      filters.date_to ||
      (filters.source_type && filters.source_type !== 'ALL') ||
      (filters.verdict && filters.verdict !== 'ALL') ||
      (filters.model && filters.model !== 'ALL'),
  )

  const handleInputChange = (field: keyof AnalyticsFilterParams, value: string) => {
    onFilterChange({
      ...filters,
      [field]: value === 'ALL' ? undefined : value || undefined,
    })
  }

  return (
    <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-4 sm:p-5 backdrop-blur-xs shadow-xs space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2.5 text-slate-200">
          <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <Filter className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-200">Analytics Filters</h2>
            <p className="text-xs text-slate-400">Refine evaluation stats across dates, modes, models, and verdicts</p>
          </div>
        </div>

        {hasActiveFilters && (
          <button
            type="button"
            onClick={onReset}
            disabled={loading}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 rounded-lg transition-colors cursor-pointer self-start sm:self-auto disabled:opacity-50"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Filters</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {/* Date From */}
        <div className="space-y-1">
          <label htmlFor="filter-date-from" className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>From Date</span>
          </label>
          <input
            id="filter-date-from"
            type="date"
            value={filters.date_from ? filters.date_from.split('T')[0] : ''}
            onChange={(e) => handleInputChange('date_from', e.target.value ? `${e.target.value}T00:00:00Z` : '')}
            style={{ colorScheme: 'dark' }}
            className="w-full bg-slate-950/80 border border-slate-800 text-slate-200 text-xs rounded-xl px-3 py-2 min-h-[38px] focus:outline-hidden focus:border-amber-500/50 transition-colors cursor-pointer"
          />
        </div>

        {/* Date To */}
        <div className="space-y-1">
          <label htmlFor="filter-date-to" className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>To Date</span>
          </label>
          <input
            id="filter-date-to"
            type="date"
            value={filters.date_to ? filters.date_to.split('T')[0] : ''}
            onChange={(e) => handleInputChange('date_to', e.target.value ? `${e.target.value}T23:59:59Z` : '')}
            style={{ colorScheme: 'dark' }}
            className="w-full bg-slate-950/80 border border-slate-800 text-slate-200 text-xs rounded-xl px-3 py-2 min-h-[38px] focus:outline-hidden focus:border-amber-500/50 transition-colors cursor-pointer"
          />
        </div>

        {/* Mode / Source Type */}
        <div className="space-y-1">
          <label htmlFor="filter-source-type" className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            <span>Mode</span>
          </label>
          <select
            id="filter-source-type"
            value={filters.source_type || 'ALL'}
            onChange={(e) => handleInputChange('source_type', e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 text-slate-200 text-xs rounded-xl px-3 py-2 min-h-[38px] focus:outline-hidden focus:border-amber-500/50 transition-colors cursor-pointer"
          >
            <option value="ALL">All Modes</option>
            <option value="SINGLE">Single Prompt</option>
            <option value="BATCH">Batch Job</option>
          </select>
        </div>

        {/* Verdict */}
        <div className="space-y-1">
          <label htmlFor="filter-verdict" className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
            <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
            <span>Verdict</span>
          </label>
          <select
            id="filter-verdict"
            value={filters.verdict || 'ALL'}
            onChange={(e) => handleInputChange('verdict', e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 text-slate-200 text-xs rounded-xl px-3 py-2 min-h-[38px] focus:outline-hidden focus:border-amber-500/50 transition-colors cursor-pointer"
          >
            <option value="ALL">All Verdicts</option>
            <option value="PASS">Pass</option>
            <option value="NEEDS_IMPROVEMENT">Needs Improvement</option>
            <option value="FAIL">Fail</option>
          </select>
        </div>

        {/* Model */}
        <div className="space-y-1">
          <label htmlFor="filter-model" className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-slate-400" />
            <span>Response Model</span>
          </label>
          <select
            id="filter-model"
            value={filters.model || 'ALL'}
            onChange={(e) => handleInputChange('model', e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 text-slate-200 text-xs rounded-xl px-3 py-2 min-h-[38px] focus:outline-hidden focus:border-amber-500/50 transition-colors cursor-pointer"
          >
            <option value="ALL">All Models</option>
            {metadata?.available_models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}
