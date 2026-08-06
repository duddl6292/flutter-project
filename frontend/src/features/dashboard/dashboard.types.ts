export type CtStatus = 'waiting' | 'processing' | 'completed' | 'failed'

export type Gender = 'M' | 'F' | string

export interface DashboardPatient {
  patient_id: string
  patient_number: string | null
  name: string
  age: number | null
  gender: Gender
  department: string
  appointment_at: string
  status: string
  phone?: string
}

export interface DashboardActivity {
  activity_id: string | number
  occurred_at: string
  message: string
  type: string
}

export interface DashboardSchedule {
  schedule_id: string | number
  start_at: string
  patient_id: string
  patient_name: string
  room: string
  status: string
}

export interface DashboardConsultation {
  consultation_id: string | number
  status: string
  department: string
  title: string
  patient_id: string
  patient_display: string
  requested_at: string
  responded_at?: string | null
}

export interface DashboardResponse {
  date: string
  doctor: {
    name: string
    department: string
    title: string
  }
  summary: {
    appointments: {
      total: number
      confirmed: number
      waiting: number
    }
    consultations: {
      total: number
      waiting: number
      answered: number
    }
    tests: {
      total: number
      processing: number
      result_waiting: number
    }
    ct_analyses: {
      total: number
      processing: number
      completed: number
    }
  }
  patients: DashboardPatient[]
  activities: DashboardActivity[]
  schedules: DashboardSchedule[]
  consultations: DashboardConsultation[]
}

export interface CtPredictResponse {
  ct_id: string | number
  display_id: string
  job_id: string
  status: CtStatus
  progress: number
  message: string
}

export interface CtStatusResponse {
  ct_id: string | number
  display_id: string
  status: CtStatus
  progress: number
  elapsed_time: number
  error_code: string
  error_message: string
}

export interface CtHistoryItem {
  ct_id: string | number
  display_id: string
  patient_id: string
  patient_name: string
  gender: Gender
  age: number
  status: CtStatus
  progress: number
  created_at: string
}

export interface CtHistoryResponse {
  results: CtHistoryItem[]
  count: number
}
