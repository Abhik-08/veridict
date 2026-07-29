/**
 * Global Search Engine Module for Veridict.
 * Main entry point for searching, filtering, ranking, sorting, and paginating evaluation records.
 */

import type { SearchOptions, SearchResult, ScoredResult } from './searchTypes'
import { buildSearchDocument } from './searchIndexer'
import { rankDocument } from './searchRanker'
import { applySearchFilters } from './searchFilters'

export class SearchEngine {
  /**
   * Primary entry point for global search.
   * Runs the complete pipeline: Indexing -> Ranking -> Filtering -> Sorting -> Pagination.
   */
  public search<T extends object>(options: SearchOptions<T>): SearchResult<T> {
    const {
      items = [],
      query = '',
      filters,
      sort,
      pagination,
      documentExtractor,
    } = options

    if (!items || items.length === 0) {
      return {
        items: [],
        scoredItems: [],
        total: 0,
        page: 1,
        pageSize: pagination?.pageSize || 50,
        totalPages: 0,
        query,
        hasMore: false,
      }
    }

    // 1. Build Index & Calculate Ranking Scores
    let scoredItems: ScoredResult<T>[] = items.map((item) => {
      const doc = buildSearchDocument(item, documentExtractor)
      return rankDocument(item, doc, query)
    })

    // 2. Remove items with 0 match score (when query is present)
    if (query?.trim()) {
      scoredItems = scoredItems.filter((entry) => entry.score > 0)
    }

    // 3. Apply Filters
    scoredItems = applySearchFilters(scoredItems, filters)

    // 4. Sort Results
    scoredItems = this.sortResults(scoredItems, sort, Boolean(query?.trim()))

    // 5. Paginate Results
    const page = Math.max(1, pagination?.page || 1)
    const pageSize = Math.max(1, pagination?.pageSize || items.length || 50)
    const total = scoredItems.length
    const totalPages = Math.ceil(total / pageSize) || 1

    const startIndex = (page - 1) * pageSize
    const paginatedScoredItems = scoredItems.slice(startIndex, startIndex + pageSize)
    const paginatedItems = paginatedScoredItems.map((entry) => entry.item)

    return {
      items: paginatedItems,
      scoredItems: paginatedScoredItems,
      total,
      page,
      pageSize,
      totalPages,
      query,
      hasMore: page < totalPages,
    }
  }

  /**
   * Sorts scored results deterministically based on sort options or relevance score.
   */
  private sortResults<T>(
    items: ScoredResult<T>[],
    sort?: SearchOptions['sort'],
    hasQuery?: boolean
  ): ScoredResult<T>[] {
    const sorted = [...items]

    if (sort?.field) {
      const { field, order = 'asc' } = sort
      const mult = order === 'asc' ? 1 : -1

      sorted.sort((a, b) => {
        let valA: any = (a.doc as any)[field] ?? (a.item as any)[field]
        let valB: any = (b.doc as any)[field] ?? (b.item as any)[field]

        if (valA === valB) return 0
        if (valA === null || valA === undefined) return 1
        if (valB === null || valB === undefined) return -1

        if (typeof valA === 'string') {
          return valA.localeCompare(valB) * mult
        }
        return (valA < valB ? -1 : 1) * mult
      })
    } else if (hasQuery) {
      // Default: Sort by relevance score descending
      sorted.sort((a, b) => b.score - a.score)
    }

    return sorted
  }
}

/** Singleton instance export for searchEngine.search() usage */
export const searchEngine = new SearchEngine()
