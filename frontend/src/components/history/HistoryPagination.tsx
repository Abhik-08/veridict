import { ChevronLeft, ChevronRight } from 'lucide-react'
import type { PaginationMetadata } from '@/services/historyService'

interface HistoryPaginationProps {
  pagination: PaginationMetadata
  onPageChange: (page: number) => void
  onPageSizeChange: (pageSize: number) => void
}

export function HistoryPagination({
  pagination,
  onPageChange,
  onPageSizeChange,
}: Readonly<HistoryPaginationProps>) {
  const { page, page_size, total_items, total_pages, has_next, has_previous } = pagination

  if (total_items === 0) return null

  const startItem = (page - 1) * page_size + 1
  const endItem = Math.min(page * page_size, total_items)

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-800/80">
      {/* Page Size Selector & Items Counter */}
      <div className="flex items-center gap-3 text-xs text-slate-400">
        <span className="font-medium">
          Showing <strong className="text-slate-200">{startItem}-{endItem}</strong> of{' '}
          <strong className="text-slate-200">{total_items}</strong> records
        </span>

        <div className="flex items-center gap-1.5 ml-2">
          <span>Rows per page:</span>
          <select
            value={page_size}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="bg-slate-900 text-xs text-slate-200 border border-slate-800 rounded px-1.5 py-1 outline-none cursor-pointer"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => onPageChange(page - 1)}
          disabled={!has_previous}
          className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 border border-slate-800 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
          <span>Previous</span>
        </button>

        <span className="text-xs font-semibold text-slate-300 px-2">
          Page {page} of {total_pages || 1}
        </span>

        <button
          type="button"
          onClick={() => onPageChange(page + 1)}
          disabled={!has_next}
          className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 border border-slate-800 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed"
        >
          <span>Next</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}
