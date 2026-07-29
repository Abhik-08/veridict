/**
 * Search Ranker Module for Veridict Global Search Engine.
 * Responsible for relevance scoring and multi-token search ranking.
 */

import type { EvaluationSearchDocument, ScoredResult } from './searchTypes'
import { normalizeQuery, normalizeText } from './searchNormalizer'
import { tokenizeText } from './searchUtils'

function _calculateFieldScores(doc: EvaluationSearchDocument, query: string): number {
  let score = 0

  const question = normalizeText(doc.question)
  const aiResponse = normalizeText(doc.aiResponse)
  const reference = normalizeText(doc.referenceAnswer)
  const evidence = normalizeText(doc.evidenceText)
  const reasoning = normalizeText(`${doc.reasoning || ''} ${doc.accuracyReasoning || ''} ${doc.relevanceReasoning || ''}`)
  const verdict = normalizeText(doc.verdict)
  const filename = normalizeText(doc.filename)
  const date = normalizeText(doc.formattedDate)
  const id = normalizeText(doc.id)

  if (question === query) {
    score += 100
  } else if (question.includes(query)) {
    score += 90
  }

  if (aiResponse.includes(query)) score += 80
  if (reference?.includes(query)) score += 70
  if (evidence?.includes(query)) score += 60
  if (reasoning?.includes(query)) score += 50
  if (verdict?.includes(query)) score += 40
  if (filename?.includes(query)) score += 30
  if (date?.includes(query) || id?.includes(query)) score += 20

  return score
}

function _calculateTokenBonuses(doc: EvaluationSearchDocument, queryTokens: string[]): number {
  let bonus = 0
  const question = normalizeText(doc.question)
  const aiResponse = normalizeText(doc.aiResponse)
  const reasoning = normalizeText(doc.reasoning)
  const verdict = normalizeText(doc.verdict)

  queryTokens.forEach((token) => {
    if (question.includes(token)) bonus += 15
    if (aiResponse.includes(token)) bonus += 10
    if (verdict.includes(token)) bonus += 8
    if (reasoning.includes(token)) bonus += 5
  })

  return bonus
}

/**
 * Calculates a weighted relevance score for a search document against a normalized query.
 * Returns 0 if document does not match the query requirements.
 */
export function rankDocument<T>(
  item: T,
  doc: EvaluationSearchDocument,
  rawQuery: string
): ScoredResult<T> {
  const normalizedQuery = normalizeQuery(rawQuery)

  if (!normalizedQuery) {
    return { item, doc, score: 1 }
  }

  const queryTokens = tokenizeText(normalizedQuery)
  const searchableText = doc.searchableText || normalizeText(`${doc.question} ${doc.aiResponse} ${doc.reasoning}`)

  // Require every query token to be present in searchableText (Multi-token match)
  const allTokensPresent = queryTokens.every((token) => searchableText.includes(token))
  if (!allTokensPresent) {
    return { item, doc, score: 0 }
  }

  const score = _calculateFieldScores(doc, normalizedQuery) + _calculateTokenBonuses(doc, queryTokens)
  return { item, doc, score }
}
