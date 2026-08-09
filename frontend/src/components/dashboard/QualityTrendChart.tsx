import React from 'react'
import type { QualityTrendPoint } from '@/services/dashboardService'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { TrendingUp } from 'lucide-react'

interface QualityTrendChartProps {
  trends?: QualityTrendPoint[]
  loading?: boolean
}

export const QualityTrendChart: React.FC<QualityTrendChartProps> = ({
  trends = [],
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

  return (
    <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-xs shadow-xs space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <TrendingUp className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">Quality Trend Over Time</h3>
            <p className="text-xs text-slate-400">Average overall evaluation score trajectory by date</p>
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        {trends.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-slate-500">
            No time-series trend data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trends} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 5]} stroke="#94a3b8" tick={{ fontSize: 11 }} />
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
                formatter={(val: any) => [`${Number(val).toFixed(2)} / 5.00`, 'Average Score']}
                labelFormatter={(label) => (typeof label === 'string' ? `Date: ${label}` : 'Date')}
              />
              <Line
                type="monotone"
                dataKey="average_score"
                stroke="#f59e0b"
                strokeWidth={3}
                dot={{ r: 4, fill: '#f59e0b', strokeWidth: 2, stroke: '#0f172a' }}
                activeDot={{ r: 6, fill: '#fbbf24' }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
