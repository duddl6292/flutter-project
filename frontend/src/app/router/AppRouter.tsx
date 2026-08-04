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
  PatientDetailPage,
} from '../../features/patients/PatientDetailPage'

import {
  AppointmentPage,
} from '../../features/appointments/AppointmentPage'

import {
  NotificationSettingsPage,
} from '../../features/notifications/NotificationSettingsPage'

import {
  AccountSettingsPage,
} from '../../features/account/AccountSettingsPage'

import {
  MyPage,
} from '../../features/account/MyPage'

import {
  PrescriptionPage,
} from '../../features/prescriptions/PrescriptionPage'

import {
  ReportPage,
} from '../../features/reports/ReportPage'

import {
  EncounterPage,
} from '../../features/encounters/EncounterPage'

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
          path="/patients/:patientId"
          element={<PatientDetailPage />}
        />
        <Route
          path="/appointments"
          element={
            <AppointmentPage />
          }
        />
        <Route
          path="/reports"
          element={<ReportPage />}
        />
        <Route
          path="/encounters"
          element={<EncounterPage />}
        />
        <Route
          path="/prescriptions"
          element={<PrescriptionPage />}
        />
        <Route
          path="/my-page"
          element={<MyPage />}
        />
        <Route
          path="/settings/account"
          element={
            <AccountSettingsPage />
          }
        />
        <Route
          path="/settings/notifications"
          element={
            <NotificationSettingsPage />
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
