import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle, CheckCircle2, Mail } from 'lucide-react'
import { useAuth } from '@/context/useAuth'
import { AuthLayout } from '@/components/Auth/AuthLayout'
import { AuthCard } from '@/components/Auth/AuthCard'
import { LoadingButton } from '@/components/Auth/LoadingButton'
import { mapAuthError } from '@/utils/authErrorMapper'

export const ForgotPassword: React.FC = () => {
  const { resetPassword } = useAuth()

  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleResetPassword = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    if (!email) {
      setError('Please enter your registered email address.')
      return
    }

    setLoading(true)
    try {
      const { error: resetError } = await resetPassword(email)
      if (resetError) {
        setError(mapAuthError(resetError, 'reset'))
      } else {
        setSuccess('Password reset link sent! Check your email inbox.')
        setEmail('')
      }
    } catch (err: any) {
      setError(mapAuthError(err, 'reset'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout>
      <AuthCard
        title="Reset Password"
        subtitle="Enter your email to receive a password reset link"
        footer={
          <p>
            Remember your password?{' '}
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

        <form onSubmit={handleResetPassword} className="space-y-4">
          <div>
            <label htmlFor="forgot-password-email" className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="forgot-password-email"
                type="email"
                required
                autoComplete="email"
                placeholder="developer@veridict.ai"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-amber-500/60 transition-colors"
              />
            </div>
          </div>

          <LoadingButton type="submit" loading={loading}>
            Send Reset Link
          </LoadingButton>
        </form>
      </AuthCard>
    </AuthLayout>
  )
}
