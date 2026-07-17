import { GlassCard } from './GlassCard'
import { SectionContainer } from './SectionContainer'
import { FileText, Database, Cpu, Target, CheckCircle } from 'lucide-react'

export interface RetrievedChunk {
  id: string
  score?: number
  source: string
  document_id: string
  chunk_index: number
  question?: string
  answer?: string
  text: string
  filename?: string | null
  page_number?: number | null
  chunk_character_count?: number | null
  created_at?: string | null
  namespace?: string | null
  preview?: string | null
}

export interface RelevanceEvaluation {
  relevance_score: number
  reasoning: string
  model_used: string
}

export interface AccuracyEvaluation {
  accuracy_score: number
  reasoning: string
  model_used: string
}

export interface EvaluationResultData {
  question: string
  ai_response: string
  reference_answer?: string | null
  retrieved_chunks: RetrievedChunk[]
  pdf_namespace?: string | null
  pdf_status?: string | null
  relevance_evaluation?: RelevanceEvaluation | null
  accuracy_evaluation?: AccuracyEvaluation | null
}

interface EvaluationResultProps {
  result: EvaluationResultData | null
}

export function EvaluationResult({ result }: Readonly<EvaluationResultProps>) {
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
  } = result

  // Helper to safely slice text for preview fallback
  const getPreviewText = (chunk: RetrievedChunk): string => {
    if (chunk.preview) {
      return chunk.preview
    }
    const cleanText = chunk.text.trim()
    return cleanText.length > 250 ? `${cleanText.slice(0, 250)}...` : cleanText
  }

  // Get status color styling
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

  // Get relevance score label and styling
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

  // Get accuracy score label and styling
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

  return (
    <SectionContainer width="narrow" className="mt-12 w-full animate-fade-in-up">
      <GlassCard padding="lg" static className="border border-border/80 shadow-glow-sm flex flex-col gap-8">
        
        {/* Title Header */}
        <div>
          <h2 className="font-display text-2xl font-bold text-text-primary flex items-center gap-2">
            <Cpu size={24} className="text-primary" />
            Evaluation Result
          </h2>
          <p className="text-sm text-muted mt-1.5">
            Retrieved knowledge used during semantic retrieval.
          </p>
        </div>
        {/* SECTION: Evaluation Metrics */}
        <div className="flex flex-col gap-4 border-t border-border/80 pt-6">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">
            Evaluation Metrics
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Relevance Card */}
            <GlassCard padding="md" static className="border border-border/60 bg-background/25 flex flex-col justify-between gap-4">
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-text-primary flex items-center gap-1.5">
                    <Target size={16} className="text-primary" />
                    Relevance
                  </h4>
                  {relevance_evaluation ? (
                    <span className={`text-[10px] font-semibold border rounded-full px-2.5 py-0.5 uppercase ${getRelevanceLabel(relevance_evaluation.relevance_score).colorClass}`}>
                      {getRelevanceLabel(relevance_evaluation.relevance_score).text}
                    </span>
                  ) : (
                    <span className="text-[10px] font-semibold border border-muted/30 bg-muted/10 text-muted px-2.5 py-0.5 rounded-full uppercase">
                      Unavailable
                    </span>
                  )}
                </div>

                <div className="flex items-baseline gap-1 mt-1">
                  {relevance_evaluation ? (
                    <>
                      <span className="text-4xl font-display font-bold text-text-primary">
                        {relevance_evaluation.relevance_score}
                      </span>
                      <span className="text-sm text-muted">/ 5</span>
                    </>
                  ) : (
                    <span className="text-3xl font-display font-bold text-muted">—</span>
                  )}
                </div>

                <p className="text-xs text-text-secondary leading-relaxed font-light mt-1">
                  {relevance_evaluation 
                    ? relevance_evaluation.reasoning 
                    : "Relevance evaluation temporarily unavailable."}
                </p>
              </div>

              <div className="flex items-center justify-between border-t border-border/20 pt-3">
                <span className="text-[9px] uppercase tracking-wider font-semibold text-muted">
                  Judge Model
                </span>
                <span className="text-[10px] font-mono text-muted bg-background/40 px-2 py-0.5 rounded border border-border/30 truncate max-w-[150px]">
                  {relevance_evaluation ? relevance_evaluation.model_used : "N/A"}
                </span>
              </div>
            </GlassCard>

            {/* Accuracy Card */}
            <GlassCard padding="md" static className="border border-border/60 bg-background/25 flex flex-col justify-between gap-4">
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-text-primary flex items-center gap-1.5">
                    <CheckCircle size={16} className="text-primary" />
                    Accuracy
                  </h4>
                  {accuracy_evaluation ? (
                    <span className={`text-[10px] font-semibold border rounded-full px-2.5 py-0.5 uppercase ${getAccuracyLabel(accuracy_evaluation.accuracy_score).colorClass}`}>
                      {getAccuracyLabel(accuracy_evaluation.accuracy_score).text}
                    </span>
                  ) : (
                    <span className="text-[10px] font-semibold border border-muted/30 bg-muted/10 text-muted px-2.5 py-0.5 rounded-full uppercase">
                      Unavailable
                    </span>
                  )}
                </div>

                <div className="flex items-baseline gap-1 mt-1">
                  {accuracy_evaluation ? (
                    <>
                      <span className="text-4xl font-display font-bold text-text-primary">
                        {accuracy_evaluation.accuracy_score}
                      </span>
                      <span className="text-sm text-muted">/ 5</span>
                    </>
                  ) : (
                    <span className="text-3xl font-display font-bold text-muted">—</span>
                  )}
                </div>

                <p className="text-xs text-text-secondary leading-relaxed font-light mt-1">
                  {accuracy_evaluation 
                    ? accuracy_evaluation.reasoning 
                    : "Accuracy evaluation temporarily unavailable."}
                </p>
              </div>

              <div className="flex items-center justify-between border-t border-border/20 pt-3">
                <span className="text-[9px] uppercase tracking-wider font-semibold text-muted">
                  Judge Model
                </span>
                <span className="text-[10px] font-mono text-muted bg-background/40 px-2 py-0.5 rounded border border-border/30 truncate max-w-[150px]">
                  {accuracy_evaluation ? accuracy_evaluation.model_used : "N/A"}
                </span>
              </div>
            </GlassCard>
          </div>
        </div>

        {/* SECTION 1: Submission Summary */}
        <div className="flex flex-col gap-4 border-t border-border/80 pt-6">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">
            Submission Summary
          </h3>
          <div className="flex flex-col gap-4 bg-background/25 border border-border/40 p-5 rounded-2xl">
            <div className="flex flex-col gap-1">
              <span className="text-[10px] uppercase font-bold tracking-widest text-muted">Question</span>
              <p className="text-sm text-text-primary leading-relaxed font-light">{question}</p>
            </div>
            <div className="flex flex-col gap-1 border-t border-border/20 pt-3">
              <span className="text-[10px] uppercase font-bold tracking-widest text-muted">AI Response</span>
              <p className="text-sm text-text-secondary leading-relaxed font-light">{ai_response}</p>
            </div>
            <div className="flex flex-col gap-1 border-t border-border/20 pt-3">
              <span className="text-[10px] uppercase font-bold tracking-widest text-muted">Reference Answer</span>
              <p className="text-sm text-text-secondary leading-relaxed font-light">
                {reference_answer ? (
                  <span className="text-text-primary font-normal">{reference_answer}</span>
                ) : (
                  <span className="text-muted-foreground italic font-light">Not Provided</span>
                )}
              </p>
            </div>
          </div>
        </div>

        {/* SECTION 3: Uploaded PDF Status (Render before chunks if enqueued) */}
        {pdf_namespace && (
          <div className="flex flex-col gap-4 border-t border-border/80 pt-6">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">
              Uploaded PDF Namespace
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <GlassCard padding="sm" static className="border border-border/50 bg-background/20 flex flex-col gap-1.5">
                <span className="text-[10px] uppercase font-bold tracking-widest text-muted">Namespace</span>
                <span className="text-xs font-mono text-text-primary truncate">{pdf_namespace}</span>
              </GlassCard>
              <GlassCard padding="sm" static className="border border-border/50 bg-background/20 flex flex-col gap-1.5">
                <span className="text-[10px] uppercase font-bold tracking-widest text-muted">Status</span>
                <div className="flex items-center gap-1.5">
                  <span className={`text-[10px] uppercase tracking-wider font-semibold border rounded-full px-2.5 py-0.5 ${getStatusBadgeClass(pdf_status || 'Pending')}`}>
                    {pdf_status || 'Pending'}
                  </span>
                </div>
              </GlassCard>
            </div>
          </div>
        )}

        {/* SECTION 2: Retrieved Context */}
        <div className="flex flex-col gap-4 border-t border-border/80 pt-6">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">
            Retrieved Context
          </h3>

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
                  className="border border-border/60 hover:border-border/90 bg-background/25 flex flex-col gap-4 transition-all duration-300"
                >
                  {/* Card Header (Index, Score, Source) */}
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
                      {/* Similarity Badge */}
                      {chunk.score !== undefined && (
                        <span className="text-[10px] font-semibold border border-primary/20 bg-primary-muted text-primary px-2.5 py-0.5 rounded-full">
                          Similarity {chunk.score.toFixed(4)}
                        </span>
                      )}
                      {/* Source badge */}
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

                  {/* Chunk Text Preview */}
                  <div className="flex flex-col gap-1.5 border-t border-border/20 pt-3">
                    <span className="text-[10px] uppercase font-bold tracking-widest text-muted">Preview</span>
                    <p className="text-sm text-text-secondary leading-relaxed font-light">
                      {getPreviewText(chunk)}
                    </p>
                  </div>

                  {/* Chunk Metadata Grid */}
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

      </GlassCard>
    </SectionContainer>
  )
}
