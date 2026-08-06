export type PrescriptionStatus =
  | 'DRAFT'
  | 'ACTIVE'
  | 'COMPLETED'
  | 'DISCONTINUED'
  | 'CANCELLED'

export interface PrescriptionItem {
  prescription_item_id: string
  medicine_name: string
  dosage: string
  dose_unit: string
  frequency: string
  route: string
  instructions: string
  start_date: string
  end_date: string | null
  meal_times: Array<'BREAKFAST' | 'LUNCH' | 'DINNER'>
}

export interface Prescription {
  prescription_id: string
  encounter_id: string
  encounter_number: string
  clinical_record_id: string
  patient_id: string
  patient_number: string | null
  patient_name: string
  clinician_name: string
  status: PrescriptionStatus
  status_label: string
  notes: string
  prescribed_at: string
  discontinued_at: string | null
  items: PrescriptionItem[]
  created_at: string
  updated_at: string
}

export interface PrescriptionContext {
  clinical_record_id: string
  encounter_id: string
  encounter_number: string
  patient_id: string
  patient_number: string | null
  patient_name: string
  recorded_at: string
}

export interface PrescriptionListMeta {
  page: number
  page_size: number
  total_count: number
  total_pages: number
}

export interface PrescriptionItemInput {
  medicine_name: string
  dosage: string
  dose_unit: string
  frequency: string
  route: string
  instructions: string
  start_date: string
  end_date: string | null
  meal_times: Array<'BREAKFAST' | 'LUNCH' | 'DINNER'>
}

export interface PrescriptionCreateInput {
  clinical_record_id: string
  status: 'DRAFT' | 'ACTIVE'
  notes: string
  items: PrescriptionItemInput[]
}
