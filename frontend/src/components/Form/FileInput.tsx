import React, { useRef, useState } from 'react'
import { cn } from '@/utils'
import { Upload, FileText, X } from 'lucide-react'

interface FileInputProps {
  readonly label: string
  readonly id: string
  readonly file: File | null
  readonly onChange: (file: File | null) => void
  readonly accept?: string
  readonly maxSizeMB?: number
}

export function FileInput({
  label,
  id,
  file,
  onChange,
  accept = 'application/pdf',
  maxSizeMB = 10,
}: FileInputProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const processFile = (selectedFile: File) => {
    if (selectedFile.type !== accept) {
      alert(`Only ${accept.replace('application/', '').toUpperCase()} files are supported.`)
      return
    }
    if (selectedFile.size > maxSizeMB * 1024 * 1024) {
      alert(`File size exceeds the ${maxSizeMB}MB limit.`)
      return
    }
    onChange(selectedFile)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0])
    }
  }

  const removeFile = () => {
    onChange(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="flex flex-col gap-2 w-full group">
      <div className="flex justify-between items-center">
        <label htmlFor={id} className="text-xs font-semibold tracking-wider uppercase text-text-secondary group-focus-within:text-primary transition-colors duration-300">
          {label}
        </label>
        <span className="text-[10px] text-muted-foreground uppercase tracking-widest">Optional PDF</span>
      </div>

      <input
        type="file"
        id={id}
        ref={fileInputRef}
        onChange={handleFileChange}
        accept={accept}
        className="hidden"
      />

      {file === null ? (
        <button
          type="button"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            "w-full flex flex-col items-center justify-center border border-dashed rounded-xl p-8 cursor-pointer transition-all duration-300 bg-background/20 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary focus:shadow-glow-sm",
            isDragging 
              ? "border-primary bg-primary-muted/10 shadow-glow-sm" 
              : "border-border hover:border-border-hover hover:bg-background/30"
          )}
        >
          <span className="flex items-center justify-center w-10 h-10 rounded-full bg-surface-elevated text-muted mb-3 group-hover:text-primary transition-colors">
            <Upload size={18} />
          </span>
          <span className="text-sm font-medium text-text-secondary">
            Drag & drop your PDF here, or <span className="text-primary hover:underline">browse</span>
          </span>
          <span className="text-xs text-muted-foreground mt-1">
            Supports only PDF files (Max {maxSizeMB}MB)
          </span>
        </button>
      ) : (
        <div className="flex items-center justify-between p-4 bg-surface-elevated/40 border border-border hover:border-border-hover/120 rounded-xl transition-all duration-300">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary-muted/20 text-primary shrink-0">
              <FileText size={20} />
            </div>
            <div className="flex flex-col overflow-hidden">
              <span className="text-sm font-medium text-text-primary truncate">
                {file.name}
              </span>
              <span className="text-xs text-muted-foreground">
                {(file.size / (1024 * 1024)).toFixed(2)} MB
              </span>
            </div>
          </div>
          <button
            type="button"
            onClick={removeFile}
            className="p-1.5 rounded-lg text-muted hover:text-error hover:bg-error/10 transition-colors"
            aria-label="Remove file"
          >
            <X size={16} />
          </button>
        </div>
      )}
    </div>
  )
}

