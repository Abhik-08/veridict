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
  average_confidence: number
  highest_score?: number
  lowest_score?: number
  average_batch_size: number
  recent_activity_count: number
  most_recent_evaluation?: string | null
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
}
