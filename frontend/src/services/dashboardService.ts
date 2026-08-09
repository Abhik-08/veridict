import { api } from './api'
import type { HistoryItemResponse } from './historyService'

export interface DashboardStatistics {
  total_evaluations: number
  total_batch_jobs: number
  pass_count: number
  needs_improvement_count: number
  fail_count: number
  pass_percentage: number
  fail_percentage?: number
  needs_improvement_percentage?: number
  average_score: number
  highest_score?: number
  lowest_score?: number
  average_batch_size: number
  recent_activity_count: number
  most_recent_evaluation?: string | null
}

export interface VerdictDistribution {
  pass_count: number
  needs_improvement_count: number
  fail_count: number
  pass_percentage: number
  needs_improvement_percentage: number
  fail_percentage: number
}

export interface AverageDimensionScores {
  average_relevance: number
  average_accuracy: number
  average_completeness: number
  average_overall_score: number
  relevance?: number
  accuracy?: number
  completeness?: number
  overall_score?: number
}

export interface HallucinationMetrics {
  evaluable_count: number
  insufficient_evidence_count: number
  hallucinated_count: number
  grounded_count: number
  hallucination_rate_percentage: number
  average_hallucination_score: number
  missing_evidence_count?: number
  insufficient_evidence?: number
}

export interface QualityTrendPoint {
  date: string
  count: number
  average_score: number
  pass_count: number
  needs_improvement_count: number
  fail_count: number
}

export interface AvailableFilterMetadata {
  available_models: string[]
  available_source_types: string[]
  available_verdicts: string[]
}

export interface AnalyticsStatistics {
  total_evaluations: number
  verdict_distribution: VerdictDistribution
  average_scores: AverageDimensionScores
  hallucination_metrics: HallucinationMetrics
  quality_trends: QualityTrendPoint[]
  available_filters: AvailableFilterMetadata
}

export interface AnalyticsFilterParams {
  date_from?: string
  date_to?: string
  source_type?: string
  verdict?: string
  model?: string
}

export const dashboardService = {
  async getDashboardStats(): Promise<DashboardStatistics> {
    const response = await api.get<DashboardStatistics>('/history/stats')
    return response.data
  },

  async getRecentHistory(limit = 10): Promise<HistoryItemResponse[]> {
    const response = await api.get<HistoryItemResponse[]>('/history/recent', {
      params: { limit },
    })
    return response.data
  },

  async getAnalytics(params?: AnalyticsFilterParams): Promise<AnalyticsStatistics> {
    const cleanParams: Record<string, any> = {}
    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== '' && val !== 'ALL') {
          cleanParams[key] = val
        }
      })
    }
    const response = await api.get<AnalyticsStatistics>('/history/analytics', { params: cleanParams })
    return response.data
  },
}
