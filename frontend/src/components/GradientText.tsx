import type { BaseComponentProps } from '@/types'
import { cn } from '@/utils'

type Tag = 'span' | 'h1' | 'h2' | 'h3' | 'h4' | 'p'
type Variant = 'default' | 'white' | 'cool'

interface GradientTextProps extends BaseComponentProps {
  as?: Tag
  variant?: Variant
}

const variantClass: Record<Variant, string> = {
  default: 'gradient-text',
  white: 'gradient-text-white',
  cool: 'gradient-text-cool',
}

export function GradientText({
  children,
  className,
  as: Tag = 'span',
  variant = 'default',
}: GradientTextProps) {
  return (
    <Tag className={cn(variantClass[variant], className)}>
      {children}
    </Tag>
  )
}
