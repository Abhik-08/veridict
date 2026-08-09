import { useState } from 'react'
import { SectionContainer } from '@/components'
import {
  DashboardStatsGrid,
  RecentActivityList,
  AnalyticsFilterBar,
  DimensionScoreChart,
  VerdictDistributionChart,
  QualityTrendChart,
  HallucinationAnalysis,
} from '@/components/dashboard'
import { EvaluationDetailModal } from '@/components/history/EvaluationDetailModal'
import { ErrorState } from '@/components/shared/ErrorState'
import { useDashboard } from '@/hooks/useDashboard'
import { historyService, type EvaluationDetailResponse } from '@/services/historyService'
import { LayoutDashboard, RefreshCw, ArrowRight, FilterX } from 'lucide-react'
import { Link } from 'react-router-dom'

export function DashboardPage() {
  const {
    stats,
    recentItems,
    analytics,
    loading,
    analyticsLoading,
    error,
    filters,
    updateFilters,
    resetFilters,
    refetch,
  } = useDashboard()

  const [selectedEvalId, setSelectedEvalId] = useState<string | null>(null)
  const [detailItem, setDetailItem] = useState<EvaluationDetailResponse | null>(null)
  const [detailLoading, setDetailLoading] = useState<boolean>(false)

  const openDetail = async (id: string) => {
    setSelectedEvalId(id)
    setDetailLoading(true)
    setDetailItem(null)
    try {
      const detail = await historyService.getEvaluationDetail(id)
      setDetailItem(detail)
    } catch (err) {
      console.error('Failed to fetch evaluation detail:', err)
    } finally {
      setDetailLoading(false)
    }
  }

  const closeDetail = () => {
    setSelectedEvalId(null)
    setDetailItem(null)
  }

  const hasEmptyAnalytics = !analyticsLoading && analytics?.total_evaluations === 0

  return (
    <div className="flex flex-col items-center w-full min-h-[calc(100vh-72px)] pb-16 pt-6">
      <SectionContainer className="space-y-6">
        {/* Header Title */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <LayoutDashboard className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-display text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-100">
                Evaluation Dashboard
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Overview of response quality metrics, verdict distributions, and recent evaluations
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link
              to="/history"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-950 bg-amber-500 hover:bg-amber-400 rounded-lg transition-colors shadow-xs"
            >
              <span>View Full History</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>

            <button
              type="button"
              onClick={refetch}
              disabled={loading || analyticsLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
              title="Refresh dashboard metrics"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading || analyticsLoading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Content Body */}
        {error ? (
          <ErrorState message={error} onRetry={refetch} />
        ) : (
          <div className="space-y-6">
            {/* KPI Cards Grid */}
            <DashboardStatsGrid stats={stats} analytics={analytics} loading={loading || analyticsLoading} />

            {/* Analytics Filter Area */}
            <AnalyticsFilterBar
              metadata={analytics?.available_filters}
              filters={filters}
              onFilterChange={updateFilters}
              onReset={resetFilters}
              loading={analyticsLoading}
            />

            {/* Empty Analytics State vs Analytics Content */}
            {hasEmptyAnalytics ? (
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-10 text-center space-y-3">
                <div className="mx-auto w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
                  <FilterX className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-slate-200">No evaluations match the selected filters</h3>
                <p className="text-xs text-slate-400 max-w-md mx-auto">
                  Try adjusting or resetting your date range, evaluation mode, model, or verdict filters.
                </p>
                <button
                  type="button"
                  onClick={resetFilters}
                  className="px-3.5 py-1.5 text-xs font-semibold text-slate-950 bg-amber-500 hover:bg-amber-400 rounded-lg transition-colors cursor-pointer inline-flex items-center gap-1.5"
                >
                  Clear Filters
                </button>
              </div>
            ) : (
              <>
                {/* Analytics Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <DimensionScoreChart scores={analytics?.average_scores} loading={analyticsLoading} />
                  <VerdictDistributionChart
                    distribution={analytics?.verdict_distribution}
                    totalEvaluations={analytics?.total_evaluations}
                    loading={analyticsLoading}
                  />
                </div>

                {/* Quality Trend Over Time */}
                <QualityTrendChart trends={analytics?.quality_trends} loading={analyticsLoading} />

                {/* Hallucination Metrics */}
                <HallucinationAnalysis metrics={analytics?.hallucination_metrics} loading={analyticsLoading} />
              </>
            )}

            {/* Recent Activity Feed */}
            <RecentActivityList
              items={recentItems}
              loading={loading}
              onItemClick={openDetail}
            />
          </div>
        )}

        {/* Evaluation Detail Modal */}
        <EvaluationDetailModal
          isOpen={Boolean(selectedEvalId)}
          onClose={closeDetail}
          detail={detailItem}
          loading={detailLoading}
        />
      </SectionContainer>
    </div>
  )
}
