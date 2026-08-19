import React from 'react'

interface VeridictLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  showText?: boolean
  showBadge?: boolean
  className?: string
  badgeText?: string
}

export const VeridictLogo: React.FC<VeridictLogoProps> = ({
  size = 'md',
  showText = true,
  showBadge = false,
  className = '',
  badgeText = 'ENTERPRISE',
}) => {
  const iconSizes = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-11 h-11',
    xl: 'w-14 h-14',
  }

  const textSizes = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-3xl',
  }

  return (
    <div className={`inline-flex items-center gap-3 select-none ${className}`}>
      {/* Modern High-Precision Vector Emblem */}
      <div className={`relative flex items-center justify-center ${iconSizes[size]} shrink-0 group`}>
        {/* Ambient Glow */}
        <div className="absolute inset-0 bg-gradient-to-tr from-amber-500/30 to-blue-500/20 rounded-xl blur-md transition-all duration-500 group-hover:scale-110 group-hover:blur-lg" />

        <svg
          viewBox="0 0 48 48"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="relative z-10 w-full h-full drop-shadow-[0_2px_8px_rgba(245,158,11,0.25)] transition-transform duration-300 group-hover:scale-105"
        >
          <defs>
            <linearGradient id="veridict-shield-grad" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#0F172A" />
              <stop offset="100%" stopColor="#1E293B" />
            </linearGradient>
            <linearGradient id="veridict-amber-grad" x1="12" y1="8" x2="36" y2="40" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#F59E0B" />
              <stop offset="60%" stopColor="#D97706" />
              <stop offset="100%" stopColor="#B45309" />
            </linearGradient>
            <linearGradient id="veridict-accent-grad" x1="8" y1="8" x2="40" y2="40" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="100%" stopColor="#0284C7" />
            </linearGradient>
          </defs>

          {/* Base Shield Container with Rounded Curves */}
          <rect
            x="4"
            y="4"
            width="40"
            height="40"
            rx="12"
            fill="url(#veridict-shield-grad)"
            stroke="#334155"
            strokeWidth="1.5"
          />

          {/* Verification Multi-Node Geometric Glyph */}
          {/* Outer Shield Facet */}
          <path
            d="M24 10L36 15.5V25C36 32 30.5 37.5 24 39.5C17.5 37.5 12 32 12 25V15.5L24 10Z"
            fill="none"
            stroke="url(#veridict-amber-grad)"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Inner Golden Neural Truth Core */}
          <circle cx="24" cy="24" r="3.5" fill="url(#veridict-amber-grad)" />

          {/* Verification Dynamic Beam / Check Crest */}
          <path
            d="M19 24.5L22.5 28L29.5 20.5"
            stroke="#FFFFFF"
            strokeWidth="2.4"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Multi-Agent Satellite Orbit Nodes */}
          <circle cx="16" cy="17" r="1.5" fill="#38BDF8" />
          <circle cx="32" cy="17" r="1.5" fill="#F59E0B" />
          <circle cx="24" cy="34" r="1.5" fill="#10B981" />
        </svg>
      </div>

      {/* Brand Typography */}
      {showText && (
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span
              className={`font-display font-extrabold tracking-tight text-slate-900 leading-none ${textSizes[size]}`}
            >
              Veridict
            </span>
            {showBadge && (
              <span className="px-1.5 py-0.5 text-[9px] font-bold tracking-wider uppercase bg-amber-50 text-amber-700 border border-amber-300/60 rounded-md">
                {badgeText}
              </span>
            )}
          </div>
          <span className="text-[11px] font-medium text-slate-500 tracking-wide mt-0.5">
            AI Quality Evaluation Engine
          </span>
        </div>
      )}
    </div>
  )
}
