import React from 'react'
import { CheckCircle2, AlertCircle, Info, XCircle, X } from 'lucide-react'

export interface ToastMessage {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  title: string
  message?: string
}

interface ToastProps {
  toasts: ToastMessage[]
  onDismiss: (id: string) => void
}

const getToastTheme = (type: ToastMessage['type']): string => {
  switch (type) {
    case 'success':
      return 'bg-slate-900/95 border-emerald-500/30 text-slate-100'
    case 'error':
      return 'bg-slate-900/95 border-rose-500/30 text-slate-100'
    case 'warning':
      return 'bg-slate-900/95 border-amber-500/30 text-slate-100'
    case 'info':
    default:
      return 'bg-slate-900/95 border-slate-700 text-slate-100'
  }
}

export const ToastContainer: React.FC<ToastProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null

  return (
    <div
      className="fixed bottom-4 right-3 left-3 sm:left-auto sm:right-5 z-50 flex flex-col gap-2.5 max-w-[calc(100vw-24px)] sm:max-w-sm w-auto pointer-events-none"
      aria-live="polite"
      aria-atomic="true"
    >
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-xl border backdrop-blur-md transition-all duration-300 animate-fade-in-up ${getToastTheme(
            toast.type
          )}`}
        >
          <div className="flex-shrink-0 mt-0.5">
            {toast.type === 'success' && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
            {toast.type === 'error' && <XCircle className="w-5 h-5 text-rose-400" />}
            {toast.type === 'warning' && <AlertCircle className="w-5 h-5 text-amber-400" />}
            {toast.type === 'info' && <Info className="w-5 h-5 text-sky-400" />}
          </div>

          <div className="flex-1 min-w-0">
            <h4 className="text-xs font-semibold text-white tracking-wide">{toast.title}</h4>
            {toast.message && <p className="text-[11px] text-slate-300 mt-0.5 leading-relaxed">{toast.message}</p>}
          </div>

          <button
            onClick={() => onDismiss(toast.id)}
            className="flex-shrink-0 p-1 text-slate-400 hover:text-white rounded-md transition-colors"
            aria-label="Dismiss notification"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  )
}
