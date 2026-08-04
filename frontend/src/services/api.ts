import axios from 'axios'
import { supabase } from '@/lib/supabase'
import { authManager } from '@/lib/authManager'

export const api = axios.create({
  baseURL: (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, ''),
  timeout: 30000,
})

// Request Interceptor: Inject JWT token into Authorization header if not already present
api.interceptors.request.use(
  async (config) => {
    try {
      // Check whether Authorization header already exists safely across Axios versions
      const headers = config.headers
      const existingAuth =
        headers?.Authorization ||
        headers?.authorization ||
        (typeof headers?.get === 'function' ? headers.get('Authorization') || headers.get('authorization') : null)

      if (!existingAuth) {
        const { data } = await supabase.auth.getSession()
        const token = data.session?.access_token
        if (token) {
          if (typeof headers?.set === 'function') {
            headers.set('Authorization', `Bearer ${token}`)
          } else if (headers) {
            headers.Authorization = `Bearer ${token}`
          }
        }
      }
    } catch (err) {
      console.warn('[API Interceptor] Could not fetch session token:', err)
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response Interceptor: Handle 401/403 session expiration via Centralized Auth Manager
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.warn('[API Interceptor] Session expired or unauthorized (401/403). Triggering centralized logout...')
      await authManager.handleUnauthorized()
    }
    throw error
  }
)