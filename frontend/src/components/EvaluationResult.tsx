import { useState } from 'react'
import { GlassCard } from './GlassCard'
import { SectionContainer } from './SectionContainer'
import {
  FileText,
  Database,
  Cpu,
  Target,
  BadgeCheck,
  ShieldCheck,
  ListChecks,
  Award,
  BookOpen,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Check,
  X,
  Layers,
  Sparkles
} from 'lucide-react'
import type {
  EvaluationResultData,
  RetrievedChunk,
  RelevanceEvaluation,
  AccuracyEvaluation,
  HallucinationEvaluation,
  CompletenessEvaluation,
  VerdictEvaluation
} from '../types'
import { exportEvaluationPDF } from '../services/evaluationService'

interface EvaluationResultProps {
  result: EvaluationResultData | null
}

// ──────────────────────────────────────────────
// Helper Formatting Functions
// ──────────────────────────────────────────────
const getPreviewText = (chunk: RetrievedChunk): string => {
  if (chunk.preview) {
    return chunk.preview
  }
  const cleanText = chunk.text.trim()
  return cleanText.length > 250 ? `${cleanText.slice(0, 250)}...` : cleanText
}

const getStatusBadgeClass = (status: string) => {
  const s = status.toLowerCase()
  if (s === 'completed') {
    return 'bg-success/15 border-success/30 text-success'
  }
  if (s === 'processing' || s === 'pending') {
    return 'bg-warning/15 border-warning/30 text-warning animate-pulse'
  }
  return 'bg-error/15 border-error/30 text-error'
}

const getRelevanceLabel = (score: number) => {
  switch (score) {
    case 5:
      return { text: 'Highly Relevant', colorClass: 'bg-success/15 border-success/30 text-success' }
    case 4:
      return { text: 'Mostly Relevant', colorClass: 'bg-success/10 border-success/20 text-success/90' }
    case 3:
      return { text: 'Partially Relevant', colorClass: 'bg-warning/15 border-warning/30 text-warning' }
    case 2:
      return { text: 'Mostly Irrelevant', colorClass: 'bg-warning/10 border-warning/20 text-warning/90' }
    case 1:
      return { text: 'Irrelevant', colorClass: 'bg-error/15 border-error/30 text-error' }
    default:
      return { text: 'Unknown', colorClass: 'bg-muted/15 border-muted/30 text-muted' }
  }
}

const getAccuracyLabel = (score: number) => {
  switch (score) {
    case 5:
      return { text: 'Highly Accurate', colorClass: 'bg-success/15 border-success/30 text-success' }
    case 4:
      return { text: 'Mostly Accurate', colorClass: 'bg-success/10 border-success/20 text-success/90' }
    case 3:
      return { text: 'Partially Accurate', colorClass: 'bg-warning/15 border-warning/30 text-warning' }
    case 2:
      return { text: 'Mostly Inaccurate', colorClass: 'bg-warning/10 border-warning/20 text-warning/90' }
    case 1:
      return { text: 'Inaccurate', colorClass: 'bg-error/15 border-error/30 text-error' }
    default:
      return { text: 'Unknown', colorClass: 'bg-muted/15 border-muted/30 text-muted' }
  }
}

const isInsufficientEvidence = (eval_data: HallucinationEvaluation | null | undefined): boolean => {
  return eval_data?.status === 'INSUFFICIENT_EVIDENCE'
}

const getHallucinationLabel = (score: number) => {
  switch (score) {
    case 5:
      return { text: 'Fully Grounded', colorClass: 'bg-success/15 border-success/30 text-success' }
    case 4:
      return { text: 'Mostly Grounded', colorClass: 'bg-success/10 border-success/20 text-success/90' }
    case 3:
      return { text: 'Partially Grounded', colorClass: 'bg-warning/15 border-warning/30 text-warning' }
    case 2:
      return { text: 'Mostly Hallucinated', colorClass: 'bg-warning/10 border-warning/20 text-warning/90' }
    case 1:
      return { text: 'Highly Hallucinated', colorClass: 'bg-error/15 border-error/30 text-error' }
    default:
      return { text: 'Unknown', colorClass: 'bg-muted/15 border-muted/30 text-muted' }
  }
}

const getCompletenessLabel = (score: number) => {
  switch (score) {
    case 5:
      return { text: 'Complete', colorClass: 'bg-success/15 border-success/30 text-success' }
    case 4:
      return { text: 'Mostly Complete', colorClass: 'bg-success/10 border-success/20 text-success/90' }
    case 3:
      return { text: 'Partially Complete', colorClass: 'bg-warning/15 border-warning/30 text-warning' }
    case 2:
      return { text: 'Mostly Incomplete', colorClass: 'bg-warning/10 border-warning/20 text-warning/90' }
    case 1:
      return { text: 'Incomplete', colorClass: 'bg-error/15 border-error/30 text-error' }
    default:
      return { text: 'Unknown', colorClass: 'bg-muted/15 border-muted/30 text-muted' }
  }
}

const getVerdictBadge = (verdict: string) => {
  switch (verdict) {
    case 'PASS':
      return { label: 'PASS', colorClass: 'bg-success/15 border-success/30 text-success' }
    case 'NEEDS_IMPROVEMENT':
      return { label: 'NEEDS IMPROVEMENT', colorClass: 'bg-warning/15 border-warning/30 text-warning' }
    case 'FAIL':
      return { label: 'FAIL', colorClass: 'bg-error/15 border-error/30 text-error' }
    default:
      return { label: verdict, colorClass: 'bg-muted/15 border-muted/30 text-muted' }
  }
}

// ──────────────────────────────────────────────
// Reusable Component: Export PDF Button (SINGLE BUTTON)
// ──────────────────────────────────────────────
function ExportPDFButton({ result }: Readonly<{ result: EvaluationResultData }>) {
  const [isExporting, setIsExporting] = useState(false)

  const handleExportPDF = async () => {
    try {
      setIsExporting(true)
      await exportEvaluationPDF(result)
    } catch (err) {
      console.error("PDF export failed:", err)
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <button
      type="button"
      onClick={handleExportPDF}
      disabled={isExporting}
      className="flex items-center gap-2 text-xs font-bold px-3 sm:px-4 py-2 rounded-xl border border-primary/40 bg-primary text-white hover:bg-primary-hover disabled:opacity-50 transition-all shadow-sm cursor-pointer min-h-[38px]"
    >
      <FileText size={15} className="shrink-0" />
      {isExporting ? (
        <span>Generating PDF...</span>
      ) : (
        <>
          <span className="hidden sm:inline">Export AI Evaluation Report (PDF)</span>
          <span className="sm:hidden">Export PDF Report</span>
        </>
      )}
    </button>
  )
}

// ──────────────────────────────────────────────
// Reusable Component: Collapsible Reasoning
// ──────────────────────────────────────────────
function CollapsibleReasoning({ text }: Readonly<{ text: string }>) {
  const [expanded, setExpanded] = useState(false)
  const isLong = text.length > 180

  return (
    <div className="flex flex-col gap-1">
      <p className="text-xs text-text-secondary leading-relaxed font-light">
        {isLong && !expanded ? `${text.slice(0, 180)}...` : text}
      </p>
      {isLong && (
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="text-[10px] font-semibold text-primary hover:underline flex items-center gap-0.5 mt-1 self-start"
        >
          {expanded ? 'Show Less' : 'Show More'}
          {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>
      )}
    </div>
  )
}

// ──────────────────────────────────────────────
// Reusable Component: Evidence Source Chips
// ──────────────────────────────────────────────
function EvidenceChips({
  hasReference,
  hasEvidence,
  pdfNamespace
}: Readonly<{
  hasReference: boolean
  hasEvidence: boolean
  pdfNamespace?: string | null
}>) {
  return (
    <div className="flex flex-wrap items-center gap-1.5 mt-1">
      {hasReference && (
        <span className="text-[10px] font-semibold border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 px-2.5 py-0.5 rounded-full flex items-center gap-1">
          <BookOpen size={11} /> Reference Answer
        </span>
      )}
      {hasEvidence && (
        <span className="text-[10px] font-semibold border border-teal-500/30 bg-teal-500/10 text-teal-400 px-2.5 py-0.5 rounded-full flex items-center gap-1">
          <Database size={11} /> Knowledge Base
        </span>
      )}
      {pdfNamespace && (
        <span className="text-[10px] font-semibold border border-amber-500/30 bg-amber-500/10 text-amber-400 px-2.5 py-0.5 rounded-full flex items-center gap-1">
          <FileText size={11} /> PDF Document
        </span>
      )}
      {!hasReference && !hasEvidence && !pdfNamespace && (
        <span className="text-[10px] font-semibold border border-muted/30 bg-muted/10 text-muted px-2.5 py-0.5 rounded-full">
          Standalone Prompt
        </span>
      )}
    </div>
  )
}

// ──────────────────────────────────────────────
// Sub-Component: Collapsible Evaluation Input Panel
// ──────────────────────────────────────────────
function EvaluationInputPanel({
  question,
  aiResponse,
  referenceAnswer,
  pdfNamespace,
  pdfStatus,
  chunkCount
}: Readonly<{
  question?: string
  aiResponse?: string
  referenceAnswer?: string | null
  pdfNamespace?: string | null
  pdfStatus?: string | null
  chunkCount: number
}>) {
  const [isExpanded, setIsExpanded] = useState(true)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setIsExpanded(!isExpanded)
    }
  }

  const hasRef = Boolean(referenceAnswer?.trim())
  const hasPdf = Boolean(pdfNamespace)

  return (
    <div className="flex flex-col border border-border/60 bg-background/35 rounded-2xl overflow-hidden shadow-sm transition-all duration-300">
      {/* Accordion Header Button */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        onKeyDown={handleKeyDown}
        aria-expanded={isExpanded}
        className="w-full flex items-center justify-between p-4 bg-background/50 hover:bg-background/70 border-b border-border/40 transition-colors text-left focus:outline-none focus:ring-2 focus:ring-primary/50"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
            <FileText size={18} />
          </div>
          <div>
            <h3 className="text-base font-display font-bold text-text-primary flex items-center gap-2">
              Evaluation Input
            </h3>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xs text-muted font-light">
                Question
              </span>
              <span className="text-muted text-[10px]">•</span>
              <span className={`text-[10px] font-mono font-semibold flex items-center gap-0.5 ${hasRef ? 'text-success' : 'text-muted'}`}>
                Reference {hasRef ? <Check size={10} /> : <X size={10} />}
              </span>
              <span className="text-muted text-[10px]">•</span>
              <span className={`text-[10px] font-mono font-semibold flex items-center gap-0.5 ${hasPdf ? 'text-success' : 'text-muted'}`}>
                PDF {hasPdf ? <Check size={10} /> : <X size={10} />}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-text-primary">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted hidden sm:inline">
            {isExpanded ? 'Collapse' : 'Expand'}
          </span>
          {isExpanded ? (
            <ChevronDown size={20} className="text-primary" />
          ) : (
            <ChevronRight size={20} className="text-primary" />
          )}
        </div>
      </button>

      {/* Accordion Content */}
      {isExpanded && (
        <div className="p-6 flex flex-col gap-6 animate-fade-in">
          {/* Question */}
          <div className="flex flex-col gap-2">
            <span className="text-[10px] uppercase font-bold tracking-widest text-muted flex items-center gap-1">
              <FileText size={12} className="text-primary" /> Question
            </span>
            <div className="p-4 bg-background/40 border border-border/40 rounded-xl text-sm text-text-primary leading-relaxed font-light select-text">
              {question || "No question provided."}
            </div>
          </div>

          {/* AI Response (Scrollable if > 300px) */}
          <div className="flex flex-col gap-2">
            <span className="text-[10px] uppercase font-bold tracking-widest text-muted flex items-center gap-1">
              <Cpu size={12} className="text-primary" /> AI Response
            </span>
            <div className="p-4 bg-background/40 border border-border/40 rounded-xl text-sm text-text-secondary leading-relaxed font-light whitespace-pre-wrap max-h-[300px] overflow-y-auto select-text font-sans">
              {aiResponse || "No AI response provided."}
            </div>
          </div>

          {/* Reference Answer & Uploaded PDF Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Reference Answer */}
            <div className="flex flex-col gap-2">
              <span className="text-[10px] uppercase font-bold tracking-widest text-muted flex items-center gap-1">
                <BookOpen size={12} className="text-primary" /> Reference Answer
              </span>
              <div className="p-4 bg-background/40 border border-border/40 rounded-xl text-sm text-text-secondary leading-relaxed font-light h-full select-text flex items-center">
                {referenceAnswer?.trim() ? (
                  <span className="text-text-primary font-normal">{referenceAnswer}</span>
                ) : (
                  <span className="text-muted-foreground italic font-light">
                    No reference answer provided.
                  </span>
                )}
              </div>
            </div>

            {/* Uploaded PDF */}
            <div className="flex flex-col gap-2">
              <span className="text-[10px] uppercase font-bold tracking-widest text-muted flex items-center gap-1">
                <FileText size={12} className="text-primary" /> Uploaded Source Document (PDF)
              </span>
              <div className="p-4 bg-background/40 border border-border/40 rounded-xl text-sm text-text-secondary flex flex-col justify-center gap-2 h-full">
                {pdfNamespace ? (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-semibold text-text-primary truncate max-w-[200px]">
                        {pdfNamespace}
                      </span>
                      <span className={`text-[10px] uppercase tracking-wider font-semibold border rounded-full px-2.5 py-0.5 ${getStatusBadgeClass(pdfStatus || 'Completed')}`}>
                        {pdfStatus || 'Completed'}
                      </span>
                    </div>
                    <span className="text-[11px] text-muted font-mono">
                      {chunkCount} processed {chunkCount === 1 ? 'chunk' : 'chunks'} indexed
                    </span>
                  </>
                ) : (
                  <span className="text-muted-foreground italic font-light">
                    No PDF uploaded.
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ──────────────────────────────────────────────
// Sub-Components: AI Agent Reports (2x2 Grid)
// ──────────────────────────────────────────────
function RelevanceAgentReport({ evalData }: Readonly<{ evalData: RelevanceEvaluation | null | undefined }>) {
  const label = evalData ? getRelevanceLabel(evalData.relevance_score) : null

  return (
    <GlassCard padding="lg" static className="border border-border/60 bg-background/25 flex flex-col justify-between gap-6 hover:border-primary/50 hover:shadow-glow-sm transition-all duration-300">
      <div className="flex flex-col gap-4">
        {/* Report Header */}
        <div className="flex items-center justify-between pb-3 border-b border-border/30">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
              <Target size={18} />
            </div>
            <div>
              <h4 className="text-base font-display font-bold text-text-primary">
                Relevance Agent
              </h4>
              <span className="text-[10px] text-muted tracking-wider uppercase font-semibold">
                Query Intent Alignment
              </span>
            </div>
          </div>
          {label ? (
            <span className={`text-[10px] font-semibold border rounded-full px-3 py-1 uppercase ${label.colorClass}`}>
              {label.text}
            </span>
          ) : (
            <span className="text-[10px] font-semibold border border-muted/30 bg-muted/10 text-muted px-2.5 py-0.5 rounded-full uppercase">
              Unavailable
            </span>
          )}
        </div>

        {/* Score Display */}
        <div className="flex items-baseline gap-1.5 mt-1">
          {evalData ? (
            <>
              <span className="text-5xl font-display font-extrabold text-text-primary tracking-tight">
                {evalData.relevance_score}
              </span>
              <span className="text-base text-muted font-medium">/ 5</span>
            </>
          ) : (
            <span className="text-4xl font-display font-bold text-muted">—</span>
          )}
        </div>

        {/* Reasoning */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] uppercase tracking-wider font-bold text-muted">Analysis Reasoning</span>
          {evalData ? (
            <CollapsibleReasoning text={evalData.reasoning} />
          ) : (
            <p className="text-xs text-text-secondary leading-relaxed font-light">
              Relevance evaluation temporarily unavailable.
            </p>
          )}
        </div>

        {/* Key Findings */}
        <div className="flex flex-col gap-1.5 pt-3 border-t border-border/20">
          <span className="text-[10px] uppercase tracking-wider font-bold text-muted">Key Findings</span>
          <div className="text-xs text-text-secondary font-light bg-background/30 p-2.5 rounded-xl border border-border/30">
            {(() => {
              if (!evalData) return "No findings available."
              return evalData.relevance_score >= 4
                ? "Directly addresses the query intent without topic drift."
                : "Partial alignment with the requested prompt."
            })()}
          </div>
        </div>
      </div>

      {/* Footer Model Info */}
      <div className="flex items-center justify-between border-t border-border/20 pt-3 mt-2">
        <span className="text-[9px] uppercase tracking-wider font-semibold text-muted">
          Agent Model
        </span>
        <span className="text-[10px] font-mono text-muted bg-background/40 px-2.5 py-0.5 rounded-md border border-border/30 truncate max-w-[150px]">
          {evalData ? evalData.model_used : "N/A"}
        </span>
      </div>
    </GlassCard>
  )
}

function AccuracyAgentReport({
  evalData,
  hasReference,
  hasEvidence,
  pdfNamespace
}: Readonly<{
  evalData: AccuracyEvaluation | null | undefined
  hasReference: boolean
  hasEvidence: boolean
  pdfNamespace?: string | null
}>) {
  const label = evalData ? getAccuracyLabel(evalData.accuracy_score) : null

  return (
    <GlassCard padding="lg" static className="border border-border/60 bg-background/25 flex flex-col justify-between gap-6 hover:border-primary/50 hover:shadow-glow-sm transition-all duration-300">
      <div className="flex flex-col gap-4">
        {/* Report Header */}
        <div className="flex items-center justify-between pb-3 border-b border-border/30">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
              <BadgeCheck size={18} />
            </div>
            <div>
              <h4 className="text-base font-display font-bold text-text-primary">
                Accuracy Agent
              </h4>
              <span className="text-[10px] text-muted tracking-wider uppercase font-semibold">
                Factual Correctness
              </span>
            </div>
          </div>
          {label ? (
            <span className={`text-[10px] font-semibold border rounded-full px-3 py-1 uppercase ${label.colorClass}`}>
              {label.text}
            </span>
          ) : (
            <span className="text-[10px] font-semibold border border-muted/30 bg-muted/10 text-muted px-2.5 py-0.5 rounded-full uppercase">
              Unavailable
            </span>
          )}
        </div>

        {/* Score Display */}
        <div className="flex items-baseline gap-1.5 mt-1">
          {evalData ? (
            <>
              <span className="text-5xl font-display font-extrabold text-text-primary tracking-tight">
                {evalData.accuracy_score}
              </span>
              <span className="text-base text-muted font-medium">/ 5</span>
            </>
          ) : (
            <span className="text-4xl font-display font-bold text-muted">—</span>
          )}
        </div>

        {/* Reasoning */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] uppercase tracking-wider font-bold text-muted">Analysis Reasoning</span>
          {evalData ? (
            <CollapsibleReasoning text={evalData.reasoning} />
          ) : (
            <p className="text-xs text-text-secondary leading-relaxed font-light">
              Accuracy evaluation temporarily unavailable.
            </p>
          )}
        </div>

        {/* Evidence Source Chips */}
        <div className="flex flex-col gap-1.5 pt-3 border-t border-border/20">
          <span className="text-[10px] uppercase tracking-wider font-bold text-muted">Evidence Sources</span>
          <EvidenceChips
            hasReference={hasReference}
            hasEvidence={hasEvidence}
            pdfNamespace={pdfNamespace}
          />
        </div>
      </div>

      {/* Footer Model Info */}
      <div className="flex items-center justify-between border-t border-border/20 pt-3 mt-2">
        <span className="text-[9px] uppercase tracking-wider font-semibold text-muted">
          Agent Model
        </span>
        <span className="text-[10px] font-mono text-muted bg-background/40 px-2.5 py-0.5 rounded-md border border-border/30 truncate max-w-[150px]">
          {evalData ? evalData.model_used : "N/A"}
        </span>
      </div>
    </GlassCard>
  )
}

function HallucinationAgentReport({
  evalData,
  hasReference,
  hasEvidence,
  pdfNamespace
}: Readonly<{
  evalData: HallucinationEvaluation | null | undefined
  hasReference: boolean
  hasEvidence: boolean
  pdfNamespace?: string | null
}>) {
  const renderBadge = () => {
    if (!evalData) {
      return (
        <span className="text-[10px] font-semibold border border-muted/30 bg-muted/10 text-muted px-2.5 py-0.5 rounded-full uppercase">
          Unavailable
        </span>
      )
    }
    if (isInsufficientEvidence(evalData)) {
      return (
        <span className="text-[10px] font-semibold border rounded-full px-3 py-1 uppercase bg-muted/15 border-muted/30 text-muted">
          Insufficient Evidence
        </span>
      )
    }
    const label = getHallucinationLabel(evalData.hallucination_score!)
    return (
      <span className={`text-[10px] font-semibold border rounded-full px-3 py-1 uppercase ${label.colorClass}`}>
        {label.text}
      </span>
    )
  }

  const renderScore = () => {
    if (!evalData) {
      return <span className="text-4xl font-display font-bold text-muted">—</span>
    }
    if (isInsufficientEvidence(evalData)) {
      return (
        <span className="text-2xl font-display font-semibold text-muted italic">
          Not Evaluated
        </span>
      )
    }
    return (
      <>
        <span className="text-5xl font-display font-extrabold text-text-primary tracking-tight">
          {evalData.hallucination_score}
        </span>
        <span className="text-base text-muted font-medium">/ 5</span>
      </>
    )
  }

  return (
    <GlassCard padding="lg" static className="border border-border/60 bg-background/25 flex flex-col justify-between gap-6 hover:border-primary/50 hover:shadow-glow-sm transition-all duration-300">
      <div className="flex flex-col gap-4">
        {/* Report Header */}
        <div className="flex items-center justify-between pb-3 border-b border-border/30">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
              <ShieldCheck size={18} />
            </div>
            <div>
              <h4 className="text-base font-display font-bold text-text-primary">
                Hallucination Agent
              </h4>
              <span className="text-[10px] text-muted tracking-wider uppercase font-semibold">
                Contextual Grounding
              </span>
            </div>
          </div>
          {renderBadge()}
        </div>

        {/* Score Display */}
        <div className="flex items-baseline gap-1.5 mt-1">
          {renderScore()}
        </div>

        {/* Reasoning */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] uppercase tracking-wider font-bold text-muted">Analysis Reasoning</span>
          {evalData ? (
            <CollapsibleReasoning text={evalData.reasoning} />
          ) : (
            <p className="text-xs text-text-secondary leading-relaxed font-light">
              Hallucination evaluation temporarily unavailable.
            </p>
          )}
        </div>

        {/* Evidence Source Chips */}
        <div className="flex flex-col gap-1.5 pt-3 border-t border-border/20">
          <span className="text-[10px] uppercase tracking-wider font-bold text-muted">Grounding Evidence</span>
          <EvidenceChips
            hasReference={hasReference}
            hasEvidence={hasEvidence}
            pdfNamespace={pdfNamespace}
          />
        </div>
      </div>

      {/* Footer Model Info */}
      <div className="flex items-center justify-between border-t border-border/20 pt-3 mt-2">
        <span className="text-[9px] uppercase tracking-wider font-semibold text-muted">
          Agent Model
        </span>
        <span className="text-[10px] font-mono text-muted bg-background/40 px-2.5 py-0.5 rounded-md border border-border/30 truncate max-w-[150px]">
          {evalData ? evalData.model_used : "N/A"}
        </span>
      </div>
    </GlassCard>
  )
}

function CompletenessAgentReport({ evalData }: Readonly<{ evalData: CompletenessEvaluation | null | undefined }>) {
  const label = evalData ? getCompletenessLabel(evalData.completeness_score) : null

  return (
    <GlassCard padding="lg" static className="border border-border/60 bg-background/25 flex flex-col justify-between gap-6 hover:border-primary/50 hover:shadow-glow-sm transition-all duration-300">
      <div className="flex flex-col gap-4">
        {/* Report Header */}
        <div className="flex items-center justify-between pb-3 border-b border-border/30">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
              <ListChecks size={18} />
            </div>
            <div>
              <h4 className="text-base font-display font-bold text-text-primary">
                Completeness Agent
              </h4>
              <span className="text-[10px] text-muted tracking-wider uppercase font-semibold">
                Coverage & Requirements
              </span>
            </div>
          </div>
          {label ? (
            <span className={`text-[10px] font-semibold border rounded-full px-3 py-1 uppercase ${label.colorClass}`}>
              {label.text}
            </span>
          ) : (
            <span className="text-[10px] font-semibold border border-muted/30 bg-muted/10 text-muted px-2.5 py-0.5 rounded-full uppercase">
              Unavailable
            </span>
          )}
        </div>

        {/* Score Display */}
        <div className="flex items-baseline gap-1.5 mt-1">
          {evalData ? (
            <>
              <span className="text-5xl font-display font-extrabold text-text-primary tracking-tight">
                {evalData.completeness_score}
              </span>
              <span className="text-base text-muted font-medium">/ 5</span>
            </>
          ) : (
            <span className="text-4xl font-display font-bold text-muted">—</span>
          )}
        </div>

        {/* Reasoning */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] uppercase tracking-wider font-bold text-muted">Analysis Reasoning</span>
          {evalData ? (
            <CollapsibleReasoning text={evalData.reasoning} />
          ) : (
            <p className="text-xs text-text-secondary leading-relaxed font-light">
              Completeness evaluation temporarily unavailable.
            </p>
          )}
        </div>

        {/* Covered & Missing Aspects Breakdown */}
        {evalData && (
          <div className="flex flex-col gap-2.5 pt-3 border-t border-border/20">
            {/* Covered Aspects */}
            <div className="flex flex-col gap-1">
              <span className="text-[10px] uppercase font-bold tracking-wider text-success flex items-center gap-1">
                <Check size={12} /> Covered Aspects
              </span>
              {evalData.covered_aspects && evalData.covered_aspects.length > 0 ? (
                <ul className="list-disc list-inside space-y-0.5">
                  {evalData.covered_aspects.map((aspect, idx) => (
                    <li key={`covered-${aspect.slice(0, 20)}-${idx}`} className="text-[11px] text-text-secondary leading-tight truncate font-light">
                      {aspect}
                    </li>
                  ))}
                </ul>
              ) : (
                <span className="text-[11px] text-muted italic">None identified</span>
              )}
            </div>

            {/* Missing Aspects */}
            <div className="flex flex-col gap-1 mt-1">
              <span className="text-[10px] uppercase font-bold tracking-wider text-error flex items-center gap-1">
                <X size={12} /> Missing Aspects
              </span>
              {evalData.missing_aspects && evalData.missing_aspects.length > 0 ? (
                <ul className="list-disc list-inside space-y-0.5">
                  {evalData.missing_aspects.map((aspect, idx) => (
                    <li key={`missing-${aspect.slice(0, 20)}-${idx}`} className="text-[11px] text-text-secondary leading-tight truncate font-light">
                      {aspect}
                    </li>
                  ))}
                </ul>
              ) : (
                <span className="text-[11px] text-muted italic">None identified</span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer Model Info */}
      <div className="flex items-center justify-between border-t border-border/20 pt-3 mt-2">
        <span className="text-[9px] uppercase tracking-wider font-semibold text-muted">
          Agent Model
        </span>
        <span className="text-[10px] font-mono text-muted bg-background/40 px-2.5 py-0.5 rounded-md border border-border/30 truncate max-w-[150px]">
          {evalData ? evalData.model_used : "N/A"}
        </span>
      </div>
    </GlassCard>
  )
}

// ──────────────────────────────────────────────
// Sub-Component: Full-Width Verdict Panel (CONTAINS SINGLE EXPORT BUTTON)
// ──────────────────────────────────────────────
function VerdictPanel({
  verdictEval,
  chunkCount,
  pdfNamespace,
  fullResult
}: Readonly<{
  verdictEval: VerdictEvaluation
  chunkCount: number
  pdfNamespace?: string | null
  fullResult: EvaluationResultData
}>) {
  const badge = getVerdictBadge(verdictEval.verdict)

  return (
    <GlassCard padding="lg" static className="border border-primary/40 bg-background/30 flex flex-col gap-6 relative overflow-hidden shadow-glow-sm">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-border/40">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-primary/15 border border-primary/30 text-primary">
            <Award size={24} />
          </div>
          <div>
            <h3 className="font-display text-xl font-bold text-text-primary flex items-center gap-2">
              Final Evaluation Verdict
              <Sparkles size={16} className="text-primary animate-pulse" />
            </h3>
            <span className="text-xs text-muted font-light">
              Deterministically aggregated overall verdict & synthesized summary
            </span>
          </div>
        </div>

        {/* SINGLE EXPORT BUTTON IN THE ENTIRE UI */}
        <div className="flex items-center gap-3">
          <ExportPDFButton result={fullResult} />
          <span className={`text-sm font-bold border rounded-full px-4 py-1.5 uppercase tracking-wider ${badge.colorClass}`}>
            {badge.label}
          </span>
        </div>
      </div>

      {/* Score and Reasoning Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
        {/* Overall Score Box */}
        <div className="flex flex-col gap-1 p-6 bg-background/40 border border-border/40 rounded-2xl justify-center items-center lg:items-start text-center lg:text-left">
          <span className="text-[10px] uppercase font-extrabold tracking-widest text-muted">
            Weighted Score
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-6xl font-display font-extrabold text-text-primary tracking-tight">
              {verdictEval.overall_score.toFixed(2)}
            </span>
            <span className="text-lg text-muted font-semibold">/ 5.00</span>
          </div>
        </div>

        {/* Synthesized Reasoning */}
        <div className="lg:col-span-2 flex flex-col gap-2">
          <span className="text-[10px] uppercase font-extrabold tracking-widest text-muted">
            Synthesized Verdict Reasoning
          </span>
          <p className="text-sm text-text-secondary leading-relaxed font-light">
            {verdictEval.reasoning}
          </p>
        </div>
      </div>

      {/* Progress Bars for Dimension Weights */}
      {verdictEval.weights_used && Object.keys(verdictEval.weights_used).length > 0 && (
        <div className="flex flex-col gap-3.5 pt-4 border-t border-border/30">
          <span className="text-[10px] uppercase font-bold tracking-widest text-muted">
            Active Dimension Weight Distribution
          </span>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(verdictEval.weights_used).map(([dim, weight]) => {
              const percent = Math.round(weight * 100)
              return (
                <div key={dim} className="flex flex-col gap-2 bg-background/25 p-3.5 rounded-xl border border-border/30">
                  <div className="flex justify-between items-center text-xs">
                    <span className="capitalize font-semibold text-text-primary">{dim}</span>
                    <span className="font-mono text-xs font-bold text-primary">{percent}%</span>
                  </div>
                  <div className="w-full bg-background/60 rounded-full h-2.5 overflow-hidden border border-border/20">
                    <div
                      className="bg-primary h-2.5 rounded-full transition-all duration-500"
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Meta Specs Footer */}
      <div className="flex flex-wrap items-center justify-between border-t border-border/30 pt-4 text-xs text-muted gap-3">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5 font-mono text-[11px]">
            <Layers size={14} className="text-primary" />
            {chunkCount} Evidence {chunkCount === 1 ? 'Chunk' : 'Chunks'}
          </span>
          {pdfNamespace && (
            <span className="flex items-center gap-1.5 font-mono text-[11px] truncate max-w-[200px]">
              <FileText size={14} className="text-primary" />
              PDF: {pdfNamespace}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] uppercase font-bold text-muted">Synthesizer Model</span>
          <span className="text-[10px] font-mono text-muted bg-background/40 px-2.5 py-0.5 rounded-md border border-border/30">
            {verdictEval.model_used}
          </span>
        </div>
      </div>
    </GlassCard>
  )
}

// ──────────────────────────────────────────────
// Main Component
// ──────────────────────────────────────────────
export function EvaluationResult({ result }: Readonly<EvaluationResultProps>) {
  const [showChunks, setShowChunks] = useState(false)

  if (!result) {
    return null
  }

  const {
    question,
    ai_response,
    reference_answer,
    retrieved_chunks,
    pdf_namespace,
    pdf_status,
    relevance_evaluation,
    accuracy_evaluation,
    hallucination_evaluation,
    completeness_evaluation,
    verdict_evaluation,
  } = result

  const hasReference = Boolean(reference_answer?.trim())
  const hasEvidence = retrieved_chunks.length > 0
  const maxSimilarity = retrieved_chunks.length > 0
    ? Math.max(...retrieved_chunks.map((c) => c.score ?? 0))
    : 0

  const badge = verdict_evaluation ? getVerdictBadge(verdict_evaluation.verdict) : null

  return (
    <SectionContainer className="mt-12 w-full animate-fade-in-up relative">
      {/* Sticky Compact Verdict Summary Header on Scroll */}
      {verdict_evaluation && badge && (
        <div className="sticky top-4 z-30 bg-background/90 backdrop-blur-md border border-primary/40 rounded-2xl py-3 px-4 sm:px-6 shadow-glow-sm mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4 transition-all duration-300">
          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
            <Award size={20} className="text-primary shrink-0" />
            <span className="font-display font-bold text-xs sm:text-sm text-text-primary">Verdict Overview:</span>
            <span className={`text-[10px] sm:text-xs font-bold border rounded-full px-2.5 sm:px-3 py-0.5 uppercase tracking-wider ${badge.colorClass}`}>
              {badge.label}
            </span>
          </div>

          <div className="flex items-baseline gap-1 self-end sm:self-auto">
            <span className="text-xl sm:text-2xl font-display font-extrabold text-text-primary tracking-tight">
              {verdict_evaluation.overall_score.toFixed(2)}
            </span>
            <span className="text-xs text-muted font-medium">/ 5.00</span>
          </div>
        </div>
      )}

      <GlassCard padding="lg" static className="border border-border/80 shadow-glow-sm flex flex-col gap-10">

        {/* Dashboard Header */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="font-display text-2xl font-bold text-text-primary flex items-center gap-2.5">
              <Cpu size={26} className="text-primary" />
              AI Evaluation Dashboard
            </h2>
            <p className="text-sm text-muted mt-1.5">
              Comprehensive multi-agent evaluation reports and aggregated verdict.
            </p>
          </div>
        </div>

        {/* SECTION 1: COLLAPSIBLE EVALUATION INPUT PANEL (Staggered Animation 0ms) */}
        <div className="animate-fade-in-up">
          <EvaluationInputPanel
            question={question}
            aiResponse={ai_response}
            referenceAnswer={reference_answer}
            pdfNamespace={pdf_namespace}
            pdfStatus={pdf_status}
            chunkCount={retrieved_chunks.length}
          />
        </div>

        {/* SECTION 2: FULL-WIDTH VERDICT PANEL (Staggered Animation 150ms) */}
        {verdict_evaluation && (
          <div className="flex flex-col gap-4 border-t border-border/80 pt-8 animate-fade-in-up [animation-delay:150ms]">
            <VerdictPanel
              verdictEval={verdict_evaluation}
              chunkCount={retrieved_chunks.length}
              pdfNamespace={pdf_namespace}
              fullResult={result}
            />
          </div>
        )}

        {/* SECTION 3: AI AGENT REPORTS 2x2 Grid (Staggered Animation 300ms) */}
        <div className="flex flex-col gap-4 border-t border-border/80 pt-8 animate-fade-in-up [animation-delay:300ms]">
          <h3 className="text-xs font-bold uppercase tracking-widest text-muted">
            AI Agent Reports
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <RelevanceAgentReport evalData={relevance_evaluation} />
            <AccuracyAgentReport
              evalData={accuracy_evaluation}
              hasReference={hasReference}
              hasEvidence={hasEvidence}
              pdfNamespace={pdf_namespace}
            />
            <HallucinationAgentReport
              evalData={hallucination_evaluation}
              hasReference={hasReference}
              hasEvidence={hasEvidence}
              pdfNamespace={pdf_namespace}
            />
            <CompletenessAgentReport evalData={completeness_evaluation} />
          </div>
        </div>

        {/* SECTION 4: COLLAPSIBLE RETRIEVED CHUNKS (Staggered Animation 450ms) */}
        <div className="flex flex-col gap-4 border-t border-border/80 pt-8 animate-fade-in-up [animation-delay:450ms]">
          <div className="flex items-center justify-between">
            {(() => {
              const chunkWord = retrieved_chunks.length === 1 ? 'Chunk' : 'Chunks'
              const buttonText = showChunks
                ? "Hide Retrieved Evidence"
                : `Show Retrieved Evidence (${retrieved_chunks.length} ${chunkWord})`

              return (
                <button
                  type="button"
                  onClick={() => setShowChunks(!showChunks)}
                  className="flex items-center gap-2 text-sm font-semibold text-text-primary hover:text-primary transition-colors py-2 px-4 rounded-xl border border-border/40 bg-background/30 hover:bg-background/50 shadow-sm"
                >
                  {showChunks ? <ChevronDown size={18} className="text-primary" /> : <ChevronRight size={18} className="text-primary" />}
                  <span>{buttonText}</span>
                </button>
              )
            })()}

            <div className="flex items-center gap-3 text-xs text-muted font-mono">
              <span>
                {retrieved_chunks.length} {retrieved_chunks.length === 1 ? 'chunk' : 'chunks'}
              </span>
              {retrieved_chunks.length > 0 && maxSimilarity > 0 && (
                <span className="hidden sm:inline border-l border-border/40 pl-3 text-primary font-semibold">
                  Highest Similarity: {maxSimilarity.toFixed(4)}
                </span>
              )}
            </div>
          </div>

          {/* Lazy-rendered Expanded Chunks Accordion */}
          {showChunks && (
            <div className="mt-4 flex flex-col gap-4 animate-fade-in">
              {retrieved_chunks.length === 0 ? (
                <div className="text-sm text-muted-foreground italic bg-background/20 border border-border/30 rounded-2xl p-6 text-center">
                  No relevant context found.
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {retrieved_chunks.map((chunk, idx) => (
                    <GlassCard
                      key={chunk.id}
                      padding="md"
                      static
                      className="border border-border/60 hover:border-border/90 hover:shadow-glow-sm bg-background/25 flex flex-col gap-4 transition-all duration-300"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-bold text-primary">
                            Chunk {idx + 1}
                          </span>
                          <span className="text-[10px] text-muted-foreground px-2 py-0.5 bg-background/40 rounded-md border border-border/30">
                            {chunk.id}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono text-muted bg-background/40 px-2 py-0.5 rounded border border-border/30">
                            {chunk.text.length} chars
                          </span>
                          {chunk.score !== undefined && (
                            <span className="text-[10px] font-semibold border border-primary/20 bg-primary-muted text-primary px-2.5 py-0.5 rounded-full">
                              Similarity {chunk.score.toFixed(4)}
                            </span>
                          )}
                          <span className="text-[10px] font-semibold border border-accent/25 bg-accent-muted text-accent px-2.5 py-0.5 rounded-full uppercase flex items-center gap-1">
                            {chunk.source === 'uploaded_pdf' ? (
                              <FileText size={10} />
                            ) : (
                              <Database size={10} />
                            )}
                            {chunk.source}
                          </span>
                        </div>
                      </div>

                      <div className="flex flex-col gap-1.5 border-t border-border/20 pt-3">
                        <span className="text-[10px] uppercase font-bold tracking-widest text-muted">Preview</span>
                        <p className="text-sm text-text-secondary leading-relaxed font-light select-text">
                          {getPreviewText(chunk)}
                        </p>
                      </div>

                      <div className="flex flex-col gap-2 border-t border-border/20 pt-3">
                        <span className="text-[10px] uppercase font-bold tracking-widest text-muted">Metadata</span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 mt-1">
                          {chunk.document_id && (
                            <div className="flex flex-col bg-background/35 px-3 py-2 border border-border/30 rounded-xl">
                              <span className="text-[8px] uppercase tracking-widest text-muted-foreground font-bold">Document ID</span>
                              <span className="text-[10px] font-mono truncate text-text-primary">{chunk.document_id}</span>
                            </div>
                          )}
                          {chunk.page_number !== null && chunk.page_number !== undefined && (
                            <div className="flex flex-col bg-background/35 px-3 py-2 border border-border/30 rounded-xl">
                              <span className="text-[8px] uppercase tracking-widest text-muted-foreground font-bold">Page Number</span>
                              <span className="text-[10px] font-mono text-text-primary">{chunk.page_number}</span>
                            </div>
                          )}
                          {chunk.namespace && (
                            <div className="flex flex-col bg-background/35 px-3 py-2 border border-border/30 rounded-xl">
                              <span className="text-[8px] uppercase tracking-widest text-muted-foreground font-bold">Namespace</span>
                              <span className="text-[10px] font-mono truncate text-text-primary">{chunk.namespace}</span>
                            </div>
                          )}
                          {chunk.filename && (
                            <div className="flex flex-col bg-background/35 px-3 py-2 border border-border/30 rounded-xl col-span-1 sm:col-span-2">
                              <span className="text-[8px] uppercase tracking-widest text-muted-foreground font-bold">Filename</span>
                              <span className="text-[10px] truncate font-mono text-text-primary">{chunk.filename}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </GlassCard>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

      </GlassCard>
    </SectionContainer>
  )
}
