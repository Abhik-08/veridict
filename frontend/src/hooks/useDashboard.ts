import { useState, useEffect, useCallback } from 'react'
import { dashboardService, type DashboardStatistics } from '@/services/dashboardService'
import type { HistoryItemResponse } from '@/services/historyService'

export function useDashboard() {
  const [stats, setStats] = useState<DashboardStatistics | null>(null)
  const [recentItems, setRecentItems] = useState<HistoryItemResponse[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDashboardData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [statsRes, recentRes] = await Promise.all([
        dashboardService.getDashboardStats(),
        dashboardService.getRecentHistory(10),
      ])
      setStats(statsRes)
      setRecentItems(recentRes)
    } catch (err: any) {
      console.error('Failed to fetch dashboard data:', err)
      setError(err.response?.data?.message || err.message || 'Failed to load dashboard metrics.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDashboardData()
  }, [fetchDashboardData])

  return {
    stats,
    recentItems,
    loading,
    error,
    refetch: fetchDashboardData,
  }
}
