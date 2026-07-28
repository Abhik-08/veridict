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
