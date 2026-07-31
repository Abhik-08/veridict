import { AlertTriangle, Trash2, X, Loader2 } from 'lucide-react'

interface BulkDeleteConfirmationModalProps {
  isOpen: boolean
  selectedCount: number
  onClose: () => void
  onConfirm: () => void
  isDeleting: boolean
}

export function BulkDeleteConfirmationModal({
  isOpen,
  selectedCount,
  onClose,
  onConfirm,
  isDeleting,
}: Readonly<BulkDeleteConfirmationModalProps>) {
  if (!isOpen || selectedCount === 0) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4">
      {/* Backdrop overlay */}
      <button
        type="button"
        aria-label="Close modal background backdrop"
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md border-0 cursor-default animate-fade-in w-full h-full"
        onClick={onClose}
        disabled={isDeleting}
      />

      {/* Modal Dialog Box */}
      <div className="relative z-10 w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-6 shadow-2xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">
                Delete {selectedCount} Evaluation Record{selectedCount > 1 ? 's' : ''}?
              </h3>
              <p className="text-xs text-slate-400">This action cannot be undone.</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            className="p-1 text-slate-400 hover:text-white rounded-lg cursor-pointer disabled:opacity-50"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Are you sure you want to permanently delete the <strong className="text-amber-400 font-bold">{selectedCount}</strong> manually selected evaluation records from your history?
        </p>

        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-800">
          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl transition-colors cursor-pointer disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isDeleting}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-500 rounded-xl transition-colors cursor-pointer shadow-md disabled:opacity-50"
          >
            {isDeleting ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Deleting {selectedCount} records...</span>
              </>
            ) : (
              <>
                <Trash2 className="w-3.5 h-3.5" />
                <span>Delete {selectedCount} Records</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
