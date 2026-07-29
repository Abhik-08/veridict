import { useState, useEffect, useCallback, useRef } from 'react'
import {
  historyService,
  type HistoryItemResponse,
  type EvaluationDetailResponse,
  type PaginationMetadata,
  type HistoryFilterParams,
} from '@/services/historyService'

export function useHistory() {
  const [items, setItems] = useState<HistoryItemResponse[]>([])
  const [pagination, setPagination] = useState<PaginationMetadata>({
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 0,
    has_next: false,
    has_previous: false,
  })

  // Filter & Search & Sort states
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [verdict, setVerdict] = useState<string>('ALL')
  const [sourceType, setSourceType] = useState<string>('ALL')
  const [sortBy, setSortBy] = useState<string>('created_at')
  const [sortOrder, setSortOrder] = useState<'ASC' | 'DESC'>('DESC')
  const [dateFrom, setDateFrom] = useState<string>('')
  const [dateTo, setDateTo] = useState<string>('')
  const [scoreMin, setScoreMin] = useState<number | undefined>(undefined)
  const [scoreMax, setScoreMax] = useState<number | undefined>(undefined)

  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Detail Modal State
  const [selectedEvalId, setSelectedEvalId] = useState<string | null>(null)
  const [detailItem, setDetailItem] = useState<EvaluationDetailResponse | null>(null)
  const [detailLoading, setDetailLoading] = useState<boolean>(false)

  // Single Delete Modal State
  const [itemToDelete, setItemToDelete] = useState<HistoryItemResponse | null>(null)
  const [isDeleting, setIsDeleting] = useState<boolean>(false)

  // Selection Mode & Manual Multi-Select Bulk Delete State
  const [isSelectionMode, setIsSelectionMode] = useState<boolean>(false)
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [isBulkModalOpen, setIsBulkModalOpen] = useState<boolean>(false)
  const [isBulkDeleting, setIsBulkDeleting] = useState<boolean>(false)
  const [bulkFeedback, setBulkFeedback] = useState<string | null>(null)

  // Debounce search input by 300ms
  const searchTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }
    searchTimeoutRef.current = setTimeout(() => {
      setDebouncedSearch(search)
      setPage(1) // Reset to page 1 on new search
    }, 300)

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
    }
  }, [search])

  const fetchHistory = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params: HistoryFilterParams = {
        page,
        page_size: pageSize,
        search: debouncedSearch.trim() || undefined,
        verdict: verdict !== 'ALL' ? verdict : undefined,
        source_type: sourceType !== 'ALL' ? sourceType : undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
        date_from: dateFrom ? new Date(dateFrom).toISOString() : undefined,
        date_to: dateTo ? new Date(dateTo).toISOString() : undefined,
        score_min: scoreMin,
        score_max: scoreMax,
      }

      const res = await historyService.getHistory(params)
      setItems(res.items || [])
      setPagination(res.pagination)
    } catch (err: any) {
      console.error('Failed to fetch history:', err)
      setError(err.response?.data?.message || err.message || 'Failed to load evaluation history.')
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, debouncedSearch, verdict, sourceType, sortBy, sortOrder, dateFrom, dateTo, scoreMin, scoreMax])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  // Selection mode handlers
  const enterSelectionMode = (initialId: string) => {
    setIsSelectionMode(true)
    setSelectedIds([initialId])
  }

  const exitSelectionMode = () => {
    setIsSelectionMode(false)
    setSelectedIds([])
  }

  const toggleSelectId = (id: string) => {
    setSelectedIds((prev) => {
      const next = prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
      if (next.length === 0) {
        setIsSelectionMode(false)
      }
      return next
    })
  }

  // Fetch Evaluation Detail
  const openDetail = async (id: string) => {
    setSelectedEvalId(id)
    setDetailLoading(true)
    setDetailItem(null)
    try {
      const detail = await historyService.getEvaluationDetail(id)
      setDetailItem(detail)
    } catch (err: any) {
      console.error('Failed to fetch evaluation detail:', err)
    } finally {
      setDetailLoading(false)
    }
  }

  const closeDetail = () => {
    setSelectedEvalId(null)
    setDetailItem(null)
  }

  // Single Delete Evaluation
  const confirmDelete = async () => {
    if (!itemToDelete) return
    setIsDeleting(true)
    try {
      await historyService.deleteEvaluation(itemToDelete.id)
      setSelectedIds((prev) => prev.filter((id) => id !== itemToDelete.id))
      setItemToDelete(null)
      if (selectedEvalId === itemToDelete.id) {
        closeDetail()
      }
      fetchHistory()
    } catch (err: any) {
      console.error('Failed to delete history item:', err)
      alert(err.response?.data?.message || 'Failed to delete evaluation record.')
    } finally {
      setIsDeleting(false)
    }
  }

  // Multi-Select Sequential Bulk Delete
  const confirmBulkDelete = async () => {
    if (selectedIds.length === 0) return
    setIsBulkDeleting(true)
    setBulkFeedback(null)

    let successCount = 0
    let failureCount = 0

    for (const id of selectedIds) {
      try {
        await historyService.deleteEvaluation(id)
        successCount++
      } catch (err) {
        console.error(`Failed to delete item ${id}:`, err)
        failureCount++
      }
    }

    setIsBulkDeleting(false)
    setIsBulkModalOpen(false)

    if (failureCount === 0) {
      setBulkFeedback(`Successfully deleted ${successCount} evaluation record${successCount > 1 ? 's' : ''}.`)
    } else {
      setBulkFeedback(`Deleted ${successCount} evaluation record${successCount !== 1 ? 's' : ''}. Failed to delete ${failureCount}.`)
    }

    exitSelectionMode()
    fetchHistory()

    // Auto dismiss feedback banner after 4 seconds
    setTimeout(() => {
      setBulkFeedback(null)
    }, 4000)
  }

  const resetFilters = () => {
    setSearch('')
    setDebouncedSearch('')
    setVerdict('ALL')
    setSourceType('ALL')
    setSortBy('created_at')
    setSortOrder('DESC')
    setDateFrom('')
    setDateTo('')
    setScoreMin(undefined)
    setScoreMax(undefined)
    setPage(1)
  }

  return {
    items,
    pagination,
    loading,
    error,
    page,
    pageSize,
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
    itemToDelete,
    isDeleting,
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
    setItemToDelete,
    setIsBulkModalOpen,
    enterSelectionMode,
    exitSelectionMode,
    toggleSelectId,
    openDetail,
    closeDetail,
    confirmDelete,
    confirmBulkDelete,
    resetFilters,
    refetch: fetchHistory,
  }
}
