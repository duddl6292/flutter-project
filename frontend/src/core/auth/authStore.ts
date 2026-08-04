import { create } from 'zustand'

export type UserRole =
  | 'PATIENT'
  | 'CLINICIAN'
  | 'ADMIN'

export interface AuthUser {
  id: string
  username: string
  email: string
  role: UserRole
}

export interface ClinicianProfile {
  id: string
  name: string
  license_number: string
  approval_status: string
  hospital_id: string
  hospital_name: string
  department_id: string
  department_code: string
  department_name: string
}

interface StoredSession {
  accessToken: string
  refreshToken: string
  user: AuthUser
  clinician: ClinicianProfile
}

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: AuthUser | null
  clinician: ClinicianProfile | null

  setSession: (
    session: StoredSession,
  ) => void

  updateTokens: (
    accessToken: string,
    refreshToken?: string,
  ) => void

  updateUser: (
    user: AuthUser,
  ) => void

  clearSession: () => void
}

const STORAGE_KEY = 'brainon-web-session'

function readStoredSession():
StoredSession | null {
  try {
    const value =
      sessionStorage.getItem(STORAGE_KEY)

    if (!value) {
      return null
    }

    return JSON.parse(value) as StoredSession
  } catch {
    sessionStorage.removeItem(STORAGE_KEY)
    return null
  }
}

const initialSession = readStoredSession()

export const useAuthStore =
  create<AuthState>((set, get) => ({
    accessToken:
      initialSession?.accessToken ?? null,

    refreshToken:
      initialSession?.refreshToken ?? null,

    user:
      initialSession?.user ?? null,

    clinician:
      initialSession?.clinician ?? null,

    setSession: (session) => {
      sessionStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(session),
      )

      set(session)
    },

    updateTokens: (
      accessToken,
      refreshToken,
    ) => {
      const current = get()

      const nextRefreshToken =
        refreshToken
        ?? current.refreshToken

      set({
        accessToken,
        refreshToken: nextRefreshToken,
      })

      if (
        current.user
        && current.clinician
        && nextRefreshToken
      ) {
        sessionStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            accessToken,
            refreshToken:
              nextRefreshToken,
            user: current.user,
            clinician:
              current.clinician,
          }),
        )
      }
    },

    updateUser: (user) => {
      const current = get()

      set({ user })

      if (
        current.accessToken
        && current.refreshToken
        && current.clinician
      ) {
        sessionStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            accessToken:
              current.accessToken,
            refreshToken:
              current.refreshToken,
            user,
            clinician:
              current.clinician,
          }),
        )
      }
    },

    clearSession: () => {
      sessionStorage.removeItem(
        STORAGE_KEY,
      )

      set({
        accessToken: null,
        refreshToken: null,
        user: null,
        clinician: null,
      })
    },
  }))
