export type EncounterStatus =
  | 'REGISTERED'
  | 'ARRIVED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED'

export type EncounterType =
  | 'OUTPATIENT'
  | 'EMERGENCY'
  | 'INPATIENT'
  | 'TELEMEDICINE'

export interface ClinicalRecord {
  clinical_record_id: string
  recorded_at: string
  chief_complaint: string
  subjective: string
  objective: string
  assessment: string
  plan: string
  patient_visible_summary: string
  created_at: string
  updated_at: string
}

export type ClinicalRecordInput = Omit<
  ClinicalRecord,
  | 'clinical_record_id'
  | 'recorded_at'
  | 'created_at'
  | 'updated_at'
>

export interface EncounterSummary {
  encounter_id: string
  encounter_number: string
  encounter_type: EncounterType
  encounter_type_label: string
  status: EncounterStatus
  status_label: string
  patient_id: string | null
  patient_number: string | null
  patient_name: string
  patient_birth_date: string | null
  patient_sex: string | null
  appointment_id: string | null
  scheduled_at: string | null
  appointment_reason: string | null
  department_name: string
  clinician_id: string
  clinician_name: string
  hospital_name: string | null
  arrived_at: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

export interface EncounterDetail
  extends EncounterSummary {
  clinical_record: ClinicalRecord | null
  prescriptions: Array<{
    prescription_id: string
    status: string
    status_label: string
    prescribed_at: string
    medicine_names: string[]
  }>
  ct_cases: Array<{
    case_id: string
    study_type: string
    study_type_label: string
    status: string
    status_label: string
    performed_at: string | null
    created_at: string
  }>
}

export interface EncounterListResponse {
  data: EncounterSummary[]
  meta: {
    page: number
    page_size: number
    total_count: number
    total_pages: number
  }
}
