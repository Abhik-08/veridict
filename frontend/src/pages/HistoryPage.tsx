import { SectionContainer } from '@/components'
import { HistorySearchBar } from '@/components/history/HistorySearchBar'
import { HistoryFilters } from '@/components/history/HistoryFilters'
import { HistorySorting } from '@/components/history/HistorySorting'
import { HistoryTable } from '@/components/history/HistoryTable'
import { HistoryPagination } from '@/components/history/HistoryPagination'
import { HistoryBulkActionBar } from '@/components/history/HistoryBulkActionBar'
import { BulkDeleteConfirmationModal } from '@/components/history/BulkDeleteConfirmationModal'
import { EvaluationDetailModal } from '@/components/history/EvaluationDetailModal'
import { ErrorState } from '@/components/shared/ErrorState'
import { useHistory } from '@/hooks/useHistory'
import { History as HistoryIcon, RefreshCw, CheckCircle2 } from 'lucide-react'

export function HistoryPage() {
  const {
    items,
    pagination,
    loading,
    error,
    search,
    verdict,
    sourceType,
    sortBy,
    sortOrder,
    dateFrom,
    dateTo,
    scoreMin,
    scoreMax,
    selectedEvalId,
    detailItem,
    detailLoading,
    isSelectionMode,
    selectedIds,
    isBulkModalOpen,
    isBulkDeleting,
    bulkFeedback,
    setPage,
    setPageSize,
    setSearch,
    setVerdict,
    setSourceType,
    setSortBy,
    setSortOrder,
    setDateFrom,
    setDateTo,
    setScoreMin,
    setScoreMax,
    setIsBulkModalOpen,
    enterSelectionMode,
    exitSelectionMode,
    toggleSelectId,
    openDetail,
    closeDetail,
    confirmBulkDelete,
    resetFilters,
    refetch,
  } = useHistory()

  const hasActiveFilters =
    verdict !== 'ALL' ||
    sourceType !== 'ALL' ||
    scoreMin !== undefined ||
    scoreMax !== undefined ||
    dateFrom !== '' ||
    dateTo !== ''

  return (
    <div className="flex flex-col items-center w-full min-h-[calc(100vh-72px)] pb-16 pt-6 relative">
      <SectionContainer className="space-y-6">
        {/* Header Title */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <HistoryIcon className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-display text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-100">
                Evaluation History
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Audit, search, filter, and inspect past AI evaluation records
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={refetch}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
            title="Refresh history"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Bulk Operation Feedback Toast Banner */}
        {bulkFeedback && (
          <div className="flex items-center gap-2.5 p-3.5 px-4 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-semibold animate-fade-in shadow-md">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{bulkFeedback}</span>
          </div>
        )}

        {/* Search & Sort Header Controls */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          <HistorySearchBar value={search} onChange={setSearch} />
          <HistorySorting
            sortBy={sortBy}
            sortOrder={sortOrder}
            onSortByChange={setSortBy}
            onSortOrderChange={setSortOrder}
          />
        </div>

        {/* Filter Controls Bar */}
        <HistoryFilters
          verdict={verdict}
          sourceType={sourceType}
          scoreMin={scoreMin}
          scoreMax={scoreMax}
          dateFrom={dateFrom}
          dateTo={dateTo}
          onVerdictChange={setVerdict}
          onSourceTypeChange={setSourceType}
          onScoreMinChange={setScoreMin}
          onScoreMaxChange={setScoreMax}
          onDateFromChange={setDateFrom}
          onDateToChange={setDateTo}
          onReset={resetFilters}
        />

        {/* Main Content / Error State / History Table */}
        {error ? (
          <ErrorState message={error} onRetry={refetch} />
        ) : (
          <div className="space-y-4">
            {/* Selection Mode Bulk Action Bar */}
            <HistoryBulkActionBar
              selectedCount={selectedIds.length}
              onDeleteClick={() => setIsBulkModalOpen(true)}
              onCancel={exitSelectionMode}
              disabled={isBulkDeleting}
            />

            <HistoryTable
              items={items}
              loading={loading}
              searchQuery={search}
              hasActiveFilters={hasActiveFilters}
              isSelectionMode={isSelectionMode}
              selectedIds={selectedIds}
              isDeleting={isBulkDeleting}
              onToggleSelect={toggleSelectId}
              onEnterSelectionMode={enterSelectionMode}
              onRowClick={openDetail}
              onResetFilters={resetFilters}
            />

            <HistoryPagination
              pagination={pagination}
              onPageChange={setPage}
              onPageSizeChange={setPageSize}
            />
          </div>
        )}

        {/* Bulk Delete Confirmation Modal */}
        <BulkDeleteConfirmationModal
          isOpen={isBulkModalOpen}
          selectedCount={selectedIds.length}
          onClose={() => setIsBulkModalOpen(false)}
          onConfirm={confirmBulkDelete}
          isDeleting={isBulkDeleting}
        />

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
