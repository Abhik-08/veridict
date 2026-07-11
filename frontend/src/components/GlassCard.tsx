import type { BaseComponentProps } from '@/types'
import { cn } from '@/utils'

interface GlassCardProps extends BaseComponentProps {
  /** Disable hover lift effect */
  static?: boolean
  /** Padding preset */
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const paddingMap = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

export function GlassCard({
  children,
  className,
  static: isStatic = false,
  padding = 'md',
}: Readonly<GlassCardProps>) {
  return (
    <div
      className={cn(
        isStatic ? 'glass-card-static' : 'glass-card',
        paddingMap[padding],
        className,
      )}
    >
      {children}
    </div>
  )
}
