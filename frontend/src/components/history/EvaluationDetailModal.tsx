import { useEffect } from 'react'
import { X, Calendar, ShieldCheck, AlertTriangle, XCircle, FileText, CheckCircle2 } from 'lucide-react'
import type { EvaluationDetailResponse } from '@/services/historyService'
import { SkeletonDetailModal } from '../shared/SkeletonLoader'

interface EvaluationDetailModalProps {
  isOpen: boolean
  onClose: () => void
  detail: EvaluationDetailResponse | null
  loading: boolean
}

export function EvaluationDetailModal({
  isOpen,
  onClose,
  detail,
  loading,
}: Readonly<EvaluationDetailModalProps>) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  const getVerdictBadge = (verdict?: string) => {
    if (!verdict) return null
    switch (verdict.toUpperCase()) {
      case 'PASS':
        return (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-bold">
            <CheckCircle2 className="w-4 h-4" />
            <span>PASS</span>
          </div>
        )
      case 'NEEDS_IMPROVEMENT':
        return (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-400 text-xs font-bold">
            <AlertTriangle className="w-4 h-4" />
            <span>NEEDS IMPROVEMENT</span>
          </div>
        )
      case 'FAIL':
        return (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/15 border border-rose-500/30 text-rose-400 text-xs font-bold">
            <XCircle className="w-4 h-4" />
            <span>FAIL</span>
          </div>
        )
      default:
        return (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-xs font-bold">
            <span>{verdict}</span>
          </div>
        )
    }
  }

  const formatDate = (isoString?: string) => {
    if (!isoString) return '-'
    try {
      return new Date(isoString).toLocaleString()
    } catch {
      return isoString
    }
  }

  const renderModalBody = () => {
    if (loading) {
      return <SkeletonDetailModal />
    }

    if (!detail) {
      return (
        <div className="text-center py-12 text-slate-500">
          Evaluation details could not be loaded.
        </div>
      )
    }

    return (
      <>
        {/* Top Overview Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
              Verdict
            </span>
            <div className="mt-1.5">{getVerdictBadge(detail.verdict)}</div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
              Overall Score
            </span>
            <div className="mt-1 flex items-baseline gap-1">
              <span className="text-xl font-black text-amber-400">
                {detail.overall_score !== undefined ? detail.overall_score.toFixed(1) : '-'}
              </span>
              <span className="text-xs text-slate-500 font-semibold">/ 5.0</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
              Confidence
            </span>
            <div className="mt-1 text-xl font-bold text-slate-200">
              {detail.confidence !== undefined && detail.confidence !== null
                ? `${(detail.confidence * 100).toFixed(0)}%`
                : '-'}
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
              Date Evaluated
            </span>
            <div className="mt-1 text-xs text-slate-300 font-medium flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <span>{formatDate(detail.created_at)}</span>
            </div>
          </div>
        </div>

        {/* Question / Prompt Section */}
        <div className="space-y-1.5">
          <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Question / Prompt
          </h4>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800/90 text-slate-200 leading-relaxed font-medium whitespace-pre-wrap">
            {detail.question}
          </div>
        </div>

        {/* AI Response Section */}
        <div className="space-y-1.5">
          <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            AI Generated Response
          </h4>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800/90 text-slate-200 leading-relaxed whitespace-pre-wrap max-h-56 overflow-y-auto">
            {detail.ai_response}
          </div>
        </div>

        {/* Reference Answer Section */}
        {detail.reference_answer && (
          <div className="space-y-1.5">
            <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Reference Answer (Ground Truth)
            </h4>
            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-slate-300 leading-relaxed whitespace-pre-wrap">
              {detail.reference_answer}
            </div>
          </div>
        )}

        {/* RAG Evidence Section */}
        {detail.retrieved_evidence && (
          <div className="space-y-1.5">
            <h4 className="text-[11px] font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5" />
              <span>Retrieved RAG Evidence</span>
            </h4>
            <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800/90 max-h-48 overflow-y-auto text-slate-300 font-mono text-[11px]">
              <pre className="whitespace-pre-wrap">
                {typeof detail.retrieved_evidence === 'string'
                  ? detail.retrieved_evidence
                  : JSON.stringify(detail.retrieved_evidence, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Judge Reports Payload */}
        {detail.evaluation_result && (
          <div className="space-y-1.5">
            <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Multi-Agent Evaluation Payload
            </h4>
            <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800/90 max-h-56 overflow-y-auto font-mono text-[11px] text-slate-400">
              <pre className="whitespace-pre-wrap">
                {JSON.stringify(detail.evaluation_result, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop overlay */}
      <button
        type="button"
        aria-label="Close modal backdrop"
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md border-0 cursor-default animate-fade-in w-full h-full"
        onClick={onClose}
      />

      {/* Modal Container */}
      <div className="relative z-10 w-full max-w-3xl max-h-[85vh] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">
                Evaluation Details
              </h2>
              <p className="text-xs text-slate-400">
                Full multi-agent inspection report & RAG evidence breakdown
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
            title="Close modal"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-xs text-slate-300">
          {renderModalBody()}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-3.5 border-t border-slate-800 bg-slate-900/90">
          <div className="text-[11px] text-slate-500 font-mono">ID: {detail?.id}</div>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
