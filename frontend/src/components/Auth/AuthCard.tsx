import React from 'react'

interface AuthCardProps {
  title: string
  subtitle?: string
  children: React.ReactNode
  footer?: React.ReactNode
}

export const AuthCard: React.FC<AuthCardProps> = ({ title, subtitle, children, footer }) => {
  return (
    <div className="w-full max-w-[420px] p-7 rounded-2xl glass-card border border-slate-800/90 bg-slate-900/80 shadow-2xl backdrop-blur-xl space-y-5">
      <div className="space-y-1.5 text-center">
        <h1 className="text-xl font-display font-extrabold text-white tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-slate-400 leading-relaxed">{subtitle}</p>}
      </div>

      {children}

      {footer && <div className="pt-4 border-t border-slate-800/80 text-center text-xs text-slate-400">{footer}</div>}
    </div>
  )
}
