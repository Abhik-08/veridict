import { useState, useEffect, useCallback } from 'react'
import {
  dashboardService,
  type DashboardStatistics,
  type AnalyticsStatistics,
  type AnalyticsFilterParams,
} from '@/services/dashboardService'
import type { HistoryItemResponse } from '@/services/historyService'

export function useDashboard() {
  const [stats, setStats] = useState<DashboardStatistics | null>(null)
  const [recentItems, setRecentItems] = useState<HistoryItemResponse[]>([])
  const [analytics, setAnalytics] = useState<AnalyticsStatistics | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [analyticsLoading, setAnalyticsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<AnalyticsFilterParams>({})

  const fetchDashboardData = useCallback(async () => {
    setLoading(true)
    setAnalyticsLoading(true)
    setError(null)
    try {
      const [statsRes, recentRes, analyticsRes] = await Promise.all([
        dashboardService.getDashboardStats(),
        dashboardService.getRecentHistory(10),
        dashboardService.getAnalytics(filters),
      ])
      setStats(statsRes)
      setRecentItems(recentRes)
      setAnalytics(analyticsRes)
    } catch (err: any) {
      console.error('Failed to fetch dashboard data:', err)
      setError(err.response?.data?.message || err.message || 'Failed to load dashboard metrics.')
    } finally {
      setLoading(false)
      setAnalyticsLoading(false)
    }
  }, [filters])

  const refetchAnalyticsOnly = useCallback(async (newFilters: AnalyticsFilterParams) => {
    setAnalyticsLoading(true)
    try {
      const analyticsRes = await dashboardService.getAnalytics(newFilters)
      setAnalytics(analyticsRes)
    } catch (err: any) {
      console.error('Failed to update analytics filters:', err)
    } finally {
      setAnalyticsLoading(false)
    }
  }, [])

  const updateFilters = useCallback(
    (newFilters: AnalyticsFilterParams) => {
      setFilters(newFilters)
      refetchAnalyticsOnly(newFilters)
    },
    [refetchAnalyticsOnly],
  )

  const resetFilters = useCallback(() => {
    setFilters({})
    refetchAnalyticsOnly({})
  }, [refetchAnalyticsOnly])

  useEffect(() => {
    fetchDashboardData()
  }, [fetchDashboardData])

  return {
    stats,
    recentItems,
    analytics,
    loading,
    analyticsLoading,
    error,
    filters,
    updateFilters,
    resetFilters,
    refetch: fetchDashboardData,
  }
}
