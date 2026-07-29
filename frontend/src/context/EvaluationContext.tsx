import React, { createContext, useContext, useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { useAuth } from '@/context/useAuth'
import type { BatchProgress, BatchItemEvaluationResult, EvaluationResultData } from '@/types'

export interface FileMetadata {
  name: string
  size: number
  type: string
}

export interface SingleEvaluationState {
  question: string
  response: string
  reference: string
  fileMetadata: FileMetadata | null
  evaluationResult: EvaluationResultData | null
}

export interface BatchEvaluationState {
  batchId: string | null
  batchProgress: BatchProgress | null
  batchResults: BatchItemEvaluationResult[]
  batchFileMetadata: FileMetadata | null
}

interface EvaluationContextType {
  engineMode: 'single' | 'batch'
  setEngineMode: (mode: 'single' | 'batch') => void

  singleState: SingleEvaluationState
  updateSingleState: (updates: Partial<SingleEvaluationState>) => void
  clearSingleState: () => void

  batchState: BatchEvaluationState
  updateBatchState: (updates: Partial<BatchEvaluationState>) => void
  clearBatchState: () => void

  clearAllEvaluationState: () => void
}

const DEFAULT_SINGLE_STATE: SingleEvaluationState = {
  question: '',
  response: '',
  reference: '',
  fileMetadata: null,
  evaluationResult: null,
}

const DEFAULT_BATCH_STATE: BatchEvaluationState = {
  batchId: null,
  batchProgress: null,
  batchResults: [],
  batchFileMetadata: null,
}

const EvaluationContext = createContext<EvaluationContextType | undefined>(undefined)

export const EvaluationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth()
  const storageKey = useMemo(() => {
    return user?.id ? `veridict_eval_state_${user.id}` : 'veridict_eval_state_guest'
  }, [user?.id])

  const [engineMode, setEngineMode] = useState<'single' | 'batch'>('single')
  const [singleState, setSingleState] = useState<SingleEvaluationState>(DEFAULT_SINGLE_STATE)
  const [batchState, setBatchState] = useState<BatchEvaluationState>(DEFAULT_BATCH_STATE)
  const isRestoredRef = useRef<boolean>(false)

  // Restore state from localStorage when storageKey changes (e.g. on mount or login change)
  useEffect(() => {
    try {
      const saved = localStorage.getItem(storageKey)
      if (saved) {
        const parsed = JSON.parse(saved)
        if (parsed.engineMode) setEngineMode(parsed.engineMode)
        if (parsed.singleState) setSingleState(parsed.singleState)
        if (parsed.batchState) setBatchState(parsed.batchState)
      } else {
        setSingleState(DEFAULT_SINGLE_STATE)
        setBatchState(DEFAULT_BATCH_STATE)
        setEngineMode('single')
      }
    } catch (err) {
      console.warn('[EvaluationContext] Could not restore evaluation state:', err)
    } finally {
      isRestoredRef.current = true
    }
  }, [storageKey])

  // Persist state to localStorage on state changes
  useEffect(() => {
    if (!isRestoredRef.current) return
    try {
      const dataToSave = {
        engineMode,
        singleState,
        batchState,
      }
      localStorage.setItem(storageKey, JSON.stringify(dataToSave))
    } catch (err) {
      console.warn('[EvaluationContext] Could not persist evaluation state:', err)
    }
  }, [storageKey, engineMode, singleState, batchState])

  const updateSingleState = useCallback((updates: Partial<SingleEvaluationState>) => {
    setSingleState((prev) => ({ ...prev, ...updates }))
  }, [])

  const clearSingleState = useCallback(() => {
    setSingleState(DEFAULT_SINGLE_STATE)
  }, [])

  const updateBatchState = useCallback((updates: Partial<BatchEvaluationState>) => {
    setBatchState((prev) => ({ ...prev, ...updates }))
  }, [])

  const clearBatchState = useCallback(() => {
    setBatchState(DEFAULT_BATCH_STATE)
  }, [])

  const clearAllEvaluationState = useCallback(() => {
    setSingleState(DEFAULT_SINGLE_STATE)
    setBatchState(DEFAULT_BATCH_STATE)
    setEngineMode('single')
    try {
      localStorage.removeItem(storageKey)
    } catch (err) {
      console.warn('[EvaluationContext] Error clearing storage:', err)
    }
  }, [storageKey])

  const value = useMemo(
    () => ({
      engineMode,
      setEngineMode,
      singleState,
      updateSingleState,
      clearSingleState,
      batchState,
      updateBatchState,
      clearBatchState,
      clearAllEvaluationState,
    }),
    [
      engineMode,
      setEngineMode,
      singleState,
      updateSingleState,
      clearSingleState,
      batchState,
      updateBatchState,
      clearBatchState,
      clearAllEvaluationState,
    ]
  )

  return <EvaluationContext.Provider value={value}>{children}</EvaluationContext.Provider>
}

export const useEvaluation = (): EvaluationContextType => {
  const context = useContext(EvaluationContext)
  if (!context) {
    throw new Error('useEvaluation must be used within an EvaluationProvider')
  }
  return context
}
