import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { AlertCircle, CheckCircle2, Lock, Mail, Eye, EyeOff, Check } from 'lucide-react'
import logoSrc from '@/assets/logo.png'
import heroIllustrationSrc from '@/assets/hero-illustration.jpg'
import { useAuth } from '@/context/useAuth'
import { AuthLayout } from '@/components/Auth/AuthLayout'
import { AuthCard } from '@/components/Auth/AuthCard'
import { LoadingButton } from '@/components/Auth/LoadingButton'
import { mapAuthError } from '@/utils/authErrorMapper'

export const Login: React.FC = () => {
  const { login, loginWithGoogle } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const searchParams = new URLSearchParams(location.search)
  const redirectParam = searchParams.get('redirect')
  const fromState = (location.state as any)?.from?.pathname

  // OWASP Open Redirect Defense: Sanitize redirect destination to internal relative paths only
  const sanitizeRedirectUrl = (url: string | null | undefined): string => {
    if (!url) return '/'
    if (url.startsWith('/') && !url.startsWith('//') && !url.includes('\\') && !url.includes(':')) {
      return url
    }
    return '/'
  }
  const returnUrl = sanitizeRedirectUrl(redirectParam || fromState)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Detect URL error parameters from Supabase email verification or password reset links
  useEffect(() => {
    const hash = window.location.hash
    const query = window.location.search
    if (hash.includes('error=') || query.includes('error=')) {
      const params = new URLSearchParams(hash.replace('#', '?') || query)
      const errCode = params.get('error_code') || params.get('error')
      const errDesc = params.get('error_description')
      if (errCode || errDesc) {
        setError(mapAuthError({ message: errDesc || undefined, code: errCode || undefined }, 'login'))
      }
    }
  }, [location])

  const handleLogin = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    if (!email || !password) {
      setError('Please fill in all required fields.')
      return
    }

    setLoading(true)
    try {
      const { error: authError } = await login(email, password)
      if (authError) {
        setError(mapAuthError(authError, 'login'))
      } else {
        setSuccess('Login successful! Redirecting...')
        setTimeout(() => navigate(returnUrl, { replace: true }), 600)
      }
    } catch (err: any) {
      setError(mapAuthError(err, 'login'))
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setError(null)
    setGoogleLoading(true)
    try {
      const { error: oauthError } = await loginWithGoogle()
      if (oauthError) {
        setError(mapAuthError(oauthError, 'login'))
      }
    } catch (err: any) {
      setError(mapAuthError(err, 'login'))
    } finally {
      setGoogleLoading(false)
    }
  }

  const featureList = [
    'Accuracy Analysis',
    'Relevance Assessment',
    'Completeness Evaluation',
    'Hallucination Detection',
    'RAG Grounding',
    'Explainable Verdicts',
  ]

  return (
    <AuthLayout>
      <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center my-auto py-2">
        {/* Left Column: Hero Branding & Hero Illustration */}
        <div className="lg:col-span-7 flex flex-col items-center lg:items-start text-center lg:text-left space-y-5 justify-center">
          {/* Logo & Title */}
          <div className="flex flex-col items-center lg:items-start gap-1">
            <Link to="/" className="inline-flex items-center gap-3 group">
              <img
                src={logoSrc}
                alt="Veridict Logo"
                className="h-9 w-9 object-contain rounded-md transition-transform duration-300 group-hover:scale-105"
              />
              <span className="font-display text-3xl font-extrabold tracking-tight text-white">
                Veridict
              </span>
            </Link>
            <p className="text-xs font-semibold uppercase tracking-widest text-amber-400 mt-1">
              AI Response Quality Evaluation Platform
            </p>
          </div>

          {/* Description (max 2 lines) */}
          <p className="text-sm text-slate-300 max-w-xl leading-relaxed">
            Evaluate AI-generated responses using a multi-agent evaluation pipeline that measures factual accuracy, relevance, completeness, hallucination detection, and RAG grounding.
          </p>

          {/* Hero Illustration / Artwork (15–20% smaller, seamless soft glow, no harsh border) */}
          <div className="relative w-full max-w-[340px] sm:max-w-[380px] lg:max-w-[420px] my-1 flex justify-center items-center">
            {/* Soft ambient orange/blue glow background */}
            <div className="absolute inset-0 bg-amber-500/10 blur-3xl rounded-full scale-90 pointer-events-none" />
            <img
              src={heroIllustrationSrc}
              alt="Veridict Multi-Agent Evaluation Engine Illustration"
              className="relative z-10 w-full h-auto object-contain rounded-2xl shadow-[0_12px_40px_rgba(0,0,0,0.6)] transition-all duration-700 hover:scale-[1.01] animate-float"
              loading="lazy"
            />
          </div>

          {/* Clean 2-Column Feature Checklist */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2.5 w-full max-w-lg pt-1">
            {featureList.map((feat) => (
              <div
                key={feat}
                className="flex items-center gap-2.5 text-xs text-slate-300 font-medium"
              >
                <div className="flex items-center justify-center w-4 h-4 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-400 shrink-0">
                  <Check className="w-2.5 h-2.5" />
                </div>
                <span>{feat}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Authentication Card */}
        <div className="lg:col-span-5 flex justify-center items-center w-full">
          <AuthCard
            title="Welcome to Veridict"
            subtitle="Sign in to continue evaluating AI-generated responses."
            footer={
              <p>
                Don't have an account?{' '}
                <Link to="/register" className="font-bold text-amber-400 hover:text-amber-300 transition-colors">
                  Sign Up
                </Link>
              </p>
            }
          >
            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {success && (
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>{success}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label htmlFor="login-email" className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    id="login-email"
                    type="email"
                    required
                    autoComplete="email"
                    placeholder="developer@veridict.ai"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-slate-900/90 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500/40 transition-all"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label htmlFor="login-password" className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Password
                  </label>
                  <Link to="/forgot-password" className="text-[11px] font-medium text-amber-400 hover:text-amber-300 transition-colors">
                    Forgot password?
                  </Link>
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    autoComplete="current-password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-slate-900/90 border border-slate-800 rounded-lg pl-9 pr-10 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500/40 transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors focus:outline-none"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <LoadingButton type="submit" loading={loading}>
                {loading ? 'Signing In...' : 'Sign In'}
              </LoadingButton>
            </form>

            <div className="relative flex py-1 items-center">
              <div className="flex-grow border-t border-slate-800" />
              <span className="flex-shrink mx-3 text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Or continue with
              </span>
              <div className="flex-grow border-t border-slate-800" />
            </div>

            <LoadingButton
              type="button"
              variant="secondary"
              loading={googleLoading}
              onClick={handleGoogleLogin}
            >
              <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              <span>Continue with Google</span>
            </LoadingButton>
          </AuthCard>
        </div>
      </div>
    </AuthLayout>
  )
}
