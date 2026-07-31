/**
 * Search Indexer Module for Veridict Global Search Engine.
 * Pre-computes searchable text and cached index entries per document.
 */

import type { EvaluationSearchDocument } from './searchTypes'
import { normalizeText } from './searchNormalizer'
import { defaultDocumentExtractor } from './searchUtils'

const _documentIndexCache = new WeakMap<object, EvaluationSearchDocument>()

/**
 * Builds or retrieves a cached index entry for a given evaluation item.
 * Combines all searchable fields into a single normalized pre-computed string.
 */
export function buildSearchDocument<T extends object>(
  item: T,
  extractor?: (item: T) => EvaluationSearchDocument
): EvaluationSearchDocument {
  if (item && _documentIndexCache.has(item)) {
    return _documentIndexCache.get(item)!
  }

  const doc = extractor ? extractor(item) : defaultDocumentExtractor(item)

  const overallStr = doc.overallScore !== null && doc.overallScore !== undefined ? doc.overallScore.toFixed(2) : ''
  const verdictStr = doc.verdict ? doc.verdict.replaceAll('_', ' ') : ''

  const fieldsToCombine = [
    doc.question,
    doc.aiResponse,
    doc.referenceAnswer,
    doc.evidenceText,
    doc.evidenceSource,
    doc.reasoning,
    doc.accuracyReasoning,
    doc.relevanceReasoning,
    doc.completenessReasoning,
    doc.hallucinationReasoning,
    doc.verdict,
    verdictStr,
    doc.id,
    doc.batchId,
    doc.filename,
    overallStr,
    doc.formattedDate,
  ].filter(Boolean)

  const searchableText = normalizeText(fieldsToCombine.join(' '))
  const indexedDoc: EvaluationSearchDocument = {
    ...doc,
    searchableText,
  }

  if (item && typeof item === 'object') {
    _documentIndexCache.set(item, indexedDoc)
  }

  return indexedDoc
}

/**
 * Clears the index cache if memory cleanup is requested.
 */
export function clearIndexCache(): void {
  // WeakMap garbage collects automatically when items are freed
}
