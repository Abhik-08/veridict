import type { BaseComponentProps } from '@/types'
import { cn } from '@/utils'

type Width = 'default' | 'narrow' | 'wide'

interface SectionContainerProps extends BaseComponentProps {
  width?: Width
}

const widthClass: Record<Width, string> = {
  default: 'section-container',
  narrow: 'section-container-narrow',
  wide: 'section-container-wide',
}

export function SectionContainer({
  children,
  className,
  width = 'default',
}: Readonly<SectionContainerProps>) {
  return (
    <div className={cn(widthClass[width], className)}>
      {children}
    </div>
  )
}
