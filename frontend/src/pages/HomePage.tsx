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
import { ArrowRight, RefreshCw, Loader2, UserCheck, Layers, Upload, Play, BarChart2, Download, Bot } from 'lucide-react'
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

    try {
      const result = await evaluateResponse({
        question: singleState.question,
        aiResponse: singleState.response,
        referenceAnswer: singleState.reference,
        file,
      })

      updateSingleState({ evaluationResult: result })
      // No success toast — evaluation results display directly inline below form
    } catch (error: any) {
      console.error('Evaluation failed:', error)
      addToast('error', 'Evaluation Failed', error.message || 'Evaluation failed. Please try again.')
    } finally {
      setIsEvaluating(false)
    }
  }

  const handleReset = () => {
    if (isEvaluating) return
    setFile(null)
    setErrors({})
    clearSingleState()
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
          <p className="mt-2 text-sm text-slate-300 max-w-xl leading-relaxed">
            Multi-agent evaluation platform detecting hallucinations, measuring factual accuracy, and verifying RAG compliance.
          </p>

          {/* Engine Mode Toggle Bar */}
          <div className="mt-4 p-1 rounded-2xl bg-slate-900/90 border border-slate-800 flex items-center gap-1 shadow-xl">
            <button
              type="button"
              onClick={() => setEngineMode('single')}
              className={cn(
                'flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold transition-all duration-200 cursor-pointer',
                engineMode === 'single'
                  ? 'bg-amber-500 text-slate-950 shadow-md scale-105'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              )}
            >
              <UserCheck className="w-4 h-4" />
              <span>Single Prompt Evaluator</span>
            </button>
            <button
              type="button"
              onClick={() => setEngineMode('batch')}
              className={cn(
                'flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold transition-all duration-200 cursor-pointer',
                engineMode === 'batch'
                  ? 'bg-amber-500 text-slate-950 shadow-md scale-105'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              )}
            >
              <Layers className="w-4 h-4" />
              <span>Batch Dataset Evaluator</span>
            </button>
          </div>

          {/* Workflow Steps Indicator Bar */}
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2 w-full max-w-3xl px-2">
            {steps.map((step) => {
              const Icon = step.icon
              return (
                <div
                  key={step.num}
                  className="flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-sm text-[11px] font-semibold text-slate-300 shadow-sm"
                >
                  <Icon className="w-3.5 h-3.5 text-amber-400" />
                  <span>{step.label}</span>
                </div>
              )
            })}
          </div>
        </SectionContainer>
      </section>

      {/* Engine 1: Single Prompt Evaluation Form */}
      {engineMode === 'single' && (
        <>
          <section className="relative w-full z-10 pt-2">
            <SectionContainer width="narrow">
              <GlassCard padding="lg" static className="border border-border/80 shadow-glow-sm">
                <div className="flex items-center justify-between border-b border-border/80 pb-4 mb-6">
                  <div>
                    <h2 className="font-display text-base font-bold text-text-primary">
                      Evaluation Request
                    </h2>
                    <p className="text-xs text-muted mt-0.5">
                      Submit AI output and optional context for multi-agent evaluation
                    </p>
                  </div>
                  <span className="text-[11px] font-medium text-primary px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
                    Active Session
                  </span>
                </div>

                <form onSubmit={handleEvaluate} className="flex flex-col gap-5">
                  <TextArea
                    id="question"
                    label="Question / Prompt"
                    required
                    rows={3}
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
                    disabled={isEvaluating}
                  />

                  {singleState.fileMetadata && !file && (
                    <div className="text-[11px] text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-md flex items-center justify-between">
                      <span>Restored file context: <strong>{singleState.fileMetadata.name}</strong></span>
                      <button
                        type="button"
                        onClick={() => updateSingleState({ fileMetadata: null })}
                        disabled={isEvaluating}
                        className="text-slate-400 hover:text-white underline ml-2 disabled:opacity-50"
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
                      className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2.5 border border-border hover:border-border-hover rounded-full text-xs font-medium text-muted hover:text-text-primary transition-all duration-150 disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
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

          {/* Inline Loading / Progress Panel */}
          {isEvaluating && (
            <SectionContainer width="narrow" className="mt-4 w-full animate-fade-in-up">
              <GlassCard padding="lg" static className="border border-amber-500/30 bg-slate-950/80 backdrop-blur-md flex flex-col gap-4 shadow-xl">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                    <Bot className="w-5 h-5 animate-pulse" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                      Evaluating Response...
                    </h3>
                    <p className="text-xs text-slate-400">
                      Running multi-agent assessment pipeline
                    </p>
                  </div>
                </div>

                <div className="space-y-2 text-xs text-slate-300 font-medium pl-2">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                    <span>Retrieving reference knowledge & RAG evidence</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                    <span>Running relevance analysis</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                    <span>Running accuracy analysis</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                    <span>Checking hallucinations</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                    <span>Generating final verdict</span>
                  </div>
                </div>
              </GlassCard>
            </SectionContainer>
          )}

          {singleState.evaluationResult !== null && !isEvaluating && (
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