import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle, CheckCircle2, Lock, Mail } from 'lucide-react'
import { useAuth } from '@/context/useAuth'
import { AuthLayout } from '@/components/Auth/AuthLayout'
import { AuthCard } from '@/components/Auth/AuthCard'
import { LoadingButton } from '@/components/Auth/LoadingButton'

export const Register: React.FC = () => {
  const { register, loginWithGoogle } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleRegister = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    if (!email || !password || !confirmPassword) {
      setError('Please fill in all required fields.')
      return
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)
    try {
      const { error: authError } = await register(email, password)
      if (authError) {
        setError(authError.message || 'Registration failed.')
      } else {
        setSuccess('Registration successful! Please check your email to confirm your account.')
        setEmail('')
        setPassword('')
        setConfirmPassword('')
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred during registration.')
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
        setError(oauthError.message || 'Google OAuth failed.')
      }
    } catch (err: any) {
      setError(err.message || 'Could not connect to Google auth.')
    } finally {
      setGoogleLoading(false)
    }
  }

  return (
    <AuthLayout>
      <AuthCard
        title="Create Account"
        subtitle="Sign up for your Veridict evaluation workspace"
        footer={
          <p>
            Already have an account?{' '}
            <Link to="/login" className="font-bold text-amber-400 hover:text-amber-300 transition-colors">
              Sign In
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

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label htmlFor="register-email" className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="register-email"
                type="email"
                required
                placeholder="developer@veridict.ai"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-amber-500/60 transition-colors"
              />
            </div>
          </div>

          <div>
            <label htmlFor="register-password" className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Password (Min 6 chars)
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="register-password"
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-amber-500/60 transition-colors"
              />
            </div>
          </div>

          <div>
            <label htmlFor="register-confirm-password" className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Confirm Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="register-confirm-password"
                type="password"
                required
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-amber-500/60 transition-colors"
              />
            </div>
          </div>

          <LoadingButton type="submit" loading={loading}>
            Create Account
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
          <svg className="w-4 h-4" viewBox="0 0 24 24">
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
          Continue with Google
        </LoadingButton>
      </AuthCard>
    </AuthLayout>
  )
}
