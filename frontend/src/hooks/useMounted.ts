import { useState, useEffect } from 'react'

/**
 * Returns true once the component has mounted.
 * Useful for triggering entrance animations after hydration.
 */
export function useMounted(): boolean {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return mounted
}
