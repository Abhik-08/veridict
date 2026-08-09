import React from 'react'
import type { AverageDimensionScores } from '@/services/dashboardService'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { BarChart3 } from 'lucide-react'

interface DimensionScoreChartProps {
  scores?: AverageDimensionScores
  loading?: boolean
}

const DIMENSION_COLORS = {
  Relevance: '#3b82f6', // blue-500
  Accuracy: '#10b981', // emerald-500
  Completeness: '#8b5cf6', // purple-500
  Overall: '#f59e0b', // amber-500
}

export const DimensionScoreChart: React.FC<DimensionScoreChartProps> = ({
  scores,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 h-80 animate-pulse flex flex-col justify-between">
        <div className="h-4 bg-slate-800 rounded-md w-1/3" />
        <div className="h-48 bg-slate-800/50 rounded-xl" />
      </div>
    )
  }

  const getScore = (primary?: number, ...fallbacks: (number | undefined)[]): number => {
    if (typeof primary === 'number' && !Number.isNaN(primary) && primary > 0) return primary
    for (const fb of fallbacks) {
      if (typeof fb === 'number' && !Number.isNaN(fb) && fb > 0) return fb
    }
    return typeof primary === 'number' && !Number.isNaN(primary) ? primary : 0
  }

  const data = [
    {
      name: 'Relevance',
      score: getScore(
        scores?.average_relevance,
        scores?.relevance,
        (scores as any)?.relevance_score,
        (scores as any)?.average_relevance_score,
      ),
      fill: DIMENSION_COLORS.Relevance,
    },
    {
      name: 'Accuracy',
      score: getScore(
        scores?.average_accuracy,
        scores?.accuracy,
        (scores as any)?.accuracy_score,
        (scores as any)?.average_accuracy_score,
      ),
      fill: DIMENSION_COLORS.Accuracy,
    },
    {
      name: 'Completeness',
      score: getScore(
        scores?.average_completeness,
        scores?.completeness,
        (scores as any)?.completeness_score,
        (scores as any)?.average_completeness_score,
      ),
      fill: DIMENSION_COLORS.Completeness,
    },
    {
      name: 'Overall',
      score: getScore(
        scores?.average_overall_score,
        scores?.overall_score,
        (scores as any)?.overall,
        (scores as any)?.average_score,
      ),
      fill: DIMENSION_COLORS.Overall,
    },
  ]

  const hasDimensionScores = data.some((d) => d.name !== 'Overall' && d.score > 0)
  const isSummaryOnly = !hasDimensionScores && (data.find((d) => d.name === 'Overall')?.score ?? 0) > 0

  return (
    <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-xs shadow-xs space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <BarChart3 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">Dimension Score Breakdown</h3>
            <p className="text-xs text-slate-400">Average scores across evaluation criteria (1–5 scale)</p>
          </div>
        </div>

        {isSummaryOnly && (
          <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 self-start sm:self-auto">
            Dimensions Unavailable (Summary-Only)
          </span>
        )}
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
            <XAxis type="number" domain={[0, 5]} stroke="#94a3b8" tick={{ fontSize: 12 }} />
            <YAxis
              dataKey="name"
              type="category"
              stroke="#cbd5e1"
              tick={{ fontSize: 12, fontWeight: 600 }}
              width={100}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '0.75rem',
                color: '#f8fafc',
                fontSize: '12px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
              }}
              itemStyle={{ color: '#f8fafc', fontWeight: 600 }}
              labelStyle={{ color: '#f8fafc', fontWeight: 700 }}
              cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
              formatter={(val: any, _name: any, item: any) => {
                const numVal = Number(val)
                if (numVal === 0 && item?.payload?.name !== 'Overall' && isSummaryOnly) {
                  return ['Unavailable (Summary-only record)', 'Score']
                }
                return [`${numVal.toFixed(2)} / 5.00`, 'Score']
              }}
            />
            <Bar dataKey="score" radius={[0, 8, 8, 0]} barSize={24} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
