import React from 'react'
import { Link } from 'react-router-dom'
import { VeridictLogo } from '@/components/Brand/VeridictLogo'

export const AuthLightLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-[#FFF9F2] text-slate-900 flex flex-col justify-between relative overflow-x-hidden selection:bg-amber-200 selection:text-amber-950">
      {/* Rich Warm Sunset Orange & Amber Radiant Background Canvas */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {/* Multi-Stop Warm Ambient Mesh Gradient */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,_var(--tw-gradient-stops))] from-amber-200/40 via-[#FFF5E8] to-[#FDE8D0]" />

        {/* Static Warm Amber / Orange Luminous Orbs */}
        <div className="absolute -top-[15%] left-[5%] w-[720px] h-[720px] bg-gradient-to-br from-amber-400/35 via-orange-300/25 to-transparent rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-[15%] -right-[8%] w-[680px] h-[680px] bg-gradient-to-bl from-orange-400/30 via-amber-300/20 to-transparent rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute -bottom-[15%] left-[25%] w-[600px] h-[600px] bg-gradient-to-tr from-amber-300/30 via-orange-200/20 to-transparent rounded-full blur-[110px] pointer-events-none" />

        {/* Soft Warm Micro-Grid */}
        <div
          className="absolute inset-0 opacity-[0.38]"
          style={{
            backgroundImage: `radial-gradient(#EA580C 0.85px, transparent 0.85px)`,
            backgroundSize: '30px 30px',
            maskImage: 'radial-gradient(ellipse 90% 75% at 50% 35%, black 40%, transparent 100%)',
            WebkitMaskImage: 'radial-gradient(ellipse 90% 75% at 50% 35%, black 40%, transparent 100%)',
          }}
        />
      </div>

      {/* Top Header Bar */}
      <header className="relative z-20 w-full border-b border-amber-900/10 bg-white/75 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-15 flex items-center justify-between">
          <Link to="/" className="hover:opacity-90 transition-opacity flex items-center gap-2">
            <VeridictLogo size="sm" showBadge={false} />
          </Link>

          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100/70 border border-amber-300/70 text-amber-900 text-xs font-semibold shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-[11px] font-medium tracking-tight text-amber-950">Multi-Agent Engine Active</span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 flex-1 flex items-center justify-center">
        {children}
      </main>

      {/* Clean Minimalist Footer */}
      <footer className="relative z-20 w-full border-t border-amber-900/10 bg-white/70 backdrop-blur-md py-3.5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-amber-950/70 font-medium">
          <p>© {new Date().getFullYear()} Veridict • Development of AI Response Validation System with Hallucination Detection Assistance</p>
        </div>
      </footer>
    </div>
  )
}
