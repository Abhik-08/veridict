import { cn } from '@/utils'

interface BlobConfig {
  variant: 'primary' | 'accent' | 'subtle'
  size: number
  top?: string
  left?: string
  right?: string
  bottom?: string
  delay?: string
}

interface GradientBlobsProps {
  blobs?: BlobConfig[]
  className?: string
}

const defaultBlobs: BlobConfig[] = [
  { variant: 'primary', size: 500, top: '-10%', left: '-5%', delay: '0s' },
  { variant: 'accent', size: 400, top: '20%', right: '-8%', delay: '2s' },
  { variant: 'subtle', size: 600, bottom: '-15%', left: '30%', delay: '4s' },
]

const variantClass: Record<string, string> = {
  primary: 'gradient-blob-primary',
  accent: 'gradient-blob-accent',
  subtle: 'gradient-blob-subtle',
}

export function GradientBlobs({ blobs = defaultBlobs, className }: GradientBlobsProps) {
  return (
    <div className={cn('pointer-events-none fixed inset-0 z-0 overflow-hidden', className)} aria-hidden="true">
      {blobs.map((blob, i) => (
        <div
          key={i}
          className={cn('gradient-blob', variantClass[blob.variant])}
          style={{
            width: blob.size,
            height: blob.size,
            top: blob.top,
            left: blob.left,
            right: blob.right,
            bottom: blob.bottom,
            animationDelay: blob.delay,
          }}
        />
      ))}
    </div>
  )
}
