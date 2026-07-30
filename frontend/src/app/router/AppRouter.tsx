import { Route, Routes } from 'react-router-dom'

import App from '../../App'
import { ProtectedRoute } from '../../core/auth/ProtectedRoute'
import { LoginPlaceholder } from '../../features/auth/LoginPlaceholder'
import { DashboardPlaceholder } from '../../features/dashboard/DashboardPlaceholder'

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/login" element={<LoginPlaceholder />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<DashboardPlaceholder />} />
      </Route>
    </Routes>
  )
}
