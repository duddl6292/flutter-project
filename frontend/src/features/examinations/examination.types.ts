export type ExaminationStatus =
  | 'REGISTERED'
  | 'IN_PROGRESS'
  | 'PRELIMINARY'
  | 'FINAL'
  | 'CORRECTED'
  | 'CANCELLED'

export type ExaminationCategory =
  | 'LABORATORY'
  | 'IMAGING'
  | 'PHYSIOLOGY'
  | 'PATHOLOGY'
  | 'NEURO_ASSESSMENT'
  | 'OTHER'

export type ExaminationSource =
  | 'INTERNAL'
  | 'EXTERNAL'
  | 'PATIENT_UPLOAD'

export type ExaminationInterpretation =
  | 'NORMAL'
  | 'LOW'
  | 'HIGH'
  | 'ABNORMAL'
  | 'CRITICAL'
  | 'UNKNOWN'

export type ExaminationValueType =
  | 'NUMERIC'
  | 'TEXT'
  | 'CODED'
  | 'BOOLEAN'

export interface ExaminationObservation {
  observation_id: string
  code: string
  name: string
  sequence: number
  value_type: ExaminationValueType
  numeric_value: string | null
  text_value: string
  coded_value: string
  boolean_value: boolean | null
  formatted_value: string
  unit: string
  reference_low: string | null
  reference_high: string | null
  reference_text: string
  interpretation: ExaminationInterpretation
  interpretation_label: string
}

export interface DiagnosticReport {
  report_id: string
  revision_number: number
  author_name: string
  status: 'DRAFT' | 'FINAL' | 'CORRECTED' | 'CANCELLED'
  status_label: string
  title: string
  summary: string
  conclusion: string
  issued_at: string | null
  signed_at: string | null
  is_released_to_patient: boolean
  released_at: string | null
  assets: Array<{
    asset_id: string
    stored_object_id: string
    asset_type: string
    asset_type_label: string
    display_name: string
    created_at: string
  }>
  created_at: string
  updated_at: string
}

export interface Examination {
  examination_id: string
  patient_id: string
  patient_number: string | null
  patient_name: string
  patient_birth_date: string | null
  patient_sex: string
  encounter_id: string | null
  encounter_number: string | null
  hospital_name: string
  ordered_by_name: string | null
  test_code: string
  test_name: string
  category: ExaminationCategory
  category_label: string
  accession_number: string
  status: ExaminationStatus
  status_label: string
  source: ExaminationSource
  source_label: string
  performed_at: string | null
  result_available_at: string | null
  overall_interpretation: ExaminationInterpretation
  overall_interpretation_label: string
  abnormal_count: number
  observations: ExaminationObservation[]
  report: DiagnosticReport | null
  created_at: string
  updated_at: string
}

export interface ExaminationContext {
  encounter_id: string
  encounter_number: string
  patient_id: string
  patient_number: string | null
  patient_name: string
  department_name: string
  created_at: string
}

export interface ExaminationListMeta {
  page: number
  page_size: number
  total_count: number
  total_pages: number
}

export interface ExaminationObservationInput {
  code: string
  name: string
  value_type: 'NUMERIC' | 'TEXT'
  numeric_value?: string | null
  text_value?: string
  unit: string
  reference_low?: string | null
  reference_high?: string | null
  reference_text: string
  interpretation: ExaminationInterpretation
}

export interface ExaminationCreateInput {
  encounter_id: string
  test_code: string
  test_name: string
  category: ExaminationCategory
  source: ExaminationSource
  performed_at: string
  observations: ExaminationObservationInput[]
  report_title: string
  report_summary: string
  report_conclusion: string
}
