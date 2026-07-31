import { api } from './api'

export interface HistoryItemResponse {
  id: string
  user_id: string
  question: string
  ai_response: string
  reference_answer?: string | null
  overall_score: number
  verdict: string
  source_type: string
  batch_job_id?: string | null
  created_at: string
  updated_at: string
}

export interface EvaluationDetailResponse extends HistoryItemResponse {
  retrieved_evidence?: any
  evaluation_result: Record<string, any>
}

export interface BatchHistoryResponse {
  id: string
  user_id: string
  filename: string
  status: string
  total_items: number
  completed_items: number
  average_score?: number
  created_at: string
  updated_at: string
}

export interface BatchDetailResponse extends BatchHistoryResponse {
  evaluations: HistoryItemResponse[]
  verdict_distribution: Record<string, number>
}

export interface PaginationMetadata {
  page: number
  page_size: number
  total_items: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: PaginationMetadata
}

export interface HistoryFilterParams {
  page?: number
  page_size?: number
  search?: string
  verdict?: string
  source_type?: string
  sort_by?: string
  sort_order?: string
  date_from?: string
  date_to?: string
  score_min?: number
  score_max?: number
}

export const historyService = {
  async getHistory(params: HistoryFilterParams = {}): Promise<PaginatedResponse<HistoryItemResponse>> {
    const response = await api.get<PaginatedResponse<HistoryItemResponse>>('/history', {
      params,
    })
    return response.data
  },

  async getEvaluationDetail(id: string): Promise<EvaluationDetailResponse> {
    const response = await api.get<EvaluationDetailResponse>(`/history/${id}`)
    return response.data
  },

  async deleteEvaluation(id: string): Promise<{ success: boolean; message?: string }> {
    const response = await api.delete<{ success: boolean; message?: string }>(`/history/${id}`)
    return response.data
  },

  async getBatches(skip = 0, limit = 50): Promise<BatchHistoryResponse[]> {
    const response = await api.get<BatchHistoryResponse[]>('/history/batches', {
      params: { skip, limit },
    })
    return response.data
  },

  async getBatchDetail(id: string): Promise<BatchDetailResponse> {
    const response = await api.get<BatchDetailResponse>(`/history/batches/${id}`)
    return response.data
  },

  async deleteBatch(id: string): Promise<{ success: boolean; message?: string }> {
    const response = await api.delete<{ success: boolean; message?: string }>(`/history/batches/${id}`)
    return response.data
  },
}
