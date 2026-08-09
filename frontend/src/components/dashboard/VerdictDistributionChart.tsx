import React from 'react'
import type { VerdictDistribution } from '@/services/dashboardService'
import { PieChart, Pie, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { PieChart as PieIcon } from 'lucide-react'

interface VerdictDistributionChartProps {
  distribution?: VerdictDistribution
  totalEvaluations?: number
  loading?: boolean
}

const VERDICT_COLORS = {
  PASS: '#10b981', // emerald-500
  NEEDS_IMPROVEMENT: '#f59e0b', // amber-500
  FAIL: '#f43f5e', // rose-500
}

const renderLegendText = (value: string) => (
  <span className="text-xs font-medium text-slate-300 mr-2">{value}</span>
)

export const VerdictDistributionChart: React.FC<VerdictDistributionChartProps> = ({
  distribution,
  totalEvaluations = 0,
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

  const data = [
    {
      name: 'Pass',
      value: distribution?.pass_count ?? 0,
      percentage: distribution?.pass_percentage ?? 0,
      fill: VERDICT_COLORS.PASS,
    },
    {
      name: 'Needs Improvement',
      value: distribution?.needs_improvement_count ?? 0,
      percentage: distribution?.needs_improvement_percentage ?? 0,
      fill: VERDICT_COLORS.NEEDS_IMPROVEMENT,
    },
    {
      name: 'Fail',
      value: distribution?.fail_count ?? 0,
      percentage: distribution?.fail_percentage ?? 0,
      fill: VERDICT_COLORS.FAIL,
    },
  ].filter((item) => totalEvaluations === 0 || item.value > 0)

  return (
    <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-xs shadow-xs space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <PieIcon className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">Verdict Distribution</h3>
            <p className="text-xs text-slate-400">Ratio of Pass, Needs Improvement, and Fail verdicts</p>
          </div>
        </div>
      </div>

      <div className="h-64 w-full relative flex items-center justify-center">
        {totalEvaluations === 0 ? (
          <div className="text-center text-xs text-slate-500 py-12">No evaluation verdict data</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={85}
                paddingAngle={4}
                dataKey="value"
                stroke="#0f172a"
                strokeWidth={2}
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
                formatter={(val: any, name: any, item: any) => [
                  `${val} (${item.payload.percentage}%)`,
                  name,
                ]}
              />
              <Legend height={36} formatter={renderLegendText} />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
