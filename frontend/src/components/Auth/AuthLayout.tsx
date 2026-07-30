import React from 'react'

export const AuthLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-[#030304] text-slate-100 flex flex-col justify-between items-center relative overflow-x-hidden">
      {/* Subtle Radial Gradient & Pattern Background */}
      <div className="grid-bg" />
      <div className="absolute top-1/3 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-amber-500/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-amber-500/5 blur-[100px] rounded-full pointer-events-none" />

      {/* Main Container */}
      <main className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12 z-10 flex-1 flex items-center justify-center">
        {children}
      </main>

      {/* Footer */}
      <footer className="w-full py-4 text-center text-xs text-slate-500 font-sans border-t border-slate-900/60 z-10">
        Veridict AI Response Quality Evaluation Platform
      </footer>
    </div>
  )
}
