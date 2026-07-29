import type { BatchItemEvaluationResult } from '../types'

/**
 * Normalizes search text by trimming whitespace, lowercasing,
 * and collapsing multiple spaces into a single space.
 */
export function normalizeSearchQuery(query: string): string {
  return query.trim().replaceAll(/\s+/g, ' ').toLowerCase()
}

function scoreQuestionMatch(question: string, query: string): number {
  const q = (question || '').toLowerCase()
  if (q === query) return 100
  if (q.startsWith(query)) return 80
  if (q.includes(query)) return 50
  return 0
}

function scoreContentMatches(item: BatchItemEvaluationResult, query: string): number {
  let score = 0

  const aiResponse = item.ai_response?.toLowerCase()
  if (aiResponse?.includes(query)) score += 30

  const referenceAnswer = item.reference_answer?.toLowerCase()
  if (referenceAnswer?.includes(query)) score += 25

  const verdict = item.verdict?.toLowerCase().replaceAll('_', ' ')
  if (verdict?.includes(query) || item.verdict?.toLowerCase().includes(query)) score += 20

  const overallStr = item.overall_score !== undefined ? item.overall_score.toFixed(2) : ''
  const confidenceStr = item.confidence !== undefined ? `${(item.confidence * 100).toFixed(0)}%` : ''
  const id = item.id?.toLowerCase()
  if (overallStr?.includes(query) || confidenceStr?.includes(query) || id?.includes(query)) {
    score += 15
  }

  const reasoning = item.reasoning?.toLowerCase()
  if (reasoning?.includes(query)) score += 10

  const evidenceText = item.evidence_text?.toLowerCase()
  const evidenceSource = item.evidence_source?.toLowerCase()
  if (evidenceText?.includes(query) || evidenceSource?.includes(query)) score += 5

  return score
}

/**
 * Calculates a match score for ranking search results.
 * Score > 0 indicates a match. Higher scores reflect higher relevance.
 */
export function calculateMatchScore(
  item: BatchItemEvaluationResult,
  normalizedQuery: string
): number {
  if (!normalizedQuery) return 1
  return scoreQuestionMatch(item.question, normalizedQuery) + scoreContentMatches(item, normalizedQuery)
}

/**
 * Filter and rank results using deterministic pipeline:
 * Original Results -> Search & Rank -> Verdict Filter
 */
export function filterAndRankBatchItems(
  items: BatchItemEvaluationResult[],
  searchQuery: string,
  verdictFilter: 'ALL' | 'PASS' | 'NEEDS_IMPROVEMENT' | 'FAIL'
): BatchItemEvaluationResult[] {
  if (!items || items.length === 0) return []

  const normalized = normalizeSearchQuery(searchQuery)
  let list = items

  // 1. Search & Rank
  if (normalized) {
    const scoredList = list
      .map((item) => ({ item, score: calculateMatchScore(item, normalized) }))
      .filter((entry) => entry.score > 0)

    // Sort by match score descending (higher relevance first)
    scoredList.sort((a, b) => b.score - a.score)
    list = scoredList.map((entry) => entry.item)
  }

  // 2. Verdict Filter
  if (verdictFilter !== 'ALL') {
    list = list.filter((item) => item.verdict === verdictFilter)
  }

  return list
}
