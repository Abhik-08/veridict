import React from 'react'
import { Loader2 } from 'lucide-react'

interface LoadingButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'outline'
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  children,
  variant = 'primary',
  className = '',
  disabled,
  ...props
}) => {
  const baseStyle =
    'w-full min-h-[42px] py-2.5 px-4 rounded-lg font-bold text-xs flex items-center justify-center gap-2 transition-all duration-150 shadow-md disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer'

  const variants = {
    primary: 'bg-amber-500 hover:bg-amber-600 active:bg-amber-700 text-slate-950',
    secondary: 'bg-slate-800 hover:bg-slate-700 active:bg-slate-900 text-white border border-slate-700',
    outline: 'bg-transparent hover:bg-slate-800/60 text-slate-300 border border-slate-700 hover:border-slate-500',
  }

  return (
    <button
      type="button"
      disabled={disabled || loading}
      className={`${baseStyle} ${variants[variant]} ${className}`}
      {...props}
    >
      {loading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Processing...</span>
        </>
      ) : (
        children
      )}
    </button>
  )
}
