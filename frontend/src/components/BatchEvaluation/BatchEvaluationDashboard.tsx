/**
 * Veridict Batch Evaluation Dashboard Component.
 *
 * Product-level commercial AI engineering dashboard layout for bulk dataset evaluation.
 * SaaS file upload cards, contextual processing timeline stepper, segmented filter controls,
 * number-first metric cards, and sticky table headers/columns.
 */

import React, { useState, useEffect, useRef, useMemo } from 'react'
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
import { useEvaluation } from '@/context/EvaluationContext'
import { useDebounce } from '../../hooks'
import { HighlightMatch } from '../HighlightMatch'
import { searchEngine } from '../../search'

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
  const isCompleted = progress.status === 'COMPLETED'
  const [showDetails, setShowDetails] = useState(!isCompleted)

  const steps = [
    {
      num: 1,
      title: 'File Parsed',
      desc: `${progress.total_rows} QA pairs loaded into batch queue`,
      done: progress.processed_rows > 0 || isCompleted,
      active: progress.status === 'PROCESSING' && progress.processed_rows === 0,
    },
    {
      num: 2,
      title: 'LLM Batches Scheduled',
      desc: `${progress.current_batch} of ${progress.total_batches} batches executed`,
      done: isCompleted || (progress.current_batch > 1 && progress.current_batch <= progress.total_batches),
      active: progress.status === 'PROCESSING' && progress.current_batch > 0 && !isCompleted,
    },
    {
      num: 3,
      title: 'Judge Evaluation Complete',
      desc: isCompleted ? `Evaluated ${progress.total_rows} items successfully` : 'Aggregating judge scores...',
      done: isCompleted,
      active: progress.status === 'PROCESSING' && progress.current_batch === progress.total_batches && !isCompleted,
    },
    {
      num: 4,
      title: 'Export Ready',
      desc: isCompleted ? 'CSV & PDF Executive Reports ready for export' : 'Pending completion',
      done: isCompleted,
      active: false,
    },
  ]

  return (
    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-amber-400" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Pipeline Execution Timeline
          </h4>
        </div>
        <button
          type="button"
          onClick={() => setShowDetails(!showDetails)}
          className="text-xs font-semibold text-slate-400 hover:text-amber-400 transition-colors flex items-center gap-1"
        >
          {showDetails ? 'Collapse Details' : 'Expand Details'}
          {showDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {showDetails && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
          {steps.map((s) => {
            let statusText = 'Pending'
            if (s.done) statusText = 'Done'
            else if (s.active) statusText = 'Active'

            return (
              <div key={s.num} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/60 space-y-1">
                <div className="flex items-center justify-between">
                  <span className={`w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center ${getStageBadgeStyle(s.done, s.active)}`}>
                    {s.done ? <Check className="w-3 h-3" /> : s.num}
                  </span>
                  <span className={`text-[10px] font-mono ${getStageTextStyle(s.done, s.active)}`}>
                    {statusText}
                  </span>
                </div>
                <p className={`text-xs font-bold ${getStageTextStyle(s.done, s.active)}`}>{s.title}</p>
                <p className="text-[11px] text-slate-400 leading-tight">{s.desc}</p>
              </div>
            )
          })}
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

  const metrics = [
    { label: 'Total Items', val: totalCount, icon: Layers, color: 'text-white', tooltip: 'Total QA pairs evaluated in dataset' },
    { label: 'Pass Rate', val: `${passRate}%`, icon: ShieldCheck, color: 'text-emerald-400', tooltip: 'Percentage of responses passing overall score threshold' },
    { label: 'Needs Imp', val: impCount, icon: AlertTriangle, color: 'text-amber-400', tooltip: 'Responses requiring minor revisions' },
    { label: 'Failed', val: failCount, icon: XCircle, color: 'text-rose-400', tooltip: 'Responses with major factual issues' },
    { label: 'Avg Score', val: `${avgOverall} / 5`, icon: BarChart3, color: 'text-white', tooltip: 'Weighted average evaluation score across 4 dimensions' },
    { label: 'Avg Confidence', val: `${avgConfidence}%`, icon: Check, color: 'text-slate-200', tooltip: 'Average confidence returned by Gemini judge models' },
    { label: 'Duration', val: elapsedSeconds ? `${elapsedSeconds}s` : 'Active', icon: Clock, color: 'text-slate-200', tooltip: 'Total evaluation wall-clock duration' },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
      {metrics.map((m) => {
        const Icon = m.icon
        return (
          <div key={m.label} title={m.tooltip} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 hover:border-slate-700 transition-colors cursor-help flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className={`text-xl font-extrabold ${m.color}`}>{m.val}</span>
              <Icon className="w-4 h-4 text-slate-500" />
            </div>
            <span className="text-xs font-semibold text-slate-400 mt-2 block">{m.label}</span>
          </div>
        )
      })}
    </div>
  )
}

// ──────────────────────────────────────────────
// Sub-component: Batch Progress Monitor Component
// ──────────────────────────────────────────────
const BatchProgressMonitorCard: React.FC<{
  progress: BatchProgress
  onReset: () => void
  onExportCSV: () => void
  onExportPDF: () => void
  exportingCSV: boolean
  exportingPDF: boolean
}> = ({ progress, onReset, onExportCSV, onExportPDF, exportingCSV, exportingPDF }) => {
  const percent = progress.total_rows > 0 ? Math.round((progress.processed_rows / progress.total_rows) * 100) : 0
  const elapsedSeconds = progress.elapsed_seconds || (progress.statistics?.elapsed_seconds ?? null)
  const geminiCalls = progress.gemini_call_count || (progress.statistics?.gemini_call_count ?? (progress.total_batches || 1))

  let statusBadgeStyle = 'bg-amber-500/10 text-amber-400 border border-amber-500/30 animate-pulse'
  if (progress.status === 'COMPLETED') {
    statusBadgeStyle = 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
  } else if (progress.status === 'FAILED') {
    statusBadgeStyle = 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
  }

  return (
    <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
        <div>
          <div className="flex items-center gap-2.5">
            <h3 className="text-sm font-bold text-white">
              Batch Evaluation Job ({progress.batch_id})
            </h3>
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wide ${statusBadgeStyle}`}>
              {progress.status}
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
// Sub-component: Table Row with Sticky Question Column & Match Highlighting
// ──────────────────────────────────────────────
const BatchTableRow: React.FC<{
  item: BatchItemEvaluationResult
  isExpanded: boolean
  onToggleExpand: () => void
  searchQuery?: string
}> = ({ item, isExpanded, onToggleExpand, searchQuery }) => {
  return (
    <tr className="hover:bg-slate-800/40 even:bg-slate-900/30 transition-colors duration-150">
      <td className="px-3.5 py-3.5 font-mono text-amber-400 font-semibold align-top">
        <HighlightMatch text={item.id} query={searchQuery} />
      </td>

      {/* QA Pair & Reasoning Column */}
      <td className="px-3.5 sm:px-4 py-3.5 max-w-[200px] sm:max-w-xs md:max-w-xl space-y-1 align-top md:sticky md:left-0 bg-slate-950/95 border-r border-slate-800/80 z-10 backdrop-blur-sm">
        <div className="text-sm font-bold text-slate-100">
          Q: <HighlightMatch text={item.question} query={searchQuery} />
        </div>
        <div className="text-xs text-slate-300 leading-normal">
          A: <HighlightMatch text={item.ai_response} query={searchQuery} />
        </div>
        {item.reference_answer && (
          <div className="text-[11px] text-slate-400 leading-normal pt-0.5">
            <span className="text-slate-500 font-medium">Ref: </span>
            <HighlightMatch text={item.reference_answer} query={searchQuery} />
          </div>
        )}
        {item.reasoning && (
          <div className="pt-1">
            <div
              className={`text-[11px] text-slate-400 leading-relaxed font-mono ${
                !isExpanded ? 'line-clamp-2' : ''
              }`}
            >
              <span className="text-slate-500 font-sans font-medium">Reasoning: </span>
              <HighlightMatch text={item.reasoning} query={searchQuery} />
            </div>
            {item.reasoning.length > 120 && (
              <button
                onClick={onToggleExpand}
                className="text-[10px] font-semibold text-amber-400 hover:text-amber-300 mt-0.5 inline-flex items-center gap-0.5"
              >
                {isExpanded ? 'Show less' : 'Read full reasoning'}
              </button>
            )}
          </div>
        )}
      </td>

      <td className="px-3.5 py-3.5 font-mono font-bold align-top">
        {item.overall_score !== undefined ? (
          <span className="text-white">{item.overall_score.toFixed(2)}</span>
        ) : (
          <span className="text-slate-500">-</span>
        )}
      </td>

      <td className="px-3.5 py-3.5 font-mono text-xs align-top text-slate-300">
        {item.accuracy_score !== undefined ? item.accuracy_score.toFixed(1) : '-'}
      </td>
      <td className="px-3.5 py-3.5 font-mono text-xs align-top text-slate-300">
        {item.relevance_score !== undefined ? item.relevance_score.toFixed(1) : '-'}
      </td>
      <td className="px-3.5 py-3.5 font-mono text-xs align-top text-slate-300">
        {item.completeness_score !== undefined ? item.completeness_score.toFixed(1) : '-'}
      </td>
      <td className="px-3.5 py-3.5 font-mono text-xs align-top text-slate-300">
        {item.hallucination_score !== undefined && item.hallucination_score !== null ? item.hallucination_score.toFixed(1) : '-'}
      </td>

      <td className="px-3.5 py-3.5 align-top">
        <SoftVerdictBadge verdict={item.verdict} />
      </td>

      <td className="px-3.5 py-3.5 font-mono text-xs text-slate-400 align-top">
        {item.confidence !== undefined ? `${(item.confidence * 100).toFixed(0)}%` : '-'}
      </td>
    </tr>
  )
}

// ──────────────────────────────────────────────
// Sub-component: Batch Upload Form Card
// ──────────────────────────────────────────────
const BatchUploadForm: React.FC<{
  mode: 'CSV' | 'PDF'
  onModeChange: (m: 'CSV' | 'PDF') => void
  batchFile: File | null
  onSetBatchFile: (f: File | null) => void
  evidencePdf: File | null
  onSetEvidencePdf: (f: File | null) => void
  onSubmit: (e: React.SyntheticEvent) => void
  loading: boolean
}> = ({
  mode,
  onModeChange,
  batchFile,
  onSetBatchFile,
  evidencePdf,
  onSetEvidencePdf,
  onSubmit,
  loading,
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
                }}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div className="flex flex-col items-center gap-2">
                <Upload className="w-7 h-7 text-slate-500 group-hover:scale-105 transition-transform duration-150" />
                <span className="text-xs font-bold text-slate-300">
                  📚 Context Evidence — Drag & Drop or Browse Files
                </span>
                <span className="text-[10px] text-slate-400">
                  Used for grounding & RAG evidence retrieval
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-400">Dataset Format:</span>
          <div className="inline-flex p-0.5 rounded-lg bg-slate-950 border border-slate-800">
            <button
              type="button"
              onClick={() => onModeChange('CSV')}
              className={`px-3 py-1 text-xs font-bold rounded-md transition-colors ${
                mode === 'CSV' ? 'bg-amber-500 text-slate-950' : 'text-slate-400 hover:text-white'
              }`}
            >
              CSV File
            </button>
            <button
              type="button"
              onClick={() => onModeChange('PDF')}
              className={`px-3 py-1 text-xs font-bold rounded-md transition-colors ${
                mode === 'PDF' ? 'bg-amber-500 text-slate-950' : 'text-slate-400 hover:text-white'
              }`}
            >
              Digital QA PDF
            </button>
          </div>
        </div>

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
  const { batchState, updateBatchState, clearBatchState } = useEvaluation()

  const [mode, setMode] = useState<'CSV' | 'PDF'>('CSV')
  const [batchFile, setBatchFile] = useState<File | null>(null)
  const [evidencePdf, setEvidencePdf] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [exportingCSV, setExportingCSV] = useState(false)
  const [exportingPDF, setExportingPDF] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const progress = batchState.batchProgress
  const [verdictFilter, setVerdictFilter] = useState<'ALL' | 'PASS' | 'NEEDS_IMPROVEMENT' | 'FAIL'>('ALL')
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedRowId, setExpandedRowId] = useState<string | null>(null)

  const debouncedSearchTerm = useDebounce(searchTerm, 250)

  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const handlePollUpdate = (updated: BatchProgress) => {
    const items = updated.items || (updated as any).results || []
    updateBatchState({
      batchProgress: updated,
      batchResults: items,
    })
    if (updated.status === 'COMPLETED' || updated.status === 'FAILED') {
      if (pollingRef.current) clearInterval(pollingRef.current)
      if (updated.status === 'FAILED') {
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
    updateBatchState({ batchProgress: null, batchResults: [] })

    try {
      let initialProgress: BatchProgress
      if (mode === 'CSV') {
        initialProgress = await evaluateBatchCSV(batchFile, evidencePdf || undefined)
      } else {
        initialProgress = await evaluateBatchPDF(batchFile, evidencePdf || undefined)
      }
      const initialItems = initialProgress.items || (initialProgress as any).results || []
      updateBatchState({
        batchId: initialProgress.batch_id,
        batchProgress: initialProgress,
        batchResults: initialItems,
        batchFileMetadata: { name: batchFile.name, size: batchFile.size, type: batchFile.type },
      })
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
    try {
      await exportBatchCSV(progress.batch_id)
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
    try {
      await exportBatchPDF(progress.batch_id)
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
    setError(null)
    clearBatchState()
  }

  const toggleRowExpanded = (id: string) => {
    setExpandedRowId((prev) => (prev === id ? null : id))
  }

  const rawResults: BatchItemEvaluationResult[] = progress?.items || (progress as any)?.results || batchState.batchResults || []

  // Centralized Global Search Engine pipeline invocation
  const searchResult = useMemo(() => {
    return searchEngine.search({
      items: rawResults,
      query: debouncedSearchTerm,
      filters: {
        verdict: verdictFilter,
      },
    })
  }, [rawResults, debouncedSearchTerm, verdictFilter])

  const filteredResults = searchResult.items

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="font-display text-xl font-extrabold tracking-tight text-white">
              Batch Evaluation Engine
            </h2>
            <span className="px-2.5 py-0.5 text-[10px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/30 rounded-full">
              Production Mode
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Bulk evaluation pipeline supporting up to 30 QA pairs with grouped LLM processing.
          </p>
          <CategorizedCapabilities />
        </div>

        {progress && (
          <button
            onClick={resetForm}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-bold text-slate-200 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition-colors self-start md:self-auto"
          >
            <RefreshCw className="w-3.5 h-3.5 text-amber-400" />
            New Batch
          </button>
        )}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Primary Section: Upload Form OR Progress Monitor */}
      {!progress ? (
        <BatchUploadForm
          mode={mode}
          onModeChange={setMode}
          batchFile={batchFile}
          onSetBatchFile={setBatchFile}
          evidencePdf={evidencePdf}
          onSetEvidencePdf={setEvidencePdf}
          onSubmit={handleSubmit}
          loading={loading}
        />
      ) : (
        <div className="space-y-4">
          <BatchProgressMonitorCard
            progress={progress}
            onReset={resetForm}
            onExportCSV={handleExportCSV}
            onExportPDF={handleExportPDF}
            exportingCSV={exportingCSV}
            exportingPDF={exportingPDF}
          />
          <ProcessingTimelineStepper progress={progress} />
        </div>
      )}

      {/* Metrics Cards Grid (When results exist) */}
      {progress && rawResults.length > 0 && (
        <MetricCardsGrid items={rawResults} progress={progress} />
      )}

      {/* Dataset Filter & Results Table */}
      {progress && rawResults.length > 0 && (
        <div className="space-y-4">
          {/* Segmented Filter Controls & Search */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center gap-1 overflow-x-auto pb-1 sm:pb-0">
              <Filter className="w-3.5 h-3.5 text-slate-500 mr-2 flex-shrink-0" />
              {(['ALL', 'PASS', 'NEEDS_IMPROVEMENT', 'FAIL'] as const).map((filterVal) => (
                <button
                  key={filterVal}
                  onClick={() => setVerdictFilter(filterVal)}
                  className={`px-3 py-1 rounded-lg text-xs font-bold transition-all flex-shrink-0 ${
                    verdictFilter === filterVal
                      ? 'bg-amber-500 text-slate-950 shadow-xs'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  {filterVal === 'ALL' ? 'All Items' : filterVal.replace('_', ' ')}
                  <span className="ml-1.5 text-[10px] opacity-75 font-mono">
                    ({filterVal === 'ALL' ? rawResults.length : rawResults.filter((i: BatchItemEvaluationResult) => i.verdict === filterVal).length})
                  </span>
                </button>
              ))}
            </div>

            <div className="relative w-full sm:w-72">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search questions, answers, reasoning..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-8 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500/60 transition-colors"
              />
              {searchTerm && (
                <button
                  type="button"
                  onClick={() => setSearchTerm('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 p-0.5 text-slate-500 hover:text-white rounded transition-colors"
                  title="Clear search"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Results Table with Sticky Headers & Columns */}
          <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950/80 shadow-xl">
            <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-slate-900 border-b border-slate-800 sticky top-0 z-20 shadow-md">
                  <tr>
                    <th className="px-3.5 py-3 font-bold uppercase tracking-wider text-slate-400 w-16">ID</th>
                    <th className="px-3.5 sm:px-4 py-3 font-bold uppercase tracking-wider text-slate-400 md:sticky md:left-0 bg-slate-900 border-r border-slate-800 z-30 min-w-[160px]">
                      QA Pair & Reasoning
                    </th>
                    <th className="px-3.5 py-3 font-bold uppercase tracking-wider text-slate-300 w-24">Overall</th>
                    <th className="px-3.5 py-3 font-semibold uppercase tracking-wider text-slate-400 w-20">Accuracy</th>
                    <th className="px-3.5 py-3 font-semibold uppercase tracking-wider text-slate-400 w-20">Relevance</th>
                    <th className="px-3.5 py-3 font-semibold uppercase tracking-wider text-slate-400 w-20">Complete</th>
                    <th className="px-3.5 py-3 font-semibold uppercase tracking-wider text-slate-400 w-20">Grounding</th>
                    <th className="px-3.5 py-3 font-bold uppercase tracking-wider text-slate-300 w-28">Verdict</th>
                    <th className="px-3.5 py-3 font-semibold uppercase tracking-wider text-slate-400 w-20">Conf</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {filteredResults.map((item: BatchItemEvaluationResult) => (
                    <BatchTableRow
                      key={item.id}
                      item={item}
                      isExpanded={expandedRowId === item.id}
                      onToggleExpand={() => toggleRowExpanded(item.id)}
                      searchQuery={debouncedSearchTerm}
                    />
                  ))}
                  {filteredResults.length === 0 && (
                    <tr>
                      <td colSpan={9} className="px-4 py-12 text-center">
                        <div className="space-y-3 max-w-md mx-auto">
                          <div className="w-10 h-10 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto text-slate-400">
                            <Search className="w-5 h-5" />
                          </div>
                          <div className="space-y-1">
                            <p className="text-sm font-bold text-slate-300">
                              No evaluations match your search
                            </p>
                            <p className="text-xs text-slate-500">
                              {debouncedSearchTerm
                                ? `No results found for "${debouncedSearchTerm}". Try checking for typos or clearing filters.`
                                : 'No batch items match the selected filter criteria.'}
                            </p>
                          </div>
                          {(searchTerm || verdictFilter !== 'ALL') && (
                            <button
                              type="button"
                              onClick={() => {
                                setSearchTerm('')
                                setVerdictFilter('ALL')
                              }}
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-amber-400 hover:text-amber-300 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg transition-colors"
                            >
                              <X className="w-3.5 h-3.5" />
                              Clear Search & Filters
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
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
