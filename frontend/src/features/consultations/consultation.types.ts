export type ConsultationStatus =
  | 'REQUESTED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED'

export type ConsultationPriority =
  | 'ROUTINE'
  | 'URGENT'
  | 'EMERGENCY'

export type ConsultationBox =
  | 'all'
  | 'received'
  | 'sent'

export interface ConsultationClinician {
  clinician_id: string
  name: string
  department_name: string
  hospital_name: string
}

export interface ConsultationParticipant {
  participant_id: string
  clinician: ConsultationClinician
  role: 'REQUESTER' | 'CONSULTANT' | 'OBSERVER'
  role_label: string
  joined_at: string
  left_at: string | null
  last_read_at: string | null
}

export interface ConsultationAttachment {
  attachment_id: string
  attachment_type: string
  source_id: string | null
  display_name: string
  created_at: string
}

export interface ConsultationMessage {
  message_id: string
  sequence: number
  sender: ConsultationClinician | null
  content: string
  is_system: boolean
  edited_at: string | null
  attachments: ConsultationAttachment[]
  created_at: string
}

export interface ConsultationStatusHistory {
  history_id: string
  previous_status: string
  new_status: ConsultationStatus
  new_status_label: string
  changed_by_name: string
  reason: string
  created_at: string
}

export interface Consultation {
  consultation_id: string
  encounter_id: string
  encounter_number: string
  patient_id: string
  patient_number: string | null
  patient_name: string
  patient_birth_date: string | null
  patient_sex: string | null
  department_name: string
  requester: ConsultationClinician
  consultant: ConsultationClinician
  participants: ConsultationParticipant[]
  subject: string
  priority: ConsultationPriority
  priority_label: string
  question: string
  response: string
  status: ConsultationStatus
  status_label: string
  my_role: 'REQUESTER' | 'CONSULTANT' | 'OBSERVER'
  unread_count: number
  messages: ConsultationMessage[]
  status_history: ConsultationStatusHistory[]
  due_at: string | null
  accepted_at: string | null
  completed_at: string | null
  cancelled_at: string | null
  created_at: string
  updated_at: string
}

export interface ConsultationContext {
  encounter_id: string
  encounter_number: string
  patient_id: string
  patient_number: string | null
  patient_name: string
  department_name: string
  created_at: string
}

export interface ConsultationListMeta {
  page: number
  page_size: number
  total_count: number
  total_pages: number
}

export interface ConsultationCreateInput {
  encounter_id: string
  consultant_clinician_id: string
  subject: string
  priority: ConsultationPriority
  question: string
  due_at: string | null
}
