import React from 'react'
import type { HallucinationMetrics } from '@/services/dashboardService'
import { AlertTriangle, CheckCircle2, FileQuestion, Activity } from 'lucide-react'

interface HallucinationAnalysisProps {
  metrics?: HallucinationMetrics
  loading?: boolean
}

export const HallucinationAnalysis: React.FC<HallucinationAnalysisProps> = ({
  metrics,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 h-64 animate-pulse flex flex-col justify-between">
        <div className="h-4 bg-slate-800 rounded-md w-1/3" />
        <div className="grid grid-cols-2 gap-4">
          <div className="h-20 bg-slate-800/50 rounded-xl" />
          <div className="h-20 bg-slate-800/50 rounded-xl" />
        </div>
      </div>
    )
  }

  const rate = metrics?.hallucination_rate_percentage ?? 0
  const evalCount = metrics?.evaluable_count ?? 0
  const insufficientCount =
    metrics?.insufficient_evidence_count ??
    metrics?.missing_evidence_count ??
    metrics?.insufficient_evidence ??
    0
  const hallucinatedCount = metrics?.hallucinated_count ?? 0
  const groundedCount = metrics?.grounded_count ?? 0
  const avgScore = metrics?.average_hallucination_score ?? 0

  return (
    <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-xs shadow-xs space-y-4">
      <div className="flex items-center gap-2.5">
        <div className="p-1.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400">
          <AlertTriangle className="w-4 h-4" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-100">Hallucination Frequency Analysis</h3>
          <p className="text-xs text-slate-400">Groundedness audit and unverified claims breakdown</p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 pt-1">
        {/* Hallucination Rate */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Hallucination Rate</span>
            <Activity className="w-3.5 h-3.5 text-rose-400" />
          </div>
          <p className="text-xl font-extrabold text-slate-100">{rate.toFixed(1)}%</p>
          <p className="text-[11px] text-slate-500">{hallucinatedCount} of {evalCount} evaluable</p>
        </div>

        {/* Grounded Responses */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Grounded Responses</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <p className="text-xl font-extrabold text-emerald-400">{groundedCount}</p>
          <p className="text-[11px] text-slate-500">Hallucination score ≥ 4.0</p>
        </div>

        {/* Hallucinated Responses */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Hallucinated</span>
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          </div>
          <p className="text-xl font-extrabold text-rose-400">{hallucinatedCount}</p>
          <p className="text-[11px] text-slate-500">Hallucination score &lt; 4.0</p>
        </div>

        {/* Insufficient Evidence */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Missing Evidence</span>
            <FileQuestion className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <p className="text-xl font-extrabold text-amber-400">{insufficientCount}</p>
          <p className="text-[11px] text-slate-500">Excluded (No context)</p>
        </div>

        {/* Average Hallucination Score */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Avg Grounding Score</span>
            <Activity className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <p className="text-xl font-extrabold text-slate-100">{avgScore.toFixed(2)}</p>
          <p className="text-[11px] text-slate-500">Scale 1.0 to 5.0</p>
        </div>
      </div>
    </div>
  )
}
