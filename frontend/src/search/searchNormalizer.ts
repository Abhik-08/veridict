/**
 * Search Normalizer Module for Veridict Global Search Engine.
 * Responsible ONLY for string normalization across queries and documents.
 */

/**
 * Normalizes input text by:
 * 1. Handling null/undefined
 * 2. Lowercasing
 * 3. Trimming
 * 4. Normalizing Unicode (NFD + diacritic strip)
 * 5. Stripping control characters, linebreaks (\r, \n), and tabs (\t)
 * 6. Standardizing curly quotes and special punctuation
 * 7. Collapsing multiple whitespace characters into a single space
 */
export function normalizeText(text?: string | null): string {
  if (!text) return ''

  return text
    .toLowerCase()
    .normalize('NFD')
    .replaceAll(/[\u0300-\u036f]/g, '') // Strip diacritics / accents
    .replaceAll(/[\r\n\t]/g, ' ') // Convert linebreaks & tabs to spaces
    .replaceAll(/[\u201C\u201D]/g, '"') // Standardize double quotes
    .replaceAll(/[\u2018\u2019]/g, "'") // Standardize single quotes
    .replaceAll(/[\u2013\u2014]/g, '-') // Standardize em/en dashes
    .replaceAll(/\s+/g, ' ') // Collapse multiple spaces
    .trim()
}

/**
 * Normalizes search query input for tokenization and ranking.
 */
export function normalizeQuery(query?: string | null): string {
  return normalizeText(query)
}
