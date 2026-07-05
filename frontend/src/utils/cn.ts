/**
 * Utility to conditionally join class names.
 * Filters out falsy values and joins with a space.
 *
 * @example
 * cn('base', isActive && 'active', className)
 */
export function cn(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(' ')
}
