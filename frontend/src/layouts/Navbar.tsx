import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import logoSrc from '@/assets/logo.png'
import { useAuth } from '@/context/useAuth'
import { LogOut, User as UserIcon, LayoutDashboard, History, Sparkles, Menu, X } from 'lucide-react'

export function Navbar() {
  const { user, profile, logout } = useAuth()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const displayName = profile?.full_name || profile?.email || user?.email || 'User'
  const avatarUrl = profile?.avatar_url

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/' || location.pathname === '/dashboard'
    return location.pathname === path
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-50">
      {/* Backdrop blur bar */}
      <div className="absolute inset-0 bg-background/60 backdrop-blur-2xl border-b border-border" />

      <nav className="relative section-container flex items-center justify-between h-[72px]">
        {/* Left: Logo + Title */}
        <Link to="/" className="flex items-center gap-3.5 group" onClick={() => setMobileMenuOpen(false)}>
          <img
            src={logoSrc}
            alt="Veridict Logo"
            className="h-[3.6rem] w-[3.6rem] object-contain rounded-md transition-transform duration-300 group-hover:scale-105"
          />
          <div className="flex flex-col">
            <span className="font-display text-xl font-bold tracking-tight text-text-primary leading-tight">
              Veridict
            </span>
            <span className="text-[11px] text-muted-foreground tracking-wide leading-tight hidden sm:block">
              AI Response Quality Evaluator
            </span>
          </div>
        </Link>

        {/* Center: Navigation Links */}
        {user && (
          <div className="hidden md:flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/90 border border-slate-800 shadow-md">
            <Link
              to="/"
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg font-medium text-xs transition-all ${
                isActive('/')
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <LayoutDashboard size={14} />
              Dashboard
            </Link>

            <Link
              to="/evaluator"
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg font-medium text-xs transition-all ${
                isActive('/evaluator')
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Sparkles size={14} />
              Evaluator
            </Link>

            <Link
              to="/history"
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg font-medium text-xs transition-all ${
                isActive('/history')
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <History size={14} />
              History
            </Link>
          </div>
        )}

        {/* Right side: Auth Controls */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-2.5">
              <span className="text-xs text-slate-300 font-medium hidden sm:flex items-center gap-2 bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-800">
                {avatarUrl ? (
                  <img src={avatarUrl} alt="Avatar" className="w-4 h-4 rounded-full object-cover" />
                ) : (
                  <UserIcon className="w-3.5 h-3.5 text-amber-400" />
                )}
                <span className="max-w-[160px] truncate">{displayName}</span>
              </span>
              <button
                onClick={() => logout()}
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 rounded-lg border border-slate-800 transition-colors cursor-pointer"
                title="Sign Out"
              >
                <LogOut className="w-3.5 h-3.5 text-rose-400" />
                <span>Sign Out</span>
              </button>

              {/* Mobile Hamburger Menu Button */}
              <button
                onClick={() => setMobileMenuOpen((prev) => !prev)}
                className="md:hidden flex items-center justify-center p-2 rounded-lg text-slate-300 hover:text-white bg-slate-900/90 border border-slate-800 transition-colors cursor-pointer min-w-[44px] min-h-[44px]"
                aria-label="Toggle Navigation Menu"
              >
                {mobileMenuOpen ? <X size={20} className="text-amber-400" /> : <Menu size={20} />}
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="px-4 py-2 text-xs font-bold text-slate-950 bg-amber-500 hover:bg-amber-600 rounded-lg transition-colors shadow-xs flex items-center min-h-[38px]"
            >
              Sign In
            </Link>
          )}
        </div>
      </nav>

      {/* Mobile Drawer Dropdown Menu */}
      {user && mobileMenuOpen && (
        <div className="md:hidden relative z-50 bg-slate-950/95 backdrop-blur-2xl border-b border-slate-800 px-4 py-4 space-y-3 animate-fade-in shadow-2xl">
          <div className="flex items-center gap-2.5 px-3 py-2 rounded-xl bg-slate-900/90 border border-slate-800/80 mb-2">
            {avatarUrl ? (
              <img src={avatarUrl} alt="Avatar" className="w-6 h-6 rounded-full object-cover" />
            ) : (
              <UserIcon className="w-4 h-4 text-amber-400" />
            )}
            <span className="text-xs font-semibold text-slate-200 truncate flex-1">{displayName}</span>
          </div>

          <div className="flex flex-col gap-1.5">
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-xs transition-all min-h-[44px] ${
                isActive('/')
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                  : 'text-slate-300 hover:text-white hover:bg-slate-900'
              }`}
            >
              <LayoutDashboard size={16} />
              <span>Dashboard</span>
            </Link>

            <Link
              to="/evaluator"
              onClick={() => setMobileMenuOpen(false)}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-xs transition-all min-h-[44px] ${
                isActive('/evaluator')
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                  : 'text-slate-300 hover:text-white hover:bg-slate-900'
              }`}
            >
              <Sparkles size={16} />
              <span>Evaluator Engine</span>
            </Link>

            <Link
              to="/history"
              onClick={() => setMobileMenuOpen(false)}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-xs transition-all min-h-[44px] ${
                isActive('/history')
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                  : 'text-slate-300 hover:text-white hover:bg-slate-900'
              }`}
            >
              <History size={16} />
              <span>Evaluation History</span>
            </Link>
          </div>

          <div className="pt-2 border-t border-slate-800">
            <button
              onClick={() => {
                setMobileMenuOpen(false)
                logout()
              }}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-xs font-semibold text-rose-300 hover:text-rose-200 bg-rose-500/10 hover:bg-rose-500/20 rounded-xl border border-rose-500/30 transition-colors cursor-pointer min-h-[44px]"
            >
              <LogOut className="w-4 h-4 text-rose-400" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </header>
  )
}
