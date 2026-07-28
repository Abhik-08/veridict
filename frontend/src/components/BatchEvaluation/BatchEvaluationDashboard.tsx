/**
 * Veridict Batch Evaluation Dashboard Component.
 *
 * Product-level commercial AI engineering dashboard layout for bulk dataset evaluation.
 * SaaS file upload cards, contextual processing timeline stepper, segmented filter controls,
 * number-first metric cards, and sticky table headers/columns.
 */

import React, { useState, useEffect, useRef } from 'react'
import {
  FileText,
  Upload,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Download,
  Loader2,
  RefreshCw,
  Search,
  Filter,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Clock,
  Cpu,
  Layers,
  BarChart3,
  Check,
  RotateCcw,
  X,
} from 'lucide-react'

import type { BatchProgress, BatchItemEvaluationResult } from '../../types'
import {
  evaluateBatchCSV,
  evaluateBatchPDF,
  getBatchProgress,
  exportBatchCSV,
  exportBatchPDF,
} from '../../services/batchEvaluationService'

interface BatchEvaluationDashboardProps {
  onToast?: (type: 'success' | 'error' | 'info' | 'warning', title: string, message?: string) => void
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Number.parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

// ──────────────────────────────────────────────
// Sub-component: Soft Verdict Badge
// ──────────────────────────────────────────────
const SoftVerdictBadge: React.FC<{ verdict?: string }> = ({ verdict }) => {
  if (verdict === 'PASS') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
        <CheckCircle2 className="w-3 h-3" /> PASS
      </span>
    )
  }
  if (verdict === 'NEEDS_IMPROVEMENT') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
        <AlertTriangle className="w-3 h-3" /> NEEDS IMPROVEMENT
      </span>
    )
  }
  if (verdict === 'FAIL') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
        <XCircle className="w-3 h-3" /> FAIL
      </span>
    )
  }
  return <span className="text-slate-500">-</span>
}

// ──────────────────────────────────────────────
// Sub-component: Categorized Capability Chips with Tooltips
// ──────────────────────────────────────────────
const CategorizedCapabilities: React.FC = () => {
  const categories = [
    {
      title: 'Inputs',
      chips: [
        { name: 'CSV', tooltip: 'Standard CSV file with Question and AI Response columns' },
        { name: 'Digital QA PDF', tooltip: 'Searchable PDF document containing Question: and AI Response: sections' },
      ],
    },
    {
      title: 'Capabilities',
      chips: [
        { name: 'Max 30 QA', tooltip: 'Current upload batch limit' },
        { name: 'Grouped Processing', tooltip: 'Evaluates up to three QA pairs per Gemini request' },
        { name: 'Live Progress', tooltip: 'Updates batch completion in real time' },
      ],
    },
    {
      title: 'Outputs',
      chips: [
        { name: 'CSV Export', tooltip: 'Export complete evaluation dataset as CSV' },
        { name: 'PDF Report', tooltip: 'Download executive summary PDF report' },
      ],
    },
  ]

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-400 mt-2">
      {categories.map((cat) => (
        <div key={cat.title} className="flex items-center gap-1.5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">{cat.title}:</span>
          <div className="flex items-center gap-1">
            {cat.chips.map((chip) => (
              <span
                key={chip.name}
                title={chip.tooltip}
                className="px-2 py-0.5 text-[11px] font-medium text-slate-300 bg-slate-800/80 border border-slate-700/50 rounded-md cursor-help hover:border-amber-500/40 transition-colors"
              >
                {chip.name}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

// ──────────────────────────────────────────────
// Sub-component: File Preview Card (Post-Upload)
// ──────────────────────────────────────────────
const FilePreviewCard: React.FC<{
  file: File
  label: string
  icon: React.ComponentType<{ className?: string }>
  onReplace: () => void
  onRemove: () => void
}> = ({ file, label, icon: IconComponent, onReplace, onRemove }) => {
  return (
    <div className="p-4 rounded-xl border border-emerald-500/30 bg-slate-900/80 flex items-center justify-between transition-all duration-150">
      <div className="flex items-center gap-3 min-w-0">
        <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
          <IconComponent className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-white truncate">{file.name}</span>
            <span className="px-2 py-0.5 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
              Ready
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">
            {label} • {formatBytes(file.size)}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-1.5">
        <button
          type="button"
          onClick={onReplace}
          className="flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-md border border-slate-700 transition-colors"
          title="Replace file"
        >
          <RotateCcw className="w-3 h-3" />
          Replace
        </button>
        <button
          type="button"
          onClick={onRemove}
          className="p-1 text-slate-400 hover:text-rose-400 bg-slate-800 hover:bg-slate-700 rounded-md border border-slate-700 transition-colors"
          title="Remove file"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}

// ──────────────────────────────────────────────
// Sub-component: Processing Timeline Stepper (Contextual & Collapsible)
// ──────────────────────────────────────────────
const getStageBadgeStyle = (done: boolean, active: boolean): string => {
  if (done) return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
  if (active) return 'bg-amber-500/20 text-amber-400 border border-amber-500/40 animate-pulse'
  return 'bg-slate-800 text-slate-500 border border-slate-700'
}

const getStageTextStyle = (done: boolean, active: boolean): string => {
  if (done) return 'text-slate-200 font-medium'
  if (active) return 'text-amber-400 font-semibold'
  return 'text-slate-500 font-medium'
}

const ProcessingTimelineStepper: React.FC<{ progress: BatchProgress }> = ({ progress }) => {
  const [showDetails, setShowDetails] = useState(false)
  const isCompleted = progress.status === 'COMPLETED'
  const isProcessing = progress.status === 'PROCESSING' || progress.status === 'PENDING'
  const processedRows = progress.processed_rows || 0

  const stages = [
    { label: 'Dataset Uploaded', done: true, active: false },
    { label: 'Context Loaded', done: true, active: false },
    { label: 'Evidence Retrieved', done: processedRows > 0 || isCompleted, active: isProcessing && processedRows === 0 },
    { label: 'Gemini Evaluation', done: isCompleted, active: isProcessing },
    { label: 'Reports Generated', done: isCompleted, active: isCompleted },
  ]

  if (isCompleted && !showDetails) {
    return (
      <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs flex items-center justify-between text-slate-300">
        <span className="flex items-center gap-2 font-medium text-emerald-400">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          Evaluation Pipeline Completed
        </span>
        <button
          onClick={() => setShowDetails(true)}
          className="text-[11px] font-semibold text-amber-400 hover:text-amber-300 transition-colors flex items-center gap-1"
        >
          View Processing Steps <ChevronDown className="w-3 h-3" />
        </button>
      </div>
    )
  }

  return (
    <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2">
        {stages.map((st, idx) => (
          <React.Fragment key={st.label}>
            <div className="flex items-center gap-1.5">
              <span
                className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${getStageBadgeStyle(
                  st.done,
                  st.active
                )}`}
              >
                {st.done ? '✓' : idx + 1}
              </span>
              <span className={getStageTextStyle(st.done, st.active)}>{st.label}</span>
            </div>
            {idx < stages.length - 1 && <span className="text-slate-700 hidden sm:inline">→</span>}
          </React.Fragment>
        ))}
      </div>
      {isCompleted && (
        <div className="flex justify-end pt-1">
          <button
            onClick={() => setShowDetails(false)}
            className="text-[10px] font-semibold text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1"
          >
            Hide Processing Steps <ChevronUp className="w-3 h-3" />
          </button>
        </div>
      )}
    </div>
  )
}

// ──────────────────────────────────────────────
// Sub-component: Number-First Metric Cards Grid
// ──────────────────────────────────────────────
const MetricCardsGrid: React.FC<{ items: BatchItemEvaluationResult[]; progress: BatchProgress }> = ({
  items,
  progress,
}) => {
  const totalCount = items.length
  const passCount = items.filter((i) => i.verdict === 'PASS').length
  const impCount = items.filter((i) => i.verdict === 'NEEDS_IMPROVEMENT').length
  const failCount = items.filter((i) => i.verdict === 'FAIL' || i.status === 'FAILED').length
  const passRate = totalCount > 0 ? ((passCount / totalCount) * 100).toFixed(1) : '0.0'

  const avgOverall =
    totalCount > 0 ? (items.reduce((acc, i) => acc + (i.overall_score || 0), 0) / totalCount).toFixed(2) : '0.00'

  const avgConfidence =
    totalCount > 0
      ? ((items.reduce((acc, i) => acc + (i.confidence ?? 0.9), 0) / totalCount) * 100).toFixed(0)
      : '0'

  const elapsedSeconds = progress.elapsed_seconds || (progress.statistics?.elapsed_seconds ?? null)
  const geminiCalls = progress.gemini_call_count || (progress.statistics?.gemini_call_count ?? (progress.total_batches || 1))

  const metrics = [
    { label: 'Total Items', val: totalCount, icon: Layers, color: 'text-white', tooltip: 'Total QA pairs evaluated in dataset' },
    { label: 'Pass Rate', val: `${passRate}%`, icon: ShieldCheck, color: 'text-emerald-400', tooltip: 'Percentage of responses passing overall score threshold' },
    { label: 'Needs Imp', val: impCount, icon: AlertTriangle, color: 'text-amber-400', tooltip: 'Responses requiring minor revisions' },
    { label: 'Failed', val: failCount, icon: XCircle, color: 'text-rose-400', tooltip: 'Responses with major factual issues' },
    { label: 'Avg Score', val: `${avgOverall} / 5`, icon: BarChart3, color: 'text-white', tooltip: 'Weighted average evaluation score across 4 dimensions' },
    { label: 'Avg Confidence', val: `${avgConfidence}%`, icon: Check, color: 'text-slate-200', tooltip: 'Average confidence returned by Gemini judge models' },
    { label: 'Gemini Calls', val: geminiCalls, icon: Cpu, color: 'text-amber-400', tooltip: 'Number of grouped LLM requests' },
    { label: 'Duration', val: elapsedSeconds ? `${elapsedSeconds}s` : 'Active', icon: Clock, color: 'text-slate-200', tooltip: 'Total evaluation wall-clock duration' },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
      {metrics.map((m) => {
        const Icon = m.icon
        return (
          <div key={m.label} title={m.tooltip} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800/80 hover:border-slate-700 transition-colors cursor-help">
            <div className="flex items-center justify-between">
              <span className={`text-xl font-bold ${m.color}`}>{m.val}</span>
              <Icon className="w-3.5 h-3.5 text-slate-500" />
            </div>
            <span className="text-[10px] font-medium text-slate-400 mt-1 block">{m.label}</span>
          </div>
        )
      })}
    </div>
  )
}

// ──────────────────────────────────────────────
// Sub-component: Batch Summary Panel
// ──────────────────────────────────────────────
const BatchSummaryPanel: React.FC<{ items: BatchItemEvaluationResult[]; progress: BatchProgress }> = ({
  items,
  progress,
}) => {
  const totalCount = items.length
  const passCount = items.filter((i) => i.verdict === 'PASS').length
  const impCount = items.filter((i) => i.verdict === 'NEEDS_IMPROVEMENT').length
  const failCount = items.filter((i) => i.verdict === 'FAIL' || i.status === 'FAILED').length

  const avgOverall =
    totalCount > 0 ? (items.reduce((acc, i) => acc + (i.overall_score || 0), 0) / totalCount).toFixed(2) : '0.00'

  const elapsedSeconds = progress.elapsed_seconds || (progress.statistics?.elapsed_seconds ?? null)

  return (
    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          Evaluation Summary
        </h3>
        <span className="text-xs text-slate-400">
          Average Score: <strong className="text-white">{avgOverall} / 5.00</strong>
          {elapsedSeconds && <span className="ml-3">Processing Time: <strong className="text-slate-300">{elapsedSeconds}s</strong></span>}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <div className="flex items-start gap-2.5 p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-emerald-300">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-emerald-400">✓ Passed ({passCount})</span>
            <p className="text-[11px] text-emerald-300/80 mt-0.5">
              {passCount} responses satisfied all quality checks.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-2.5 p-2.5 rounded-lg bg-amber-950/20 border border-amber-500/20 text-amber-300">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-amber-400">⚠ Needs Improvement ({impCount})</span>
            <p className="text-[11px] text-amber-300/80 mt-0.5">
              {impCount} responses require minor revisions.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-2.5 p-2.5 rounded-lg bg-rose-950/20 border border-rose-500/20 text-rose-300">
          <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-rose-400">✗ Failed ({failCount})</span>
            <p className="text-[11px] text-rose-300/80 mt-0.5">
              {failCount} responses contained major factual inaccuracies.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

// ──────────────────────────────────────────────
// Sub-component: Job Progress Card & Embedded Footer Actions
// ──────────────────────────────────────────────
const JobProgressCard: React.FC<{
  progress: BatchProgress
  exportingCSV: boolean
  exportingPDF: boolean
  onExportCSV: () => void
  onExportPDF: () => void
  onReset: () => void
}> = ({ progress, exportingCSV, exportingPDF, onExportCSV, onExportPDF, onReset }) => {
  const percent =
    progress.total_rows > 0 ? Math.round((progress.processed_rows / progress.total_rows) * 100) : 0

  const elapsedSeconds = progress.elapsed_seconds || (progress.statistics?.elapsed_seconds ?? null)
  const geminiCalls = progress.gemini_call_count || (progress.statistics?.gemini_call_count ?? (progress.total_batches || 1))

  return (
    <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-4 bg-slate-900/60">
      {/* Dominant Status Badge & Metadata */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2.5">
            {progress.status === 'PROCESSING' && (
              <span className="flex items-center gap-2 text-xs font-bold text-amber-400 bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/30 animate-pulse">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Evaluating Prompts...
              </span>
            )}
            {progress.status === 'COMPLETED' && (
              <span className="flex items-center gap-2 text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/30">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Evaluation Completed
              </span>
            )}
            {progress.status === 'FAILED' && (
              <span className="flex items-center gap-2 text-xs font-bold text-rose-400 bg-rose-500/10 px-3 py-1 rounded-full border border-rose-500/30">
                <XCircle className="w-3.5 h-3.5" />
                Evaluation Failed
              </span>
            )}

            <span className="text-sm font-semibold text-white">{progress.filename}</span>
            <span className="px-2 py-0.5 text-[10px] font-mono text-slate-400 bg-slate-800 rounded border border-slate-700">
              {progress.batch_id}
            </span>
          </div>

          <p className="text-xs text-slate-400 mt-2 space-x-2">
            <span>Batch {progress.current_batch} of {progress.total_batches}</span>
            <span>•</span>
            <span>{progress.processed_rows} of {progress.total_rows} processed</span>
            {elapsedSeconds && (
              <>
                <span>•</span>
                <span>{elapsedSeconds}s</span>
              </>
            )}
            <span>•</span>
            <span>{geminiCalls} Gemini requests</span>
          </p>
        </div>

        <button
          onClick={onReset}
          className="p-1.5 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors border border-slate-700 self-start sm:self-center"
          title="New Batch Evaluation"
          aria-label="New Batch Evaluation"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Thicker Progress Bar with Percentage at End */}
      <div className="flex items-center gap-3">
        <div className="flex-1 bg-slate-950 rounded-full h-3 overflow-hidden border border-slate-800">
          <div
            className="bg-gradient-to-r from-amber-500 to-orange-500 h-3 rounded-full transition-all duration-200"
            style={{ width: `${percent}%` }}
          />
        </div>
        <span className="text-xs font-bold font-mono text-amber-400 min-w-[40px] text-right">{percent}%</span>
      </div>

      {/* Footer Export Actions Embedded in Card */}
      {progress.status === 'COMPLETED' && (
        <div className="pt-3 border-t border-slate-800/80 flex items-center justify-end gap-2.5">
          <button
            onClick={onExportCSV}
            disabled={exportingCSV}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-2 transition-colors disabled:opacity-40"
          >
            {exportingCSV ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5 text-amber-400" />}
            Export CSV
          </button>
          <button
            onClick={onExportPDF}
            disabled={exportingPDF}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-amber-500 hover:bg-amber-600 text-slate-950 shadow-xs flex items-center gap-2 transition-colors disabled:opacity-40"
          >
            {exportingPDF ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FileText className="w-3.5 h-3.5" />}
            Export PDF Report
          </button>
        </div>
      )}
    </div>
  )
}

// ──────────────────────────────────────────────
// Sub-component: Table Row with Sticky Question Column
// ──────────────────────────────────────────────
const BatchTableRow: React.FC<{
  item: BatchItemEvaluationResult
  isExpanded: boolean
  onToggleExpand: () => void
}> = ({ item, isExpanded, onToggleExpand }) => {
  return (
    <tr className="hover:bg-slate-800/40 even:bg-slate-900/30 transition-colors duration-150">
      <td className="px-3.5 py-3.5 font-mono text-amber-400 font-semibold align-top">{item.id}</td>

      {/* Sticky Question & Response Column */}
      <td className="px-4 py-3.5 max-w-xl space-y-1 align-top sticky left-0 bg-slate-950/95 border-r border-slate-800/80 z-10 backdrop-blur-sm">
        <div className="text-sm font-bold text-slate-100">Q: {item.question}</div>
        <div className="text-xs text-slate-300 leading-normal">A: {item.ai_response}</div>
        {item.reasoning && (
          <div className="pt-1">
            <div
              className={`text-[11px] text-slate-400 leading-relaxed font-mono ${
                !isExpanded ? 'line-clamp-2' : ''
              }`}
            >
              <span className="text-slate-500 font-sans font-medium">Reasoning: </span>
              {item.reasoning}
            </div>
            {item.reasoning.length > 120 && (
              <button
                onClick={onToggleExpand}
                className="mt-1 inline-flex items-center gap-1 text-[10px] font-semibold text-amber-400 hover:text-amber-300 transition-colors"
              >
                {isExpanded ? (
                  <>
                    Show Less <ChevronUp className="w-3 h-3" />
                  </>
                ) : (
                  <>
                    Show Reasoning <ChevronDown className="w-3 h-3" />
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </td>

      {/* Center-Aligned Metric Scores */}
      <td className="px-3 py-3.5 text-center font-mono text-xs align-top pt-4">{item.relevance_score ?? '-'}</td>
      <td className="px-3 py-3.5 text-center font-mono text-xs align-top pt-4">{item.accuracy_score ?? '-'}</td>
      <td className="px-3 py-3.5 text-center font-mono text-xs align-top pt-4">{item.hallucination_score ?? '-'}</td>
      <td className="px-3 py-3.5 text-center font-mono text-xs align-top pt-4">{item.completeness_score ?? '-'}</td>
      <td className="px-3 py-3.5 text-center font-mono text-xs font-bold text-white align-top pt-4">
        {item.overall_score !== undefined ? item.overall_score.toFixed(2) : '-'}
      </td>

      {/* Verdict Badge */}
      <td className="px-4 py-3.5 text-center align-top pt-3.5">
        <SoftVerdictBadge verdict={item.verdict} />
      </td>
    </tr>
  )
}

// ──────────────────────────────────────────────
// Sub-component: Upload Form
// ──────────────────────────────────────────────
const BatchDatasetUploadForm: React.FC<{
  mode: 'CSV' | 'PDF'
  batchFile: File | null
  evidencePdf: File | null
  loading: boolean
  error: string | null
  onSetBatchFile: (f: File | null) => void
  onSetEvidencePdf: (f: File | null) => void
  onSubmit: (e: React.SyntheticEvent) => void
  onToast?: (type: 'success' | 'error' | 'info' | 'warning', title: string, message?: string) => void
}> = ({
  mode,
  batchFile,
  evidencePdf,
  loading,
  error,
  onSetBatchFile,
  onSetEvidencePdf,
  onSubmit,
  onToast,
}) => {
  return (
    <form onSubmit={onSubmit} className="glass-card p-5 rounded-xl border border-slate-800 space-y-4 bg-slate-900/40">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Primary Dataset Card / Preview */}
        <div>
          <label htmlFor="primary-dataset-dropzone" className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Primary Dataset File ({mode === 'CSV' ? '.CSV' : '.PDF'}) *
          </label>

          {batchFile ? (
            <FilePreviewCard
              file={batchFile}
              label={mode === 'CSV' ? 'CSV Dataset' : 'Digital QA PDF'}
              icon={mode === 'CSV' ? FileSpreadsheet : FileText}
              onReplace={() => onSetBatchFile(null)}
              onRemove={() => onSetBatchFile(null)}
            />
          ) : (
            <div className="relative border border-dashed border-slate-700 hover:border-amber-500/60 rounded-xl p-5 text-center transition-colors bg-slate-950/60 group">
              <input
                id="primary-dataset-dropzone"
                type="file"
                accept={mode === 'CSV' ? '.csv' : '.pdf'}
                onChange={(e) => {
                  const f = e.target.files?.[0] || null
                  onSetBatchFile(f)
                  if (f) onToast?.('info', 'File Selected', f.name)
                }}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div className="flex flex-col items-center gap-2">
                {mode === 'CSV' ? (
                  <FileSpreadsheet className="w-7 h-7 text-amber-400 group-hover:scale-105 transition-transform duration-150" />
                ) : (
                  <FileText className="w-7 h-7 text-amber-400 group-hover:scale-105 transition-transform duration-150" />
                )}
                <span className="text-xs font-bold text-slate-200">
                  📄 Primary Dataset — Drag & Drop or Browse Files
                </span>
                <div className="flex flex-wrap items-center justify-center gap-1.5 text-[10px] text-slate-400 pt-1">
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold">✓ Question</span>
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold">✓ AI Response</span>
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">Optional: Reference Answer</span>
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400" title="Current upload limit">Max 30 QA pairs</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Optional Evidence Context Card / Preview */}
        <div>
          <label htmlFor="evidence-context-dropzone" className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Context Evidence PDF (Optional)
          </label>

          {evidencePdf ? (
            <FilePreviewCard
              file={evidencePdf}
              label="Evidence PDF"
              icon={Upload}
              onReplace={() => onSetEvidencePdf(null)}
              onRemove={() => onSetEvidencePdf(null)}
            />
          ) : (
            <div className="relative border border-dashed border-slate-800 hover:border-slate-600 rounded-xl p-5 text-center transition-colors bg-slate-950/40 group">
              <input
                id="evidence-context-dropzone"
                type="file"
                accept=".pdf"
                onChange={(e) => {
                  const f = e.target.files?.[0] || null
                  onSetEvidencePdf(f)
                  if (f) onToast?.('info', 'Context PDF Selected', f.name)
                }}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div className="flex flex-col items-center gap-2">
                <Upload className="w-7 h-7 text-slate-500 group-hover:scale-105 transition-transform duration-150" />
                <span className="text-xs font-bold text-slate-300">
                  📚 Context Evidence — Drag & Drop or Browse Files
                </span>
                <span className="text-[11px] text-slate-500 leading-normal" title="Used for semantic evidence retrieval">
                  Used for semantic evidence retrieval during RAG evaluation.
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
          <XCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Primary Button — Prominent & Centered */}
      <div className="flex justify-center pt-1">
        <button
          type="submit"
          disabled={loading || !batchFile}
          className="w-full sm:w-auto px-8 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-600 active:bg-amber-700 text-slate-950 font-extrabold text-xs disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all duration-150 shadow-md"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Evaluating Prompts...
            </>
          ) : (
            <>
              <ShieldCheck className="w-4 h-4" />
              Run Batch Evaluation
            </>
          )}
        </button>
      </div>
    </form>
  )
}

// ──────────────────────────────────────────────
// Main Component
// ──────────────────────────────────────────────
export const BatchEvaluationDashboard: React.FC<BatchEvaluationDashboardProps> = ({ onToast }) => {
  const [mode, setMode] = useState<'CSV' | 'PDF'>('CSV')
  const [batchFile, setBatchFile] = useState<File | null>(null)
  const [evidencePdf, setEvidencePdf] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [exportingCSV, setExportingCSV] = useState(false)
  const [exportingPDF, setExportingPDF] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [progress, setProgress] = useState<BatchProgress | null>(null)
  const [verdictFilter, setVerdictFilter] = useState<'ALL' | 'PASS' | 'NEEDS_IMPROVEMENT' | 'FAIL'>('ALL')
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedRowId, setExpandedRowId] = useState<string | null>(null)

  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const handlePollUpdate = (updated: BatchProgress) => {
    setProgress(updated)
    if (updated.status === 'COMPLETED' || updated.status === 'FAILED') {
      if (pollingRef.current) clearInterval(pollingRef.current)
      if (updated.status === 'COMPLETED') {
        onToast?.('success', 'Batch Evaluation Complete', `Successfully evaluated ${updated.total_rows} QA pairs.`)
      } else {
        onToast?.('error', 'Batch Evaluation Failed', updated.error || 'One or more errors occurred.')
      }
    }
  }

  // Polling loop for active batch job
  useEffect(() => {
    if (progress && (progress.status === 'PENDING' || progress.status === 'PROCESSING')) {
      pollingRef.current = setInterval(async () => {
        try {
          const updated = await getBatchProgress(progress.batch_id)
          handlePollUpdate(updated)
        } catch (err) {
          console.error('Progress polling error:', err)
        }
      }, 1500)
    } else if (pollingRef.current) {
      clearInterval(pollingRef.current)
    }

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [progress?.batch_id, progress?.status])

  const handleSubmit = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    if (!batchFile) {
      setError('Please select a dataset file to evaluate.')
      return
    }

    setLoading(true)
    setError(null)
    setProgress(null)
    onToast?.('info', 'Submitting Batch Job', `Processing ${batchFile.name}...`)

    try {
      let initialProgress: BatchProgress
      if (mode === 'CSV') {
        initialProgress = await evaluateBatchCSV(batchFile, evidencePdf || undefined)
      } else {
        initialProgress = await evaluateBatchPDF(batchFile, evidencePdf || undefined)
      }
      setProgress(initialProgress)
      onToast?.('info', 'Batch Job Created', `ID: ${initialProgress.batch_id} — Evaluating in background...`)
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Batch evaluation submission failed.'
      setError(msg)
      onToast?.('error', 'Submission Failed', msg)
    } finally {
      setLoading(false)
    }
  }

  const handleExportCSV = async () => {
    if (!progress || exportingCSV) return
    setExportingCSV(true)
    onToast?.('info', 'Generating CSV Export...')
    try {
      await exportBatchCSV(progress.batch_id)
      onToast?.('success', 'CSV Exported Successfully')
    } catch (err: any) {
      const msg = err.message || 'Unknown error'
      onToast?.('error', 'CSV Export Failed', msg)
    } finally {
      setExportingCSV(false)
    }
  }

  const handleExportPDF = async () => {
    if (!progress || exportingPDF) return
    setExportingPDF(true)
    onToast?.('info', 'Generating PDF Report...')
    try {
      await exportBatchPDF(progress.batch_id)
      onToast?.('success', 'PDF Report Exported Successfully')
    } catch (err: any) {
      const msg = err.message || 'Unknown error'
      onToast?.('error', 'PDF Export Failed', msg)
    } finally {
      setExportingPDF(false)
    }
  }

  const resetForm = () => {
    setBatchFile(null)
    setEvidencePdf(null)
    setProgress(null)
    setError(null)
    onToast?.('info', 'Batch Form Cleared')
  }

  const toggleRowExpanded = (id: string) => {
    setExpandedRowId((prev) => (prev === id ? null : id))
  }

  const items = progress?.items || []
  const filteredItems = items.filter((item) => {
    const matchesVerdict = verdictFilter === 'ALL' || item.verdict === verdictFilter
    const matchesSearch =
      searchTerm === '' ||
      item.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.ai_response.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.id.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesVerdict && matchesSearch
  })

  return (
    <div className="space-y-4 max-w-7xl mx-auto px-4 py-2">
      {/* 1. Compact Engine Header Toolbar */}
      <div className="glass-card p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          <div>
            <h1 className="text-base font-bold text-white font-display">
              Batch Evaluation Engine
            </h1>
            <CategorizedCapabilities />
          </div>

          {/* Mode Selector Switcher Right-Aligned */}
          <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800 self-start lg:self-center">
            <button
              onClick={() => {
                setMode('CSV')
                setBatchFile(null)
              }}
              className={`flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded transition-all duration-150 ${
                mode === 'CSV'
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <FileSpreadsheet className="w-3.5 h-3.5" />
              CSV
            </button>
            <button
              onClick={() => {
                setMode('PDF')
                setBatchFile(null)
              }}
              className={`flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded transition-all duration-150 ${
                mode === 'PDF'
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              Digital PDF
            </button>
          </div>
        </div>
      </div>

      {/* 2. Upload Form & Informative Empty State / File Previews */}
      {!progress && (
        <BatchDatasetUploadForm
          mode={mode}
          batchFile={batchFile}
          evidencePdf={evidencePdf}
          loading={loading}
          error={error}
          onSetBatchFile={setBatchFile}
          onSetEvidencePdf={setEvidencePdf}
          onSubmit={handleSubmit}
          onToast={onToast}
        />
      )}

      {/* 3. Contextual Timeline, Progress Card, Metrics, Summary & Results */}
      {progress && (
        <div className="space-y-4">
          {/* Live / Collapsible Processing Timeline Stepper */}
          <ProcessingTimelineStepper progress={progress} />

          {/* Single Consolidated Progress Status Card */}
          <JobProgressCard
            progress={progress}
            exportingCSV={exportingCSV}
            exportingPDF={exportingPDF}
            onExportCSV={handleExportCSV}
            onExportPDF={handleExportPDF}
            onReset={resetForm}
          />

          {/* Number-First Metric Cards */}
          <MetricCardsGrid items={items} progress={progress} />

          {/* Dynamic Summary Card Above Table */}
          {progress.status === 'COMPLETED' && (
            <BatchSummaryPanel items={items} progress={progress} />
          )}

          {/* Search & Segmented Filter Control */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-1">
            <div className="flex flex-wrap items-center gap-2">
              {/* Search Input */}
              <div className="relative w-full sm:w-56">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search questions, responses or QA ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-7 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500/60"
                />
                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[9px] font-mono text-slate-600 bg-slate-800 px-1 rounded">Ctrl + K</span>
              </div>

              {/* Segmented Control Bar */}
              <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
                <Filter className="w-3 h-3 text-slate-500 ml-1.5 mr-0.5" />
                {(
                  [
                    { key: 'ALL', label: 'ALL' },
                    { key: 'PASS', label: 'PASS' },
                    { key: 'NEEDS_IMPROVEMENT', label: 'IMPROVEMENT' },
                    { key: 'FAIL', label: 'FAIL' },
                  ] as const
                ).map((f) => (
                  <button
                    key={f.key}
                    onClick={() => setVerdictFilter(f.key)}
                    className={`px-3 py-1 text-[10px] font-bold rounded transition-all duration-150 ${
                      verdictFilter === f.key
                        ? 'bg-amber-500 text-slate-950 shadow-xs'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Results Table */}
          <div className="glass-card rounded-xl border border-slate-800 overflow-hidden bg-slate-900/40">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs min-w-[900px]">
                <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800 sticky top-0 z-20 backdrop-blur-md">
                  <tr>
                    <th className="px-3.5 py-3 w-16">ID</th>
                    <th className="px-4 py-3 sticky left-0 bg-slate-950 z-30">Question & AI Response</th>
                    <th className="px-3 py-3 text-center w-20">Relevance</th>
                    <th className="px-3 py-3 text-center w-20">Accuracy</th>
                    <th className="px-3 py-3 text-center w-24">Hallucination</th>
                    <th className="px-3 py-3 text-center w-24">Completeness</th>
                    <th className="px-3 py-3 text-center w-20">Overall</th>
                    <th className="px-4 py-3 text-center w-36">Verdict</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {filteredItems.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-4 py-8 text-center text-slate-500 italic">
                        {items.length === 0
                          ? 'Evaluating items in real-time background worker...'
                          : 'No matching items found for current search or filter.'}
                      </td>
                    </tr>
                  ) : (
                    filteredItems.map((item) => (
                      <BatchTableRow
                        key={item.id}
                        item={item}
                        isExpanded={expandedRowId === item.id}
                        onToggleExpand={() => toggleRowExpanded(item.id)}
                      />
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
