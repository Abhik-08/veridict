/**
 * Centralized Supabase Auth Error Mapper for Veridict
 * OWASP-hardened authentication error mapper utility.
 * Prevents account enumeration vulnerabilities while providing actionable guidance.
 */

export interface AuthErrorLike {
  message?: string
  status?: number
  code?: string
  name?: string
  error_code?: string
}

interface ErrorRule {
  keywords: string[]
  getMessage: (context: 'login' | 'register' | 'reset') => string
}

const ERROR_RULES: ErrorRule[] = [
  {
    keywords: ['rate', 'rate limit', 'too many requests'],
    getMessage: () => 'Too many attempts. Please wait a few minutes before trying again.',
  },
  {
    keywords: ['failed to fetch', 'network error', 'unable to connect', 'network'],
    getMessage: () => 'Unable to connect. Please check your internet connection.',
  },
  {
    keywords: ['user_already_exists', 'email_exists', 'user already registered', 'email already exists', 'already in use'],
    getMessage: (context) =>
      context === 'register'
        ? 'An account with this email address may already exist. Please try signing in or use Forgot Password.'
        : 'An account with this email address may already exist. Please try signing in or reset your password.',
  },
  {
    keywords: ['identity_already_exists', 'provider_disabled', 'provider', 'google account'],
    getMessage: () => 'If you previously registered using Google, please continue with Google Sign-In or use Forgot Password.',
  },
  {
    keywords: ['invalid_credentials', 'user_not_found', 'invalid login credentials', 'user not found'],
    getMessage: (context) =>
      context === 'login'
        ? 'Incorrect email or password. If you previously registered using Google, please continue with Google Sign-In.'
        : 'Incorrect credentials. Please verify your details and try again.',
  },
  {
    keywords: ['email_not_confirmed', 'email not confirmed', 'verify your email'],
    getMessage: () => 'Please verify your email address before signing in. Check your inbox for the confirmation link.',
  },
  {
    keywords: ['password should be at least', 'weak_password'],
    getMessage: () => 'Password must be at least 6 characters long.',
  },
  {
    keywords: ['same_password', 'same as current'],
    getMessage: () => 'New password must be different from your current password.',
  },
  {
    keywords: ['otp_expired', 'access_denied', 'link is invalid', 'link has expired', 'token has expired'],
    getMessage: () => 'Your email verification or reset link has expired or is invalid. Please request a new link.',
  },
]

export function mapAuthError(
  error: AuthErrorLike | Error | string | null | undefined,
  context: 'login' | 'register' | 'reset' = 'login'
): string {
  if (!error) return 'An unexpected error occurred. Please try again.'

  const errObj: AuthErrorLike = typeof error === 'string' ? { message: error } : (error as AuthErrorLike)
  const message = (errObj.message || '').toLowerCase()
  const code = (errObj.code || errObj.error_code || '').toLowerCase()
  const status = errObj.status

  if (status === 429) {
    return 'Too many attempts. Please wait a few minutes before trying again.'
  }

  const matchedRule = ERROR_RULES.find((rule) =>
    rule.keywords.some((kw) => code.includes(kw) || message.includes(kw))
  )

  if (matchedRule) {
    return matchedRule.getMessage(context)
  }

  if (errObj.message && !errObj.message.toLowerCase().includes('auth error') && !errObj.message.includes('Exception')) {
    return errObj.message
  }

  return 'Something went wrong. Please try again.'
}
