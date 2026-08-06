export type CTCaseStatus =
  | 'UPLOADED'
  | 'VALIDATING'
  | 'READY'
  | 'PROCESSING'
  | 'COMPLETED'
  | 'FAILED'
  | 'ARCHIVED'

export type CTJobStatus =
  | 'QUEUED'
  | 'PREPARING'
  | 'RUNNING'
  | 'SUCCEEDED'
  | 'FAILED'
  | 'CANCELLED'
  | 'TIMED_OUT'

export interface CTSource {
  source_id: string
  source_type: 'IMAGING_ASSET' | 'CT_CASE'
  imaging_asset_id: string | null
  study_id: string | null
  study_description: string
  performed_at: string | null
  filename: string
  file_size_bytes: number
}

export interface CTAnalysisResult {
  result_id: string
  model_id: string
  model_version: string
  lesion_detected: boolean
  lesion_voxels: number
  lesion_volume_ml: number
  lesion_slice_count: number
  lesion_slice_indices: number[]
  lesion_slice_start: number | null
  lesion_slice_end: number | null
  max_lesion_slice: number | null
  shape: number[]
  spacing: number[]
  preprocessing_seconds: number
  inference_seconds: number
  postprocessing_seconds: number
  total_seconds: number
  end_to_end_seconds: number | null
  gpu_memory_peak_mb: number | null
  source_url: string
  mask_url: string
}

export interface CTCase {
  case_id: string
  display_id: string
  study_type: 'NCCT' | 'CTA' | 'CTP' | 'OTHER'
  study_type_label: string
  description: string
  status: CTCaseStatus
  status_label: string
  file_size_bytes: number
  patient: {
    patient_id: string
    medical_record_number: string | null
    name: string
    sex: string
    age: number | null
  } | null
  job: {
    job_id: string
    status: CTJobStatus
    progress: number
    error_code: string
    error_message: string
    error_retryable: boolean
    started_at: string | null
    completed_at: string | null
  } | null
  result: CTAnalysisResult | null
  created_at: string
  updated_at: string
}
