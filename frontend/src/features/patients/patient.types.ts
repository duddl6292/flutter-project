export type PatientSex =
  | 'M'
  | 'F'
  | 'UNKNOWN'

export type PatientStatus =
  | 'ACTIVE'
  | 'INACTIVE'
  | 'MERGED'

export interface PatientSummary {
  patient_id: string

  medical_record_number:
    string | null

  name: string

  birth_date:
    string | null

  sex: PatientSex

  phone: string

  status: PatientStatus
}

export interface PatientListMeta {
  page: number
  page_size: number
  total_count: number
  total_pages: number
}

export interface PatientListResponse {
  data: PatientSummary[]
  meta: PatientListMeta
}

export interface PatientDetail
  extends PatientSummary {
  user_id: string | null
  username: string | null
  email: string | null
  emergency_contact: string
  address: string
  merged_into_id: string | null
  created_at: string
  updated_at: string
}
