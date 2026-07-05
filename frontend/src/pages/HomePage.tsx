import { useState } from 'react'
import type { SyntheticEvent } from 'react'
import {
  SectionContainer,
  GlowButton,
  GradientText,
  GlassCard,
  TextArea,
  FileInput,
} from '@/components'
import { useMounted } from '@/hooks'
import { cn } from '@/utils'
import { ArrowRight, RefreshCw, Loader2 } from 'lucide-react'

export function HomePage() {
  const mounted = useMounted()

  // Form State
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState('')
  const [reference, setReference] = useState('')
  const [file, setFile] = useState<File | null>(null)
  
  // Validation / Interaction States
  const [errors, setErrors] = useState<{ question?: string; response?: string }>({})
  const [isEvaluating, setIsEvaluating] = useState(false)

  // Form Actions
  const handleEvaluate = (e: SyntheticEvent) => {
    e.preventDefault()
    if (isEvaluating) return
    
    // Simple Validation
    const newErrors: { question?: string; response?: string } = {}
    if (!question.trim()) {
      newErrors.question = 'Question is required.'
    }
    if (!response.trim()) {
      newErrors.response = 'AI Generated Response is required.'
    }

    setErrors(newErrors)

    if (Object.keys(newErrors).length === 0) {
      setIsEvaluating(true)
      
      // Present a clean console log
      console.log('Evaluation requested with:', {
        question,
        response,
        reference,
        file: file ? file.name : null,
      })

      // Simulate a loading state for UI presentation
      setTimeout(() => {
        setIsEvaluating(false)
      }, 1500)
    }
  }

  const handleReset = () => {
    if (isEvaluating) return
    setQuestion('')
    setResponse('')
    setReference('')
    setFile(null)
    setErrors({})
  }

  return (
    <div className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center pt-24 pb-12 overflow-hidden w-full">
        {/* Central radial glow — subtle orange behind hero */}
        <div
          className="absolute top-[40%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] rounded-full pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse, rgba(247,147,26,0.06) 0%, rgba(247,147,26,0.02) 40%, transparent 70%)',
          }}
          aria-hidden="true"
        />

        <SectionContainer className={cn(
          'flex flex-col items-center text-center',
          mounted ? 'animate-fade-in-up' : 'opacity-0',
        )}>
          {/* Large title */}
          <h1 className="font-display text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight leading-[1.05]">
            <GradientText variant="cool">Veridict</GradientText>
          </h1>

          {/* Subtitle */}
          <p className="mt-6 text-lg sm:text-xl md:text-2xl text-text-secondary max-w-3xl leading-relaxed font-light">
            Evaluate AI-generated responses using explainable multi-agent analysis
            powered by{' '}
            <span className="text-primary font-medium">Retrieval-Augmented Generation (RAG)</span>.
          </p>

          {/* Short description */}
          <p className="mt-4 text-xs sm:text-sm text-muted max-w-xl leading-relaxed">
            Score accuracy, detect hallucinations, and verify factual grounding — all in one intelligent pipeline.
          </p>
        </SectionContainer>
      </section>

      {/* Evaluation Input Module */}
      <section className="relative pb-24 w-full z-10">
        <SectionContainer width="narrow">
          <GlassCard padding="lg" static className="relative overflow-hidden border border-border/80 shadow-glow-sm">
            {/* Header */}
            <div className="mb-8">
              <h2 className="font-display text-2xl font-bold text-text-primary">
                Evaluate AI Response
              </h2>
              <p className="text-sm text-muted mt-1.5">
                Submit a prompt, AI-generated response, and optional reference material for evaluation.
              </p>
            </div>

            <form onSubmit={handleEvaluate} className="space-y-6">
              {/* Field 1: Question */}
              <TextArea
                id="question"
                label="Question"
                required
                value={question}
                onChange={(e) => {
                  setQuestion(e.target.value)
                  if (errors.question) {
                    setErrors((prev) => ({ ...prev, question: undefined }))
                  }
                }}
                error={errors.question}
                placeholder="Enter the prompt or question asked to the AI..."
                disabled={isEvaluating}
              />

              {/* Field 2: AI Generated Response */}
              <TextArea
                id="response"
                label="AI Generated Response"
                required
                rows={5}
                value={response}
                onChange={(e) => {
                  setResponse(e.target.value)
                  if (errors.response) {
                    setErrors((prev) => ({ ...prev, response: undefined }))
                  }
                }}
                error={errors.response}
                placeholder="Paste the output response to be evaluated..."
                disabled={isEvaluating}
              />

              {/* Field 3: Reference Answer */}
              <TextArea
                id="reference"
                label="Reference Answer"
                optional
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                placeholder="Provide the gold standard or expected correct answer..."
                disabled={isEvaluating}
              />

              {/* Field 4: Source Document (PDF Upload) */}
              <FileInput
                id="file-upload"
                label="Source Document"
                file={file}
                onChange={setFile}
                maxSizeMB={10}
              />

              {/* Actions Section */}
              <div className="flex flex-col sm:flex-row items-center gap-3 pt-4 border-t border-border/80">
                <GlowButton type="submit" disabled={isEvaluating} className="w-full sm:w-auto px-8 py-3">
                  {isEvaluating ? (
                    <>
                      <Loader2 size={16} className="animate-spin text-background" />
                      Evaluating...
                    </>
                  ) : (
                    <>
                      Evaluate Response
                      <ArrowRight size={16} />
                    </>
                  )}
                </GlowButton>
                <button
                  type="button"
                  onClick={handleReset}
                  disabled={isEvaluating}
                  className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 border border-border hover:border-border-hover rounded-full text-sm font-medium text-muted hover:text-text-primary transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none"
                >
                  <RefreshCw size={14} className={cn(isEvaluating && "animate-spin")} />
                  Reset
                </button>
              </div>
            </form>
          </GlassCard>
        </SectionContainer>
      </section>
    </div>
  )
}
