import { useState } from 'react'
import type { SyntheticEvent } from 'react'
import {
  SectionContainer,
  GlowButton,
  GlassCard,
  TextArea,
  FileInput,
  EvaluationResult,
} from '@/components'
import { BatchEvaluationDashboard } from '@/components/BatchEvaluation/BatchEvaluationDashboard'
import { ToastContainer, type ToastMessage } from '@/components/Toast'
import { useMounted } from '@/hooks'
import { useEvaluation } from '@/context/EvaluationContext'
import { cn } from '@/utils'
import { ArrowRight, RefreshCw, Loader2, UserCheck, Layers, Upload, Play, BarChart2, Download } from 'lucide-react'
import { evaluateResponse } from '@/services/evaluationService'

export function HomePage() {
  const mounted = useMounted()
  const {
    engineMode,
    setEngineMode,
    singleState,
    updateSingleState,
    clearSingleState,
  } = useEvaluation()

  const [toasts, setToasts] = useState<ToastMessage[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [isEvaluating, setIsEvaluating] = useState(false)
  const [errors, setErrors] = useState<{
    question?: string
    response?: string
  }>({})

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }

  const addToast = (type: ToastMessage['type'], title: string, message?: string) => {
    const id = typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}`
    setToasts((prev) => [...prev, { id, type, title, message }])
    setTimeout(() => dismissToast(id), 4000)
  }

  // Single Evaluation Form Handlers
  const handleEvaluate = async (e: SyntheticEvent) => {
    e.preventDefault()
    if (isEvaluating) return

    const newErrors: {
      question?: string
      response?: string
    } = {}

    if (!singleState.question.trim()) {
      newErrors.question = 'Question is required.'
    }
    if (!singleState.response.trim()) {
      newErrors.response = 'AI Generated Response is required.'
    }

    setErrors(newErrors)
    if (Object.keys(newErrors).length > 0) return

    setIsEvaluating(true)
    addToast('info', 'Evaluation Started', 'Submitting QA pair to multi-agent pipeline...')

    try {
      const result = await evaluateResponse({
        question: singleState.question,
        aiResponse: singleState.response,
        referenceAnswer: singleState.reference,
        file,
      })

      updateSingleState({ evaluationResult: result })

      const score = result.overall_score ?? result.verdict_evaluation?.overall_score ?? 0
      const verdict = result.verdict ?? result.verdict_evaluation?.verdict ?? 'COMPLETED'
      addToast('success', 'Evaluation Complete', `Verdict: ${verdict} (${typeof score === 'number' ? score.toFixed(2) : score})`)
    } catch (error: any) {
      console.error('Evaluation failed:', error)
      addToast('error', 'Evaluation Failed', error.message || 'Could not connect to backend server.')
    } finally {
      setIsEvaluating(false)
    }
  }

  const handleReset = () => {
    if (isEvaluating) return
    setFile(null)
    setErrors({})
    clearSingleState()
    addToast('info', 'Form Cleared')
  }

  // Workflow steps
  const steps = [
    { num: '①', label: 'Upload Files', icon: Upload },
    { num: '②', label: 'Run Evaluation', icon: Play },
    { num: '③', label: 'Review Results', icon: BarChart2 },
    { num: '④', label: 'Export Reports', icon: Download },
  ]

  return (
    <div className="flex flex-col items-center w-full pb-16">
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />

      {/* Hero Section — Minimal, Compact, Product-First */}
      <section className="relative flex flex-col items-center justify-center pt-4 pb-2 overflow-hidden w-full">
        <SectionContainer
          className={cn(
            'flex flex-col items-center text-center',
            mounted ? 'animate-fade-in-up' : 'opacity-0'
          )}
        >
          <h1 className="font-display text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-white">
            AI Response Quality Evaluator
          </h1>

          <p className="mt-1 text-xs sm:text-sm text-slate-400 max-w-xl leading-relaxed font-normal">
            Multi-agent evaluation engine for AI responses grounded in RAG evidence.
          </p>

          {/* Engine Mode Switcher Bar */}
          <div className="mt-3.5 flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/90 border border-slate-800 shadow-md">
            <button
              onClick={() => setEngineMode('single')}
              className={cn(
                'flex items-center gap-2 px-4 py-1.5 rounded-lg font-medium text-xs transition-all duration-150',
                engineMode === 'single'
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              )}
            >
              <UserCheck size={14} />
              Single Evaluation
            </button>
            <button
              onClick={() => setEngineMode('batch')}
              className={cn(
                'flex items-center gap-2 px-4 py-1.5 rounded-lg font-medium text-xs transition-all duration-150',
                engineMode === 'batch'
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              )}
            >
              <Layers size={14} />
              Batch Evaluation
            </button>
          </div>

          {/* Workflow Stepper Bar */}
          <div className="mt-3 flex items-center justify-center gap-2 text-[11px] text-slate-500 font-medium opacity-80">
            {steps.map((step, idx) => {
              const IconComp = step.icon
              return (
                <div key={step.label} className="flex items-center gap-1.5">
                  <span className="flex items-center gap-1">
                    <IconComp size={11} className="text-slate-400" />
                    <span>{step.num} {step.label}</span>
                  </span>
                  {idx < steps.length - 1 && <span className="text-slate-600 font-sans">→</span>}
                </div>
              )
            })}
          </div>
        </SectionContainer>
      </section>

      {/* Engine 1: Single Evaluation Pipeline */}
      {engineMode === 'single' && (
        <>
          <section className="relative pb-6 w-full z-10">
            <SectionContainer width="narrow">
              <GlassCard
                padding="lg"
                static
                className="relative overflow-hidden border border-border/80 shadow-glow-sm"
              >
                <div className="mb-4">
                  <h2 className="font-display text-lg font-bold text-text-primary">
                    Single Response Evaluation
                  </h2>
                  <p className="text-xs text-muted mt-0.5">
                    Submit a prompt, AI response, and optional reference material to evaluate quality across 4 dimensions.
                  </p>
                </div>

                <form onSubmit={handleEvaluate} className="space-y-4">
                  <TextArea
                    id="question"
                    label="Question / Prompt"
                    required
                    value={singleState.question}
                    onChange={(e) => {
                      updateSingleState({ question: e.target.value })
                      if (errors.question) {
                        setErrors((prev) => ({
                          ...prev,
                          question: undefined,
                        }))
                      }
                    }}
                    error={errors.question}
                    placeholder="Enter the prompt or question asked to the AI..."
                    disabled={isEvaluating}
                  />

                  <TextArea
                    id="response"
                    label="AI Generated Response"
                    required
                    rows={4}
                    value={singleState.response}
                    onChange={(e) => {
                      updateSingleState({ response: e.target.value })
                      if (errors.response) {
                        setErrors((prev) => ({
                          ...prev,
                          response: undefined,
                        }))
                      }
                    }}
                    error={errors.response}
                    placeholder="Paste the output response to be evaluated..."
                    disabled={isEvaluating}
                  />

                  <TextArea
                    id="reference"
                    label="Reference Answer"
                    optional
                    rows={2}
                    value={singleState.reference}
                    onChange={(e) => updateSingleState({ reference: e.target.value })}
                    placeholder="Provide the expected ground-truth correct answer..."
                    disabled={isEvaluating}
                  />

                  <FileInput
                    id="file-upload"
                    label="Source PDF Document"
                    file={file}
                    onChange={(newFile) => {
                      setFile(newFile)
                      updateSingleState({
                        fileMetadata: newFile ? { name: newFile.name, size: newFile.size, type: newFile.type } : null,
                      })
                    }}
                    maxSizeMB={10}
                  />

                  {singleState.fileMetadata && !file && (
                    <div className="text-[11px] text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-md flex items-center justify-between">
                      <span>Restored file context: <strong>{singleState.fileMetadata.name}</strong></span>
                      <button
                        type="button"
                        onClick={() => updateSingleState({ fileMetadata: null })}
                        className="text-slate-400 hover:text-white underline ml-2"
                      >
                        Remove
                      </button>
                    </div>
                  )}

                  <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-3 border-t border-border/80">
                    <GlowButton
                      type="submit"
                      disabled={isEvaluating}
                      className="w-full sm:w-auto px-8 py-2.5 text-xs font-semibold"
                    >
                      {isEvaluating ? (
                        <>
                          <Loader2
                            size={14}
                            className="animate-spin text-background"
                          />
                          Evaluating...
                        </>
                      ) : (
                        <>
                          Run Evaluation
                          <ArrowRight size={14} />
                        </>
                      )}
                    </GlowButton>

                    <button
                      type="button"
                      onClick={handleReset}
                      disabled={isEvaluating}
                      className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2.5 border border-border hover:border-border-hover rounded-full text-xs font-medium text-muted hover:text-text-primary transition-all duration-150 disabled:opacity-50 disabled:pointer-events-none"
                    >
                      <RefreshCw
                        size={13}
                        className={cn(isEvaluating && 'animate-spin')}
                      />
                      Reset Form
                    </button>
                  </div>
                </form>
              </GlassCard>
            </SectionContainer>
          </section>

          {singleState.evaluationResult !== null && (
            <EvaluationResult result={singleState.evaluationResult} />
          )}
        </>
      )}

      {/* Engine 2: Batch Evaluation Module */}
      {engineMode === 'batch' && (
        <section className="relative w-full z-10">
          <BatchEvaluationDashboard onToast={addToast} />
        </section>
      )}
    </div>
  )
}