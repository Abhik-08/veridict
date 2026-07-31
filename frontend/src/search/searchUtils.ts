/**
 * Search Utilities Module for Veridict Global Search Engine.
 * Reusable helper utilities for tokenization, regex escaping, and field formatting.
 */

import type { EvaluationSearchDocument } from './searchTypes'

/**
 * Tokenizes normalized text into an array of distinct non-empty tokens.
 */
export function tokenizeText(normalizedText: string): string[] {
  if (!normalizedText) return []
  return Array.from(new Set(normalizedText.split(' ').filter(Boolean)))
}

/**
 * Safely escapes special regular expression characters in search strings.
 */
export function escapeRegexString(str: string): string {
  if (!str) return ''
  return str.replaceAll(/[.*+?^${}()|[\]\\]/g, (char) => String.fromCodePoint(92) + char)
}

/**
 * Safely formats date input into searchable string formats (ISO, locale date, YYYY-MM-DD).
 */
export function formatSearchableDate(dateInput?: string | Date | null): string {
  if (!dateInput) return ''
  try {
    const dateObj = typeof dateInput === 'string' ? new Date(dateInput) : dateInput
    if (Number.isNaN(dateObj.getTime())) return String(dateInput)
    const iso = dateObj.toISOString()
    const locale = dateObj.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
    return `${iso} ${locale}`.toLowerCase()
  } catch {
    return String(dateInput)
  }
}

/**
 * Default document extractor converts generic evaluation records or BatchItemEvaluationResult into EvaluationSearchDocument.
 */
export function defaultDocumentExtractor(item: any): EvaluationSearchDocument {
  if (!item) {
    return { id: '', question: '', aiResponse: '' }
  }

  const id = item.id || item.batch_id || ''
  const question = item.question || ''
  const aiResponse = item.ai_response || item.answer || item.aiResponse || ''
  const referenceAnswer = item.reference_answer || item.referenceAnswer || null
  const evidenceText = item.evidence_text || item.evidenceText || item.retrieved_chunks?.[0]?.text || null
  const evidenceSource = item.evidence_source || item.evidenceSource || null
  const reasoning = item.reasoning || item.verdict_evaluation?.reasoning || null
  const verdict = item.verdict || item.verdict_evaluation?.verdict || null

  const overallScore = item.overall_score ?? item.overallScore ?? item.verdict_evaluation?.overall_score ?? null
  const accuracyScore = item.accuracy_score ?? item.accuracyScore ?? item.accuracy_evaluation?.accuracy_score ?? null
  const relevanceScore = item.relevance_score ?? item.relevanceScore ?? item.relevance_evaluation?.relevance_score ?? null
  const completenessScore = item.completeness_score ?? item.completenessScore ?? item.completeness_evaluation?.completeness_score ?? null
  const hallucinationScore = item.hallucination_score ?? item.hallucinationScore ?? item.hallucination_evaluation?.hallucination_score ?? null

  const filename = item.filename || item.batchFileMetadata?.name || null
  const createdAt = item.created_at || item.createdAt || null

  return {
    id: String(id),
    batchId: item.batch_id ? String(item.batch_id) : null,
    filename: filename ? String(filename) : null,
    question,
    aiResponse,
    referenceAnswer,
    evidenceText,
    evidenceSource: evidenceSource ? String(evidenceSource) : null,
    reasoning,
    verdict,
    overallScore,
    accuracyScore,
    relevanceScore,
    completenessScore,
    hallucinationScore,
    createdAt,
    formattedDate: formatSearchableDate(createdAt),
  }
}
