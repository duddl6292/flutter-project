export interface ReportStatusCount {
  status: string
  label: string
  count: number
}

export interface DailyEncounterCount {
  date: string
  count: number
}

export interface TopMedicineCount {
  medicine_name: string
  count: number
}

export interface ClinicianSummaryReport {
  clinician: {
    clinician_id: string
    name: string
  }
  period: {
    start_date: string
    end_date: string
  }
  summary: {
    patient_count: number
    appointment_completion_rate: number
    prescription_count: number
    ct_analysis_count: number
  }
  daily_encounters: DailyEncounterCount[]
  appointment_statuses: ReportStatusCount[]
  prescription_statuses: ReportStatusCount[]
  top_medicines: TopMedicineCount[]
}

export type ReportDetailType =
  | 'encounters'
  | 'appointments'
  | 'prescriptions'
  | 'ct_analyses'

export interface ReportMedicineItem {
  medicine_name: string
  dosage: string
  dose_unit: string
  frequency: string
  route: string
}

export interface ReportDetailItem {
  record_id: string
  type: ReportDetailType
  patient_id: string | null
  patient_number: string | null
  patient_name: string
  occurred_at: string
  reference: string
  status: string
  status_label: string
  details: {
    encounter_type?: string
    started_at?: string | null
    completed_at?: string | null
    duration_minutes?: number
    location?: string
    reason?: string
    cancellation_reason?: string
    notes?: string
    items?: ReportMedicineItem[]
    study_type?: string
    case_status?: string
    case_status_label?: string
    description?: string
    performed_at?: string | null
  }
}

export interface ReportDetailResponse {
  data: ReportDetailItem[]
  meta: {
    page: number
    page_size: number
    total_count: number
    total_pages: number
  }
}
