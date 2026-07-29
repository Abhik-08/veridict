import { api } from './api'

export interface UserProfile {
  id: string
  email: string
  full_name?: string | null
  avatar_url?: string | null
  provider: string
}

export const syncProfile = async (token?: string): Promise<UserProfile> => {
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  const response = await api.post<UserProfile>('/auth/sync-profile', {}, { headers })
  return response.data
}

export const getMe = async (token?: string): Promise<UserProfile> => {
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  const response = await api.get<UserProfile>('/me', { headers })
  return response.data
}
