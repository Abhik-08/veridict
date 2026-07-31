import {
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Award,
  Layers,
  Activity,
} from 'lucide-react'
import type { DashboardStatistics } from '@/services/dashboardService'
import { DashboardStatCard } from './DashboardStatCard'
import { SkeletonCard } from '../shared/SkeletonLoader'

interface DashboardStatsGridProps {
  stats: DashboardStatistics | null
  loading: boolean
}

export function DashboardStatsGrid({ stats, loading }: Readonly<DashboardStatsGridProps>) {
  if (loading || !stats) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, idx) => (
            <SkeletonCard key={idx} />
          ))}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 lg:flex lg:justify-center gap-4">
          {Array.from({ length: 3 }).map((_, idx) => (
            <div key={idx} className="w-full lg:w-[calc(25%-12px)]">
              <SkeletonCard />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Top Row: 4 Primary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Evaluations */}
        <DashboardStatCard
          title="Total Evaluations"
          value={stats.total_evaluations}
          subtitle={`${stats.recent_activity_count} in last 24h`}
          icon={<BarChart3 className="w-5 h-5" />}
          accentColor="amber"
        />

        {/* Average Score */}
        <DashboardStatCard
          title="Average Score"
          value={`${stats.average_score.toFixed(2)} / 5.0`}
          subtitle={`Max: ${stats.highest_score?.toFixed(1) || '-'} | Min: ${stats.lowest_score?.toFixed(1) || '-'}`}
          icon={<Award className="w-5 h-5" />}
          accentColor="blue"
        />

        {/* PASS Rate */}
        <DashboardStatCard
          title="PASS Rate"
          value={`${stats.pass_percentage.toFixed(1)}%`}
          subtitle={`${stats.pass_count} evaluation(s) passed`}
          icon={<CheckCircle2 className="w-5 h-5" />}
          accentColor="emerald"
        />

        {/* FAIL Rate */}
        <DashboardStatCard
          title="FAIL Rate"
          value={`${(stats.fail_percentage ?? 0).toFixed(1)}%`}
          subtitle={`${stats.fail_count} evaluation(s) failed`}
          icon={<XCircle className="w-5 h-5" />}
          accentColor="rose"
        />
      </div>

      {/* Bottom Row: 3 Secondary Metrics Centered */}
      <div className="grid grid-cols-1 sm:grid-cols-3 lg:flex lg:justify-center gap-4">
        <div className="w-full lg:w-[calc(25%-12px)]">
          {/* Needs Improvement */}
          <DashboardStatCard
            title="Needs Improvement"
            value={`${(stats.needs_improvement_percentage ?? 0).toFixed(1)}%`}
            subtitle={`${stats.needs_improvement_count} evaluation(s)`}
            icon={<AlertTriangle className="w-5 h-5" />}
            accentColor="amber"
          />
        </div>

        <div className="w-full lg:w-[calc(25%-12px)]">
          {/* Batch Evaluation Jobs */}
          <DashboardStatCard
            title="Total Batch Jobs"
            value={stats.total_batch_jobs}
            subtitle={`Avg batch size: ${stats.average_batch_size.toFixed(0)} items`}
            icon={<Layers className="w-5 h-5" />}
            accentColor="blue"
          />
        </div>

        <div className="w-full lg:w-[calc(25%-12px)]">
          {/* 24h Activity */}
          <DashboardStatCard
            title="24h Activity"
            value={stats.recent_activity_count}
            subtitle="Evaluations in last 24 hours"
            icon={<Activity className="w-5 h-5" />}
            accentColor="emerald"
          />
        </div>
      </div>
    </div>
  )
}
