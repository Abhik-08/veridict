import React, { createContext, useEffect, useState, useCallback, useMemo, useRef } from 'react'
import type { User, Session, AuthChangeEvent } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'
import { syncProfile, getMe, type UserProfile } from '@/services/authService'

export interface AuthContextType {
  user: User | null
  session: Session | null
  profile: UserProfile | null
  loading: boolean
  loadingProfile: boolean
  isAuthenticated: () => boolean
  requireAuth: () => boolean
  refreshProfile: () => Promise<void>
  login: (email: string, pass: string) => Promise<{ error: Error | null }>
  register: (email: string, pass: string) => Promise<{ data: any; error: Error | null }>
  loginWithGoogle: () => Promise<{ error: Error | null }>
  resetPassword: (email: string) => Promise<{ error: Error | null }>
  logout: () => Promise<{ error: Error | null }>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [loadingProfile, setLoadingProfile] = useState<boolean>(false)

  const syncedUserIdRef = useRef<string | null>(null)
  const syncInProgressRef = useRef<boolean>(false)
  const lastAccessTokenRef = useRef<string | null>(null)

  const isAuthenticated = useCallback((): boolean => {
    return Boolean(user && session)
  }, [user, session])

  const requireAuth = useCallback((): boolean => {
    return Boolean(user && session)
  }, [user, session])

  // Stable profile sync callback using refs to prevent duplicate HTTP requests
  const handleProfileSync = useCallback(async (accessToken: string, userId: string, force = false) => {
    if (syncInProgressRef.current) return
    if (!force && syncedUserIdRef.current === userId) return

    syncInProgressRef.current = true
    setLoadingProfile(true)

    try {
      const synced = await syncProfile(accessToken)
      setProfile(synced)
      syncedUserIdRef.current = userId
    } catch (err) {
      syncedUserIdRef.current = null
      console.warn('[AuthContext] Could not auto-sync user profile:', err)
    } finally {
      syncInProgressRef.current = false
      setLoadingProfile(false)
    }
  }, [])

  const refreshProfile = useCallback(async () => {
    if (!session?.access_token || !user?.id) return
    if (syncInProgressRef.current) return

    syncInProgressRef.current = true
    setLoadingProfile(true)
    try {
      const p = await getMe(session.access_token)
      setProfile(p)
      syncedUserIdRef.current = user.id
    } catch (err) {
      console.warn('[AuthContext] Could not refresh profile:', err)
    } finally {
      syncInProgressRef.current = false
      setLoadingProfile(false)
    }
  }, [session?.access_token, user?.id])

  // Initial Auth Lifecycle Mounting Effect
  useEffect(() => {
    // 1. Initial Session Restoration
    supabase.auth
      .getSession()
      .then(({ data: { session: currentSession } }) => {
        lastAccessTokenRef.current = currentSession?.access_token ?? null
        setSession(currentSession)
        setUser(currentSession?.user ?? null)
        setLoading(false)

        if (currentSession?.access_token && currentSession.user?.id) {
          handleProfileSync(currentSession.access_token, currentSession.user.id, false)
        }
      })
      .catch((err) => {
        console.error('[AuthContext] Error restoring session:', err)
        setLoading(false)
      })

    // 2. Register Auth State Listener
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event: AuthChangeEvent, currentSession) => {
      const token = currentSession?.access_token ?? null
      const tokenChanged = token !== lastAccessTokenRef.current

      if (event === 'SIGNED_OUT' || !currentSession) {
        lastAccessTokenRef.current = null
        syncedUserIdRef.current = null
        syncInProgressRef.current = false
        setSession(null)
        setUser(null)
        setProfile(null)
        setLoading((prev) => (prev ? false : prev))
        return
      }

      // Update state strictly if token changed to eliminate tab-focus re-render storms
      if (tokenChanged) {
        lastAccessTokenRef.current = token
        setSession(currentSession)
        setUser(currentSession.user)
      }
      setLoading((prev) => (prev ? false : prev))

      if (event === 'SIGNED_IN' || event === 'INITIAL_SESSION') {
        if (currentSession.access_token && currentSession.user?.id) {
          handleProfileSync(currentSession.access_token, currentSession.user.id, false)
        }
      }
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [handleProfileSync])

  const login = useCallback(async (email: string, pass: string) => {
    syncedUserIdRef.current = null
    lastAccessTokenRef.current = null
    const { error } = await supabase.auth.signInWithPassword({ email, password: pass })
    return { error }
  }, [])

  const register = useCallback(async (email: string, pass: string) => {
    const redirectUrl = `${window.location.origin}/login`

    const { data, error } = await supabase.auth.signUp({
      email,
      password: pass,
      options: {
        emailRedirectTo: redirectUrl,
      },
    })
    return { data, error }
  }, [])

  const loginWithGoogle = useCallback(async () => {
    syncedUserIdRef.current = null
    lastAccessTokenRef.current = null
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin,
      },
    })
    return { error }
  }, [])

  const resetPassword = useCallback(async (email: string) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/forgot-password`,
    })
    return { error }
  }, [])

  const logout = useCallback(async () => {
    const { error } = await supabase.auth.signOut()
    setProfile(null)
    syncedUserIdRef.current = null
    syncInProgressRef.current = false
    lastAccessTokenRef.current = null
    try {
      Object.keys(localStorage).forEach((key) => {
        if (key.startsWith('veridict_eval_state_')) {
          localStorage.removeItem(key)
        }
      })
    } catch (err) {
      console.warn('[AuthContext] Error clearing storage on logout:', err)
    }
    return { error }
  }, [])

  const value = useMemo(
    () => ({
      user,
      session,
      profile,
      loading,
      loadingProfile,
      isAuthenticated,
      requireAuth,
      refreshProfile,
      login,
      register,
      loginWithGoogle,
      resetPassword,
      logout,
    }),
    [user, session, profile, loading, loadingProfile, isAuthenticated, requireAuth, refreshProfile, login, register, loginWithGoogle, resetPassword, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
