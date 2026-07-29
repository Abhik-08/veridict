/**
 * Veridict Batch Evaluation API Service.
 */

import { api } from './api'
import type { BatchProgress } from '../types'

export async function evaluateBatchCSV(
  csvFile: File,
  evidencePdf?: File
): Promise<BatchProgress> {
  const formData = new FormData()
  formData.append('file', csvFile)
  if (evidencePdf) {
    formData.append('evidence_pdf', evidencePdf)
  }

  const response = await api.post<BatchProgress>(
    '/evaluate/batch/csv',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )
  return response.data
}

export async function evaluateBatchPDF(
  pdfFile: File,
  evidencePdf?: File
): Promise<BatchProgress> {
  const formData = new FormData()
  formData.append('file', pdfFile)
  if (evidencePdf) {
    formData.append('evidence_pdf', evidencePdf)
  }

  const response = await api.post<BatchProgress>(
    '/evaluate/batch/pdf',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )
  return response.data
}

export async function getBatchProgress(batchId: string): Promise<BatchProgress> {
  const response = await api.get<BatchProgress>(
    `/evaluate/batch/progress/${batchId}`
  )
  return response.data
}

export async function exportBatchCSV(batchId: string): Promise<void> {
  const response = await api.get(`/evaluate/batch/export-csv/${batchId}`, {
    responseType: 'blob',
  })
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `veridict_batch_eval_${batchId}.csv`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export async function exportBatchPDF(batchId: string): Promise<void> {
  const response = await api.get(`/evaluate/batch/export-pdf/${batchId}`, {
    responseType: 'blob',
  })
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `veridict_batch_report_${batchId}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
