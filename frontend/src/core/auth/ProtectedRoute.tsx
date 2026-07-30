import { Navigate, Outlet } from 'react-router-dom'

import { useAuthStore } from './authStore'

export function ProtectedRoute() {
  const accessToken = useAuthStore((state) => state.accessToken)

  return accessToken ? <Outlet /> : <Navigate to="/login" replace />
}
