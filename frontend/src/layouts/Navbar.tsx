import { Link } from 'react-router-dom'
import logoSrc from '@/assets/logo.png'
import { useAuth } from '@/context/useAuth'
import { LogOut, User as UserIcon } from 'lucide-react'

export function Navbar() {
  const { user, profile, logout } = useAuth()

  const displayName = profile?.full_name || profile?.email || user?.email || 'User'
  const avatarUrl = profile?.avatar_url

  return (
    <header className="fixed top-0 left-0 right-0 z-50">
      {/* Backdrop blur bar */}
      <div className="absolute inset-0 bg-background/60 backdrop-blur-2xl border-b border-border" />

      <nav className="relative section-container flex items-center justify-between h-[72px]">
        {/* Left: Logo + Title */}
        <Link to="/" className="flex items-center gap-3.5 group">
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

        {/* Right side: Auth Controls */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
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
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 rounded-lg border border-slate-800 transition-colors cursor-pointer"
                title="Sign Out"
              >
                <LogOut className="w-3.5 h-3.5 text-rose-400" />
                <span>Sign Out</span>
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="px-4 py-1.5 text-xs font-bold text-slate-950 bg-amber-500 hover:bg-amber-600 rounded-lg transition-colors shadow-xs"
            >
              Sign In
            </Link>
          )}
        </div>
      </nav>
    </header>
  )
}
