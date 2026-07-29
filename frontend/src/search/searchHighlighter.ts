/**
 * Search Highlighter Module for Veridict Global Search Engine.
 * Responsible ONLY for generating match text fragments without string mutation.
 */

import type { HighlightFragment } from './searchTypes'
import { normalizeQuery } from './searchNormalizer'
import { escapeRegexString } from './searchUtils'

/**
 * Splits input text into fragments of matching and non-matching text segments.
 */
export function getHighlightFragments(
  text?: string | null,
  query?: string | null
): HighlightFragment[] {
  if (!text) return []

  const normalizedQuery = normalizeQuery(query)
  if (!normalizedQuery) {
    return [{ text, isMatch: false }]
  }

  const escapedQuery = escapeRegexString(normalizedQuery)
  if (!escapedQuery) {
    return [{ text, isMatch: false }]
  }

  const regex = new RegExp(`(${escapedQuery})`, 'gi')
  const parts = text.split(regex)

  return parts.map((part) => {
    const isMatch = part.toLowerCase() === normalizedQuery
    return {
      text: part,
      isMatch,
    }
  })
}
