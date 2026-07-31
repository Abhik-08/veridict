/**
 * Search Filters Module for Veridict Global Search Engine.
 * Responsible ONLY for applying filtering logic across search documents.
 */

import type { EvaluationSearchDocument, SearchFilter, ScoredResult } from './searchTypes'

function _matchScoreFilter(score: number | null | undefined, min?: number, max?: number): boolean {
  if (min !== undefined && min !== null) {
    if (score === null || score === undefined || score < min) return false
  }
  if (max !== undefined && max !== null) {
    if (score === null || score === undefined || score > max) return false
  }
  return true
}

function _matchDateRange(createdAt: string | Date | null | undefined, start?: string | Date, end?: string | Date): boolean {
  if (!start && !end) return true
  if (!createdAt) return false
  const docDate = typeof createdAt === 'string' ? new Date(createdAt).getTime() : createdAt.getTime()
  if (Number.isNaN(docDate)) return false

  if (start) {
    const startTime = typeof start === 'string' ? new Date(start).getTime() : start.getTime()
    if (docDate < startTime) return false
  }
  if (end) {
    const endTime = typeof end === 'string' ? new Date(end).getTime() : end.getTime()
    if (docDate > endTime) return false
  }
  return true
}

function _matchDocFilters(doc: EvaluationSearchDocument, filters: SearchFilter): boolean {
  if (filters.verdict && filters.verdict !== 'ALL' && doc.verdict !== filters.verdict) {
    return false
  }

  if (!_matchScoreFilter(doc.overallScore, filters.minScore, filters.maxScore)) {
    return false
  }

  if (filters.batchId && doc.batchId !== filters.batchId) return false
  if (filters.evidenceSource && doc.evidenceSource !== filters.evidenceSource) return false

  return _matchDateRange(doc.createdAt, filters.startDate, filters.endDate)
}

/**
 * Applies search filters to a list of scored search items.
 */
export function applySearchFilters<T>(
  scoredItems: ScoredResult<T>[],
  filters?: SearchFilter
): ScoredResult<T>[] {
  if (!filters) return scoredItems
  return scoredItems.filter(({ doc }) => _matchDocFilters(doc, filters))
}
