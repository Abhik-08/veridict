import axios from 'axios'
import { supabase } from '@/lib/supabase'
import { authManager } from '@/lib/authManager'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
})

// Request Interceptor: Inject JWT token into Authorization header if not already present
api.interceptors.request.use(
  async (config) => {
    try {
      // Check whether Authorization header already exists
      const existingAuth = config.headers.Authorization || config.headers.authorization
      if (!existingAuth) {
        const { data } = await supabase.auth.getSession()
        const token = data.session?.access_token
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
      }
    } catch (err) {
      console.warn('[API Interceptor] Could not fetch session token:', err)
    }
    return config
  },
  (error) => {
    throw error
  }
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