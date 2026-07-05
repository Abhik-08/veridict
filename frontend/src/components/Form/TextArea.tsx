import React from 'react'
import { cn } from '@/utils'
import { AlertCircle } from 'lucide-react'

interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string
  error?: string
  required?: boolean
  optional?: boolean
}

export const TextArea = React.forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ label, id, error, required, optional, className, rows = 4, ...props }, ref) => {
    return (
      <div className="flex flex-col gap-2 w-full group">
        <div className="flex justify-between items-center">
          <label htmlFor={id} className="text-xs font-semibold tracking-wider uppercase text-text-secondary group-focus-within:text-primary transition-colors duration-300">
            {label} {required && <span className="text-primary">*</span>}
          </label>
          {optional && <span className="text-[10px] text-muted-foreground uppercase tracking-widest">Optional</span>}
        </div>
        <textarea
          id={id}
          ref={ref}
          rows={rows}
          className={cn(
            "w-full px-4 py-3 bg-background/40 border rounded-xl text-sm text-text-primary placeholder:text-muted/50 transition-all duration-300 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary focus:shadow-glow-sm resize-y",
            error 
              ? "border-error/85 focus:ring-error focus:border-error" 
              : "border-border hover:border-border-hover/120 focus:bg-background/60",
            className
          )}
          {...props}
        />
        {error && (
          <span className="text-xs text-error flex items-center gap-1 mt-0.5 animate-fade-in">
            <AlertCircle size={12} /> {error}
          </span>
        )}
      </div>
    )
  }
)

TextArea.displayName = 'TextArea'
