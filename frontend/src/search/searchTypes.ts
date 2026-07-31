/**
 * Shared type definitions for Veridict Global Search Architecture.
 */

export type VerdictType = 'PASS' | 'NEEDS_IMPROVEMENT' | 'FAIL'

/**
 * Standardized document representation extracted from any evaluation model (batch, single, history).
 */
export interface EvaluationSearchDocument {
  id: string
  batchId?: string | null
  filename?: string | null
  question: string
  aiResponse: string
  referenceAnswer?: string | null
  evidenceText?: string | null
  evidenceSource?: string | null
  reasoning?: string | null
  accuracyReasoning?: string | null
  relevanceReasoning?: string | null
  completenessReasoning?: string | null
  hallucinationReasoning?: string | null
  verdict?: VerdictType | null
  overallScore?: number | null
  accuracyScore?: number | null
  relevanceScore?: number | null
  completenessScore?: number | null
  hallucinationScore?: number | null
  createdAt?: string | Date | null
  formattedDate?: string | null
  searchableText?: string
}

export interface SearchFilter {
  verdict?: VerdictType | 'ALL'
  minScore?: number
  maxScore?: number
  startDate?: string | Date
  endDate?: string | Date
  batchId?: string
  evidenceSource?: string
}

export interface SortOptions {
  field?: 'relevance' | 'score' | 'createdAt' | 'id' | (string & {})
  order?: 'asc' | 'desc'
}

export interface PaginationOptions {
  page?: number
  pageSize?: number
}

export interface SearchOptions<T = any> {
  items: T[]
  query?: string
  filters?: SearchFilter
  sort?: SortOptions
  pagination?: PaginationOptions
  documentExtractor?: (item: T) => EvaluationSearchDocument
}

export interface ScoredResult<T = any> {
  item: T
  doc: EvaluationSearchDocument
  score: number
}

export interface SearchResult<T = any> {
  items: T[]
  scoredItems: ScoredResult<T>[]
  total: number
  page: number
  pageSize: number
  totalPages: number
  query: string
  hasMore: boolean
}

export interface HighlightFragment {
  text: string
  isMatch: boolean
}
