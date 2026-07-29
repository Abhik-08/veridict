import React from 'react'

interface HighlightMatchProps {
  text?: string | null
  query?: string | null
  className?: string
}

/**
 * Renders text with search query substrings subtly highlighted.
 * Preserves original text case while performing case-insensitive matching.
 */
export const HighlightMatch: React.FC<HighlightMatchProps> = ({
  text,
  query,
  className = '',
}) => {
  if (!text) return null
  if (!query?.trim()) {
    return <span className={className}>{text}</span>
  }

  const normalizedQuery = query.trim().replaceAll(/\s+/g, ' ').toLowerCase()
  if (!normalizedQuery) return <span className={className}>{text}</span>

  // Escape special regex characters in search query safely
  const escapedQuery = normalizedQuery.replace(/[.*+?^${}()|[\]\\]/g, (char) => String.fromCodePoint(92) + char)
  const regex = new RegExp(`(${escapedQuery})`, 'gi')
  const parts = text.split(regex)

  return (
    <span className={className}>
      {parts.map((part, index) => {
        const isMatch = part.toLowerCase() === normalizedQuery
        const key = `hl-${index}-${part.slice(0, 8)}`
        return isMatch ? (
          <mark
            key={key}
            className="bg-amber-500/25 text-amber-200 font-semibold px-0.5 rounded border border-amber-500/40"
          >
            {part}
          </mark>
        ) : (
          <React.Fragment key={key}>{part}</React.Fragment>
        )
      })}
    </span>
  )
}
