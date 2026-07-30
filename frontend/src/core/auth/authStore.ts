import { create } from 'zustand'

export type UserRole = 'PATIENT' | 'CLINICIAN' | 'ADMIN'

export interface AuthUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
}

interface AuthState {
  accessToken: string | null
  user: AuthUser | null
  setSession: (accessToken: string, user: AuthUser) => void
  setAccessToken: (accessToken: string) => void
  clearSession: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setSession: (accessToken, user) => set({ accessToken, user }),
  setAccessToken: (accessToken) => set({ accessToken }),
  clearSession: () => set({ accessToken: null, user: null }),
}))
