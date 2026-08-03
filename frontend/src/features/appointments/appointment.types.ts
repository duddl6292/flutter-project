export type AppointmentStatus =
  | 'SCHEDULED'
  | 'CONFIRMED'
  | 'CHECKED_IN'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'NO_SHOW'

export interface Appointment {
  appointment_id: string

  patient_id: string
  patient_number: string | null
  patient_name: string

  clinician_id: string
  clinician_name: string

  department_code: string
  department_name: string

  hospital_id: string
  hospital_name: string

  scheduled_at: string
  duration_minutes: number

  location: string
  reason: string
  status: AppointmentStatus
}

export interface AppointmentListResponse {
  data: Appointment[]

  meta: {
    total_count: number
  }
}

export interface AppointmentCreateInput {
  patient_id: string
  scheduled_at: string
  duration_minutes: number
  location: string
  reason: string
}