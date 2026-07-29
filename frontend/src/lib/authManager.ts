import { supabase } from '@/lib/supabase'

class AuthManager {
  private isRedirecting = false

  /**
   * Centralized unauthorized handler triggered on 401 / 403 API responses.
   * Signs out, clears session, and redirects to login preserving intended destination.
   */
  async handleUnauthorized(currentPath?: string): Promise<void> {
    if (this.isRedirecting) return
    this.isRedirecting = true

    try {
      await supabase.auth.signOut()
    } catch (err) {
      console.warn('[AuthManager] Error during sign out:', err)
    }

    if (typeof window !== 'undefined') {
      const publicPaths = ['/login', '/register', '/forgot-password']
      const path = currentPath || window.location.pathname
      const isPublic = publicPaths.some((p) => path.startsWith(p))

      if (!isPublic) {
        const target = `/login?redirect=${encodeURIComponent(path + window.location.search)}`
        window.location.href = target
      }
    }

    setTimeout(() => {
      this.isRedirecting = false
    }, 3000)
  }
}

export const authManager = new AuthManager()
