import {
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import { ProtectedRoute } from '../../core/auth/ProtectedRoute'
import { LoginPage } from '../../features/auth/LoginPage'
import { DashboardPlaceholder } from '../../features/dashboard/DashboardPlaceholder'

import {
  PatientListPage,
} from '../../features/patients/PatientListPage'

import {
  AppointmentPage,
} from '../../features/appointments/AppointmentPage'

function NotFoundPage() {
  return (
    <main>
      <h1>
        페이지를 찾을 수 없습니다.
      </h1>
    </main>
  )
}

export function AppRouter() {
  return (
    <Routes>
      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route element={<ProtectedRoute />}>
        <Route
          path="/"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

        <Route
          path="/dashboard"
          element={
            <DashboardPlaceholder />
          }
        />
        <Route
          path="/patients"
          element={
            <PatientListPage />
          }
        />
        <Route
          path="/appointments"
          element={
            <AppointmentPage />
          }
        />
      </Route>

      <Route
        path="*"
        element={<NotFoundPage />}
      />
    </Routes>
  )
}