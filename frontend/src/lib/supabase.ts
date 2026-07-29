import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabasePublishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || ''

if (!supabaseUrl || !supabasePublishableKey) {
  console.warn('Supabase environment variables (VITE_SUPABASE_URL, VITE_SUPABASE_PUBLISHABLE_KEY) are missing.')
}

const generateId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID().slice(0, 8)
  }
  return 'sb_client_1'
}

export const SUPABASE_CLIENT_ID = `sb_client_${generateId()}`
console.log(`[AuthAudit] Initializing Singleton Supabase Client Instance: ${SUPABASE_CLIENT_ID}`)

export const supabase = createClient(supabaseUrl, supabasePublishableKey)
