import React from 'react'
import { Navigate, useLocation, Outlet } from 'react-router-dom'
import { useAuth } from '@/context/useAuth'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children?: React.ReactNode
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading, loadingProfile, isAuthenticated } = useAuth()
  const location = useLocation()

  // Render loading screen strictly when initial session restoration is pending and user identity is unknown
  if (loading || (!user && loadingProfile)) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-3 text-slate-300">
        <Loader2 className="w-8 h-8 animate-spin text-amber-400" />
        <p className="text-xs font-medium tracking-wide text-slate-400">Verifying session...</p>
      </div>
    )
  }

  if (!isAuthenticated()) {
    const redirectPath = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/login?redirect=${redirectPath}`} state={{ from: location }} replace />
  }

  return children ? <>{children}</> : <Outlet />
}

export default ProtectedRoute
