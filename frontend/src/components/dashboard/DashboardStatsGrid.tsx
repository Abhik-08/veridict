import {
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Award,
  Target,
  ShieldCheck,
  Layers,
} from 'lucide-react'
import type { DashboardStatistics, AnalyticsStatistics } from '@/services/dashboardService'
import { DashboardStatCard } from './DashboardStatCard'
import { SkeletonCard } from '../shared/SkeletonLoader'

interface DashboardStatsGridProps {
  stats: DashboardStatistics | null
  analytics?: AnalyticsStatistics | null
  loading: boolean
}

export function DashboardStatsGrid({ stats, analytics, loading }: Readonly<DashboardStatsGridProps>) {
  if (loading || !stats) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, idx) => (
            <SkeletonCard key={idx} />
          ))}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, idx) => (
            <SkeletonCard key={idx} />
          ))}
        </div>
      </div>
    )
  }

  const scores = analytics?.average_scores
  const relScore = scores?.average_relevance ?? 0
  const accScore = scores?.average_accuracy ?? 0
  const compScore = scores?.average_completeness ?? 0

  return (
    <div className="space-y-4">
      {/* Top Row: 4 Overall Metrics */}
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

      {/* Bottom Row: 4 Dimension & Status Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Needs Improvement */}
        <DashboardStatCard
          title="Needs Improvement"
          value={`${(stats.needs_improvement_percentage ?? 0).toFixed(1)}%`}
          subtitle={`${stats.needs_improvement_count} evaluation(s)`}
          icon={<AlertTriangle className="w-5 h-5" />}
          accentColor="amber"
        />

        {/* Average Relevance */}
        <DashboardStatCard
          title="Average Relevance"
          value={relScore > 0 ? `${relScore.toFixed(2)} / 5.0` : 'Unavailable'}
          subtitle={relScore > 0 ? 'Target criteria scale 1–5' : 'Summary-only records'}
          icon={<Target className="w-5 h-5" />}
          accentColor="blue"
        />

        {/* Average Accuracy */}
        <DashboardStatCard
          title="Average Accuracy"
          value={accScore > 0 ? `${accScore.toFixed(2)} / 5.0` : 'Unavailable'}
          subtitle={accScore > 0 ? 'Factual verification scale 1–5' : 'Summary-only records'}
          icon={<ShieldCheck className="w-5 h-5" />}
          accentColor="emerald"
        />

        {/* Average Completeness */}
        <DashboardStatCard
          title="Average Completeness"
          value={compScore > 0 ? `${compScore.toFixed(2)} / 5.0` : 'Unavailable'}
          subtitle={compScore > 0 ? 'Aspect coverage scale 1–5' : 'Summary-only records'}
          icon={<Layers className="w-5 h-5" />}
          accentColor="purple"
        />
      </div>
    </div>
  )
}
