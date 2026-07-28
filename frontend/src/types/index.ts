/**
 * Global type definitions for Veridict design system.
 */

/** Navigation link shape */
export interface NavLink {
  label: string
  href: string
  icon?: React.ReactNode
}

/** Feature card data */
export interface FeatureItem {
  icon: React.ReactNode
  title: string
  description: string
}

/** Generic component props with className extension */
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

/** Evaluation domain interfaces */
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

export interface HallucinationEvaluation {
  status?: string
  hallucination_score: number | null
  reasoning: string
  model_used: string
}

export interface CompletenessEvaluation {
  completeness_score: number
  reasoning: string
  covered_aspects?: string[]
  missing_aspects?: string[]
  model_used: string
}

export interface VerdictEvaluation {
  overall_score: number
  verdict: 'PASS' | 'NEEDS_IMPROVEMENT' | 'FAIL'
  reasoning: string
  weights_used?: Record<string, number>
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
  hallucination_evaluation?: HallucinationEvaluation | null
  completeness_evaluation?: CompletenessEvaluation | null
  verdict_evaluation?: VerdictEvaluation | null
}

/** Batch Evaluation domain interfaces */
export interface BatchItemEvaluationResult {
  id: string
  row_index: number
  question: string
  ai_response: string
  reference_answer?: string | null
  evidence_text?: string | null
  evidence_source: 'REFERENCE_ANSWER' | 'EVIDENCE_PDF' | 'KNOWLEDGE_BASE' | 'NO_EVIDENCE'
  relevance_score: number
  accuracy_score: number
  hallucination_score: number | null
  completeness_score: number
  confidence: number
  overall_score: number
  verdict: 'PASS' | 'NEEDS_IMPROVEMENT' | 'FAIL'
  reasoning: string
  status: 'COMPLETED' | 'FAILED'
  error_message?: string | null
}

export interface BatchProgress {
  batch_id: string
  filename: string
  file_type: 'CSV' | 'PDF'
  total_rows: number
  processed_rows: number
  remaining_rows: number
  current_batch: number
  total_batches: number
  completed_count: number
  failed_count: number
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  error_message?: string | null
  error?: string | null
  elapsed_seconds?: number | null
  gemini_call_count?: number | null
  statistics?: Record<string, any> | null
  items: BatchItemEvaluationResult[]
}

