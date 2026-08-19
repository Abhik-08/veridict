import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import {
  AlertCircle,
  CheckCircle2,
  Lock,
  Mail,
  Eye,
  EyeOff,
  ShieldCheck,
  Activity,
  Database,
  Scale,
  ArrowRight,
} from 'lucide-react'
import { useAuth } from '@/context/useAuth'
import { AuthLightLayout } from '@/components/Auth/AuthLightLayout'
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

  // Form State
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(true)
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
      setError('Please enter your email and password.')
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

  const features = [
    { title: 'Factual Accuracy', desc: 'Cross-agent claim verification', icon: ShieldCheck },
    { title: 'Hallucination Sentinel', desc: 'Sub-second reference auditing', icon: Activity },
    { title: 'RAG Grounding Engine', desc: 'Semantic attribution mapping', icon: Database },
    { title: 'Explainable Verdicts', desc: 'Deterministic reasoning traces', icon: Scale },
  ]

  return (
    <AuthLightLayout>
      <div className="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center my-auto py-2">
        {/* ========================================================================= */}
        {/* LEFT COLUMN: Clean, High-Impact Product Preview (Calm & Professional) */}
        {/* ========================================================================= */}
        <div className="lg:col-span-7 flex flex-col space-y-5 text-left justify-center order-2 lg:order-1">
          {/* Header Typography */}
          <div className="space-y-2.5">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100/90 border border-amber-300 text-amber-900 text-xs font-semibold shadow-2xs">
              <span className="text-[11px] font-bold uppercase tracking-wider text-amber-900">
                AI Response Quality Engine
              </span>
            </div>

            <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-slate-900 leading-[1.12]">
              Veridict <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-600 via-orange-600 to-amber-700">Platform</span>
            </h1>

            <p className="text-sm sm:text-base font-bold text-slate-800 leading-snug max-w-xl">
              Development of AI Response Validation System with Hallucination Detection Assistance.
            </p>

            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-xl">
              Automated multi-agent consensus pipeline delivering deterministic verdicts across factual accuracy, RAG grounding, and hallucination containment.
            </p>
          </div>

          {/* Clean, Calm, Professional Metric Card (No auto-cycling numbers) */}
          <div className="w-full rounded-2xl bg-white/92 backdrop-blur-xl border border-amber-300/80 shadow-[0_20px_50px_-10px_rgba(234,88,12,0.15)] p-4 sm:p-5 space-y-3.5">
            {/* Stream Header */}
            <div className="flex items-center justify-between border-b border-amber-100 pb-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-orange-500" />
                <span className="text-xs font-bold text-slate-900">Multi-Agent Quality Telemetry</span>
              </div>
              <span className="text-[11px] font-bold text-orange-800 bg-orange-50 px-2 py-0.5 rounded border border-orange-200">
                Enterprise SLA
              </span>
            </div>

            {/* Static Clean Metrics Grid */}
            <div className="grid grid-cols-3 gap-2.5 sm:gap-3">
              {/* Grounding Score */}
              <div className="p-3 rounded-xl bg-gradient-to-b from-amber-50/90 to-orange-50/60 border border-amber-200/90 shadow-2xs">
                <div className="text-[10px] uppercase font-bold text-amber-900 tracking-wider">Grounding</div>
                <div className="text-lg sm:text-xl font-extrabold text-slate-900 mt-0.5">
                  99.4%
                </div>
                <div className="w-full h-1.5 bg-amber-200/70 rounded-full mt-2 overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full w-[99%]" />
                </div>
              </div>

              {/* Hallucination Detection */}
              <div className="p-3 rounded-xl bg-gradient-to-b from-amber-50/90 to-orange-50/60 border border-amber-200/90 shadow-2xs">
                <div className="text-[10px] uppercase font-bold text-amber-900 tracking-wider">Hallucination</div>
                <div className="text-lg sm:text-xl font-extrabold text-slate-900 mt-0.5">
                  0.02%
                </div>
                <div className="w-full h-1.5 bg-amber-200/70 rounded-full mt-2 overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full w-[4%]" />
                </div>
              </div>

              {/* Consensus Score */}
              <div className="p-3 rounded-xl bg-gradient-to-b from-amber-50/90 to-orange-50/60 border border-amber-200/90 shadow-2xs">
                <div className="text-[10px] uppercase font-bold text-amber-900 tracking-wider">Consensus</div>
                <div className="text-lg sm:text-xl font-extrabold text-slate-900 mt-0.5">
                  9.8<span className="text-xs font-normal text-slate-400">/10</span>
                </div>
                <div className="w-full h-1.5 bg-amber-200/70 rounded-full mt-2 overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full w-[98%]" />
                </div>
              </div>
            </div>

            {/* Static Sub-label */}
            <div className="flex items-center justify-between px-3 py-2 rounded-xl bg-amber-100/50 border border-amber-200/70 text-[11px] font-medium text-amber-950">
              <span>Deterministic multi-agent verification pipeline</span>
              <span className="font-bold text-emerald-800">Verified Truth</span>
            </div>
          </div>

          {/* Compact 2x2 Feature Pillars */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-0.5">
            {features.map((feat) => {
              const IconComp = feat.icon
              return (
                <div
                  key={feat.title}
                  className="flex items-center gap-3 p-2.5 sm:p-3 rounded-xl bg-white/85 backdrop-blur-sm border border-amber-200/80 hover:border-orange-300 hover:shadow-xs transition-all shadow-2xs"
                >
                  <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-orange-100 text-orange-800 border border-orange-200 shrink-0">
                    <IconComp className="w-3.5 h-3.5" />
                  </div>
                  <div className="min-w-0">
                    <h4 className="text-xs font-bold text-slate-900 leading-none">{feat.title}</h4>
                    <p className="text-[10.5px] text-slate-500 truncate mt-0.5">{feat.desc}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* ========================================================================= */}
        {/* RIGHT COLUMN: Ultra-Luxury Light Authentication Card */}
        {/* ========================================================================= */}
        <div className="lg:col-span-5 flex justify-center items-center w-full order-1 lg:order-2">
          <div className="w-full max-w-[420px] rounded-3xl bg-white/95 backdrop-blur-2xl border border-amber-300/80 shadow-[0_25px_60px_-12px_rgba(234,88,12,0.18),0_0_0_1px_rgba(255,255,255,0.9)_inset] p-6 sm:p-8 space-y-5">
            {/* Header inside Card */}
            <div className="space-y-1 text-center">
              <h2 className="text-2xl font-display font-extrabold text-slate-900 tracking-tight">
                Sign in to Veridict
              </h2>
              <p className="text-xs text-slate-500 font-normal">
                Enter your credentials to continue.
              </p>
            </div>

            {/* Error Message Alert */}
            {error && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2 animate-fade-in">
                <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                <span className="leading-snug">{error}</span>
              </div>
            )}

            {/* Success Message Alert */}
            {success && (
              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-start gap-2 animate-fade-in">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span className="leading-snug">{success}</span>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleLogin} className="space-y-3.5">
              {/* Email Field */}
              <div>
                <label
                  htmlFor="login-email"
                  className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1"
                >
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-amber-700/70 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    id="login-email"
                    type="email"
                    required
                    autoComplete="email"
                    placeholder="name@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-[#FFFDF9] hover:bg-amber-50/50 focus:bg-white border border-amber-200/90 rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:ring-3 focus:ring-amber-500/25 shadow-2xs transition-all"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label
                    htmlFor="login-password"
                    className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider"
                  >
                    Password
                  </label>
                  <Link
                    to="/forgot-password"
                    className="text-[11px] font-semibold text-amber-700 hover:text-orange-700 transition-colors"
                  >
                    Forgot password?
                  </Link>
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 text-amber-700/70 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    autoComplete="current-password"
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-[#FFFDF9] hover:bg-amber-50/50 focus:bg-white border border-amber-200/90 rounded-xl pl-10 pr-10 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:ring-3 focus:ring-amber-500/25 shadow-2xs transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 transition-colors focus:outline-none cursor-pointer"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Remember Me Checkbox */}
              <div className="flex items-center justify-between pt-0.5">
                <label className="flex items-center gap-2 text-xs text-slate-600 font-medium cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded text-amber-600 border-amber-300 focus:ring-amber-500 focus:ring-offset-0 transition-colors"
                  />
                  <span>Remember me</span>
                </label>
              </div>

              {/* Primary Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full min-h-[44px] py-2.5 px-4 rounded-xl font-bold text-xs flex items-center justify-center gap-2 text-white bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 hover:from-slate-900 hover:via-amber-950 hover:to-slate-900 active:scale-[0.99] transition-all duration-200 shadow-[0_8px_24px_rgba(217,119,6,0.25)] hover:shadow-[0_12px_28px_rgba(217,119,6,0.35)] disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer group border border-slate-700/60"
              >
                {loading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Signing in...</span>
                  </>
                ) : (
                  <>
                    <span>Sign in</span>
                    <ArrowRight className="w-3.5 h-3.5 transition-transform duration-200 group-hover:translate-x-1" />
                  </>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="relative flex py-0.5 items-center">
              <div className="flex-grow border-t border-amber-200/80" />
              <span className="flex-shrink mx-3 text-[10px] uppercase tracking-wider text-amber-900/60 font-semibold">
                Or
              </span>
              <div className="flex-grow border-t border-amber-200/80" />
            </div>

            {/* Google OAuth Button */}
            <button
              type="button"
              disabled={googleLoading}
              onClick={handleGoogleLogin}
              className="w-full min-h-[42px] py-2.5 px-4 rounded-xl font-semibold text-xs flex items-center justify-center gap-2.5 bg-white hover:bg-amber-50/60 text-slate-700 border border-amber-200/90 shadow-2xs hover:shadow-xs transition-all duration-150 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
            >
              {googleLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-slate-400/30 border-t-slate-600 rounded-full animate-spin" />
                  <span>Connecting to Google...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                    />
                  </svg>
                  <span>Continue with Google</span>
                </>
              )}
            </button>

            {/* Bottom Register Switcher */}
            <div className="pt-1.5 text-center text-xs text-slate-500 border-t border-amber-100">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="font-bold text-amber-700 hover:text-orange-700 transition-colors"
              >
                Sign up
              </Link>
            </div>
          </div>
        </div>
      </div>
    </AuthLightLayout>
  )
}
