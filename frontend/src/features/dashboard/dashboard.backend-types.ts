import type {
  DashboardActivity,
  DashboardConsultation,
  DashboardPatient,
  DashboardResponse,
  DashboardSchedule,
} from './dashboard.types'

export interface BackendHospital {
  hospital_id: string
  hospital_code: string | null
  hospital_name: string
  address: string
  phone: string
}

export interface BackendDepartment {
  department_id: string
  code: string
  name: string
  is_active: boolean
}

export interface BackendClinician {
  clinician_id: string
  user_id: string
  name: string
  license_number: string
  approval_status: string
  created_at: string
  updated_at: string

  hospital: BackendHospital
  department: BackendDepartment
}

export interface BackendDashboardResponse {
  data: {
    clinician: BackendClinician

    summary?:
      DashboardResponse['summary']

    patients?:
      DashboardPatient[]

    activities?:
      DashboardActivity[]

    schedules?:
      DashboardSchedule[]

    consultations?:
      DashboardConsultation[]
  }
}