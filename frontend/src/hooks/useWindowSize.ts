import { useState, useEffect } from 'react'

interface WindowSize {
  width: number
  height: number
}

/**
 * Track the current viewport dimensions.
 * Debounced with a 150ms delay to avoid excessive re-renders.
 */
export function useWindowSize(): WindowSize {
  const [size, setSize] = useState<WindowSize>({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  })

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>

    const handleResize = () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        setSize({ width: window.innerWidth, height: window.innerHeight })
      }, 150)
    }

    window.addEventListener('resize', handleResize)
    return () => {
      clearTimeout(timeoutId)
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return size
}
