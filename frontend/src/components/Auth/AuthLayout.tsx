import React from 'react'
import { ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'

export const AuthLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between items-center p-4 relative overflow-hidden">
      {/* Subtle Background Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-amber-500/10 blur-3xl rounded-full pointer-events-none" />

      {/* Header Logo */}
      <header className="pt-8 pb-4 z-10">
        <Link to="/" className="flex items-center gap-2 text-lg font-bold font-display text-white hover:text-amber-400 transition-colors">
          <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <span>Veridict</span>
        </Link>
      </header>

      {/* Center Form Card */}
      <main className="w-full flex justify-center items-center py-6 z-10">
        {children}
      </main>

      {/* Clean Bottom Spacing / Tagline */}
      <footer className="pb-6 text-center text-xs text-slate-500 font-mono z-10">
        Continuous AI Evaluation Platform
      </footer>
    </div>
  )
}
