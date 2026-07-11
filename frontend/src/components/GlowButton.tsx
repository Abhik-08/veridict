import type { BaseComponentProps } from '@/types'
import { cn } from '@/utils'

interface GlowButtonProps extends BaseComponentProps {
  onClick?: () => void
  type?: 'button' | 'submit'
  disabled?: boolean
}

export function GlowButton({
  children,
  className,
  onClick,
  type = 'button',
  disabled = false,
}: Readonly<GlowButtonProps>) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'glow-button',
        disabled && 'opacity-50 pointer-events-none',
        className,
      )}
    >
      {children}
    </button>
  )
}
