import type {
  Plugin,
  PluginOption,
} from 'vite'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

import {
  APPOINTMENT_DURATION_OPTIONS,
  DEFAULT_APPOINTMENT_DURATION_MINUTES,
} from './src/features/appointments/appointment.constants'

function mockApiPlugin(): Plugin {
  const hospitals = [
    {
      hospital_id: '11111111-1111-1111-1111-111111111111',
      hospital_code: 'BRN001',
      hospital_name: '브레인온 서울병원',
      address: '서울특별시 강남구 테헤란로 100',
      phone: '02-1234-5678',
    },
    {
      hospital_id: '22222222-2222-2222-2222-222222222222',
      hospital_code: 'BRN002',
      hospital_name: '브레인온 경기병원',
      address: '경기도 성남시 분당구 판교로 200',
      phone: '031-123-4567',
    },
  ]

  const departments = [
    {
      department_id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
      code: 'RADIOLOGY',
      name: '영상의학과',
      is_active: true,
    },
    {
      department_id: 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
      code: 'NEUROSURGERY',
      name: '신경외과',
      is_active: true,
    },
    {
      department_id: 'cccccccc-cccc-cccc-cccc-cccccccccccc',
      code: 'REHABILITATION_MEDICINE',
      name: '재활의학과',
      is_active: true,
    },
  ]

  let mockAccountEmail =
    'doctor@brainon.test'
  let mockAccountPassword =
    'brainon123!'

  const getMockCurrentAccount = () => ({
    user: {
      id:
        'dddddddd-dddd-dddd-dddd-dddddddddddd',
      username: '123456',
      email: mockAccountEmail,
      role: 'CLINICIAN',
    },
    clinician: {
      id:
        'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
      name: '김브레인',
      license_number: '123456',
      approval_status: 'APPROVED',
      hospital_id:
        hospitals[0].hospital_id,
      hospital_name:
        hospitals[0].hospital_name,
      department_id:
        departments[0].department_id,
      department_code:
        departments[0].code,
      department_name:
        departments[0].name,
    },
  })

  const mockPatients = [
  {
    patient_id: 'P-2026-001',
    name: '홍길동',
    age: 67,
    gender: 'M',
    department: '신경외과',
    appointment_at:
      '2026-08-03T09:00:00+09:00',
    status: 'confirmed',
    phone: '010-1111-1111',
  },
  {
    patient_id: 'P-2026-002',
    name: '김영희',
    age: 54,
    gender: 'F',
    department: '영상의학과',
    appointment_at:
      '2026-08-03T10:30:00+09:00',
    status: 'confirmed',
    phone: '010-2222-2222',
  },
  {
    patient_id: 'P-2026-003',
    name: '이민수',
    age: 42,
    gender: 'M',
    department: '재활의학과',
    appointment_at:
      '2026-08-03T13:00:00+09:00',
    status: 'waiting',
    phone: '010-3333-3333',
  },
]
  const mockPatientDirectory = [
    {
      patient_id:
        '10000000-0000-0000-0000-000000000001',

      medical_record_number:
        'P-2026-001',

      name:
        '홍길동',

      birth_date:
        '1959-04-12',

      sex:
        'M',

      phone:
        '010-1111-1111',

      status:
        'ACTIVE',
    },
    {
      patient_id:
        '10000000-0000-0000-0000-000000000002',

      medical_record_number:
        'P-2026-002',

      name:
        '김영희',

      birth_date:
        '1972-06-20',

      sex:
        'F',

      phone:
        '010-2222-2222',

      status:
        'ACTIVE',
    },
    {
      patient_id:
        '10000000-0000-0000-0000-000000000003',

      medical_record_number:
        'P-2026-003',

      name:
        '이민수',

      birth_date:
        '1984-01-15',

      sex:
        'M',

      phone:
        '010-3333-3333',

      status:
        'ACTIVE',
    },
    {
      patient_id:
        '10000000-0000-0000-0000-000000000004',

      medical_record_number:
        'P-2026-004',

      name:
        '박지수',

      birth_date:
        '1991-11-03',

      sex:
        'F',

      phone:
        '010-4444-4444',

      status:
        'INACTIVE',
    },
  ]

  const mockPrescriptionContexts = [
    {
      clinical_record_id:
        '31000000-0000-0000-0000-000000000001',
      encounter_id:
        '30000000-0000-0000-0000-000000000001',
      encounter_number:
        'E-2026-0001',
      patient_id:
        mockPatientDirectory[0].patient_id,
      patient_number:
        mockPatientDirectory[0]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[0].name,
      recorded_at:
        '2026-08-03T09:30:00+09:00',
    },
    {
      clinical_record_id:
        '31000000-0000-0000-0000-000000000002',
      encounter_id:
        '30000000-0000-0000-0000-000000000002',
      encounter_number:
        'E-2026-0002',
      patient_id:
        mockPatientDirectory[1].patient_id,
      patient_number:
        mockPatientDirectory[1]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[1].name,
      recorded_at:
        '2026-08-03T11:00:00+09:00',
    },
    {
      clinical_record_id:
        '31000000-0000-0000-0000-000000000003',
      encounter_id:
        '30000000-0000-0000-0000-000000000003',
      encounter_number:
        'E-2026-0003',
      patient_id:
        mockPatientDirectory[2].patient_id,
      patient_number:
        mockPatientDirectory[2]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[2].name,
      recorded_at:
        '2026-08-03T14:10:00+09:00',
    },
  ]

  const prescriptionStatusLabels = {
    DRAFT: '작성 중',
    ACTIVE: '처방 중',
    COMPLETED: '처방 완료',
    DISCONTINUED: '중단',
    CANCELLED: '취소',
  } as const

  let mockPrescriptions = [
    {
      prescription_id:
        '32000000-0000-0000-0000-000000000001',
      encounter_id:
        mockPrescriptionContexts[0].encounter_id,
      encounter_number:
        mockPrescriptionContexts[0]
          .encounter_number,
      clinical_record_id:
        mockPrescriptionContexts[0]
          .clinical_record_id,
      patient_id:
        mockPrescriptionContexts[0].patient_id,
      patient_number:
        mockPrescriptionContexts[0]
          .patient_number,
      patient_name:
        mockPrescriptionContexts[0]
          .patient_name,
      clinician_name: '김브레인',
      status: 'ACTIVE',
      status_label: '처방 중',
      notes: '위장 장애 발생 여부를 확인해주세요.',
      prescribed_at:
        '2026-08-03T09:40:00+09:00',
      discontinued_at:
        null as string | null,
      items: [
        {
          prescription_item_id:
            '33000000-0000-0000-0000-000000000001',
          medicine_name: '아스피린',
          dosage: '100.0000',
          dose_unit: 'mg',
          frequency: '하루 1회',
          route: '경구',
          instructions: '아침 식후 복용',
          start_date: '2026-08-03',
          end_date: '2026-08-17' as string | null,
        },
        {
          prescription_item_id:
            '33000000-0000-0000-0000-000000000003',
          medicine_name: '오메프라졸',
          dosage: '20.0000',
          dose_unit: 'mg',
          frequency: '하루 1회',
          route: '경구',
          instructions: '아침 식전 30분 복용',
          start_date: '2026-08-03',
          end_date: '2026-08-17' as string | null,
        },
      ],
      created_at:
        '2026-08-03T09:40:00+09:00',
      updated_at:
        '2026-08-03T09:40:00+09:00',
    },
    {
      prescription_id:
        '32000000-0000-0000-0000-000000000002',
      encounter_id:
        mockPrescriptionContexts[1].encounter_id,
      encounter_number:
        mockPrescriptionContexts[1]
          .encounter_number,
      clinical_record_id:
        mockPrescriptionContexts[1]
          .clinical_record_id,
      patient_id:
        mockPrescriptionContexts[1].patient_id,
      patient_number:
        mockPrescriptionContexts[1]
          .patient_number,
      patient_name:
        mockPrescriptionContexts[1]
          .patient_name,
      clinician_name: '김브레인',
      status: 'COMPLETED',
      status_label: '처방 완료',
      notes: '',
      prescribed_at:
        '2026-08-02T11:10:00+09:00',
      discontinued_at:
        null as string | null,
      items: [
        {
          prescription_item_id:
            '33000000-0000-0000-0000-000000000002',
          medicine_name: '아토르바스타틴',
          dosage: '20.0000',
          dose_unit: 'mg',
          frequency: '하루 1회',
          route: '경구',
          instructions: '저녁 식후 복용',
          start_date: '2026-08-02',
          end_date: '2026-08-16' as string | null,
        },
      ],
      created_at:
        '2026-08-02T11:10:00+09:00',
      updated_at:
        '2026-08-16T21:00:00+09:00',
    },
  ]

  let mockAppointments = [
    {
      appointment_id:
        '20000000-0000-0000-0000-000000000001',

      patient_id:
        mockPatientDirectory[0].patient_id,

      patient_number:
        mockPatientDirectory[0]
          .medical_record_number,

      patient_name:
        mockPatientDirectory[0].name,

      clinician_id:
        'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',

      clinician_name:
        '김브레인',

      department_code:
        'RADIOLOGY',

      department_name:
        '영상의학과',

      hospital_id:
        hospitals[0].hospital_id,

      hospital_name:
        hospitals[0].hospital_name,

      scheduled_at:
        '2026-08-03T09:00:00+09:00',

      duration_minutes:
        30,

      location:
        '영상검사실 1',

      reason:
        'CT 검사 결과 상담',

      status:
        'CONFIRMED',
    },
    {
      appointment_id:
        '20000000-0000-0000-0000-000000000002',

      patient_id:
        mockPatientDirectory[1].patient_id,

      patient_number:
        mockPatientDirectory[1]
          .medical_record_number,

      patient_name:
        mockPatientDirectory[1].name,

      clinician_id:
        'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',

      clinician_name:
        '김브레인',

      department_code:
        'RADIOLOGY',

      department_name:
        '영상의학과',

      hospital_id:
        hospitals[0].hospital_id,

      hospital_name:
        hospitals[0].hospital_name,

      scheduled_at:
        '2026-08-04T10:30:00+09:00',

      duration_minutes:
        30,

      location:
        '영상검사실 2',

      reason:
        'MRI 결과 확인',

      status:
        'SCHEDULED',
    },
    {
      appointment_id:
        '20000000-0000-0000-0000-000000000003',
      patient_id:
        mockPatientDirectory[0].patient_id,
      patient_number:
        mockPatientDirectory[0]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[0].name,
      clinician_id:
        'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
      clinician_name: '김브레인',
      department_code: 'RADIOLOGY',
      department_name: '영상의학과',
      hospital_id:
        hospitals[0].hospital_id,
      hospital_name:
        hospitals[0].hospital_name,
      scheduled_at:
        '2026-08-01T09:30:00+09:00',
      duration_minutes: 30,
      location: '영상검사실 1',
      reason: '정기 진료',
      status: 'COMPLETED',
    },
    {
      appointment_id:
        '20000000-0000-0000-0000-000000000004',
      patient_id:
        mockPatientDirectory[2].patient_id,
      patient_number:
        mockPatientDirectory[2]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[2].name,
      clinician_id:
        'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
      clinician_name: '김브레인',
      department_code: 'RADIOLOGY',
      department_name: '영상의학과',
      hospital_id:
        hospitals[0].hospital_id,
      hospital_name:
        hospitals[0].hospital_name,
      scheduled_at:
        '2026-08-02T13:30:00+09:00',
      duration_minutes: 30,
      location: '영상검사실 2',
      reason: '검사 결과 상담',
      status: 'CANCELLED',
    },
    {
      appointment_id:
        '20000000-0000-0000-0000-000000000005',
      patient_id:
        mockPatientDirectory[3].patient_id,
      patient_number:
        mockPatientDirectory[3]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[3].name,
      clinician_id:
        'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
      clinician_name: '김브레인',
      department_code: 'RADIOLOGY',
      department_name: '영상의학과',
      hospital_id:
        hospitals[0].hospital_id,
      hospital_name:
        hospitals[0].hospital_name,
      scheduled_at:
        '2026-08-03T15:30:00+09:00',
      duration_minutes: 30,
      location: '영상검사실 1',
      reason: 'CT 판독 상담',
      status: 'NO_SHOW',
    },
  ]

  let mockNotifications = [
    {
      notification_id:
        '30000000-0000-0000-0000-000000000001',

      type:
        'APPOINTMENT',

      title:
        '새로운 예약이 등록되었습니다.',

      body:
        '홍길동 환자의 예약이 등록되었습니다.',

      data: {
        path:
          '/appointments',

        appointment_id:
          '20000000-0000-0000-0000-000000000001',
      },

      is_read:
        false,

      read_at:
        null as string | null,

      created_at:
        '2026-08-03T10:30:00+09:00',
    },
    {
      notification_id:
        '30000000-0000-0000-0000-000000000002',

      type:
        'TEST_RESULT',

      title:
        '검사 결과가 등록되었습니다.',

      body:
        '김영희 환자의 검사 결과를 확인해주세요.',

      data: {
        path:
          '/patients?search=P-2026-002',

        patient_id:
          '10000000-0000-0000-0000-000000000002',
      },

      is_read:
        false,

      read_at:
        null as string | null,

      created_at:
        '2026-08-03T10:00:00+09:00',
    },
    {
      notification_id:
        '30000000-0000-0000-0000-000000000003',

      type:
        'CONSULTATION',

      title:
        '협진 답변이 도착했습니다.',

      body:
        '이민수 환자의 협진 답변을 확인해주세요.',

      data: {
        path:
          '/patients?search=P-2026-003',

        patient_id:
          '10000000-0000-0000-0000-000000000003',
      },

      is_read:
        true,

      read_at:
        '2026-08-03T09:30:00+09:00' as string | null,

      created_at:
        '2026-08-03T09:00:00+09:00',
    },
  ]

  let mockNotificationSettings = {
    global_setting: {
      quiet_hours_enabled:
        false,
      quiet_hours_start:
        null as string | null,
      quiet_hours_end:
        null as string | null,
    },
    preferences: [
      {
        notification_type:
          'APPOINTMENT',
        push_enabled: true,
        email_enabled: false,
      },
      {
        notification_type:
          'TEST_RESULT',
        push_enabled: true,
        email_enabled: false,
      },
      {
        notification_type:
          'CONSULTATION',
        push_enabled: true,
        email_enabled: false,
      },
      {
        notification_type:
          'SYSTEM',
        push_enabled: true,
        email_enabled: false,
      },
    ],
  }

  let mockNotificationDevices: Array<{
    device_id: string
    platform: 'WEB'
    client_type: 'CLINICIAN_WEB'
    device_identifier: string
    fcm_token: string
    device_name: string
    app_version: string
    is_active: boolean
    registered_at: string
    last_used_at: string
  }> = []

  const mockConsultations = [
    {
      consultation_id: 1,
      status: 'requested',
      department: '신경외과',
      title: '뇌출혈 수술 여부 협진 요청',
      patient_id: 'P-2026-001',
      patient_display:
        '홍길동 (P-2026-001)',
      requested_at:
        '2026-08-03T09:20:00+09:00',
      responded_at: null,
    },
    {
      consultation_id: 2,
      status: 'answered',
      department: '재활의학과',
      title: '수술 후 재활 계획 문의',
      patient_id: 'P-2026-003',
      patient_display:
        '이민수 (P-2026-003)',
      requested_at:
        '2026-08-03T08:30:00+09:00',
      responded_at:
        '2026-08-03T10:00:00+09:00',
    },
  ]

  const mockTests = [
    { id: 1, status: 'processing' },
    { id: 2, status: 'result_waiting' },
    { id: 3, status: 'result_waiting' },
    { id: 4, status: 'result_waiting' },
  ]

  const mockCtAnalyses = [
    {
      id: 1,
      case_id:
        '34000000-0000-0000-0000-000000000001',
      patient_id:
        mockPatientDirectory[0].patient_id,
      patient_number:
        mockPatientDirectory[0]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[0].name,
      status: 'processing',
      study_type: '비조영 뇌 CT',
      case_status: 'PROCESSING',
      case_status_label: '추론 중',
      description: '뇌출혈 의심 영역 분석',
      performed_at:
        '2026-08-03T08:40:00+09:00',
      created_at:
        '2026-08-03T09:00:00+09:00',
    },
    {
      id: 2,
      case_id:
        '34000000-0000-0000-0000-000000000002',
      patient_id:
        mockPatientDirectory[1].patient_id,
      patient_number:
        mockPatientDirectory[1]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[1].name,
      status: 'completed',
      study_type: 'CT 혈관조영',
      case_status: 'COMPLETED',
      case_status_label: '분석 완료',
      description: '혈관 폐색 여부 분석',
      performed_at:
        '2026-08-02T08:30:00+09:00',
      created_at:
        '2026-08-02T09:00:00+09:00',
    },
  ]

  const encounterStatusLabels: Record<string, string> = {
    REGISTERED: '등록',
    ARRIVED: '도착',
    IN_PROGRESS: '진료 중',
    COMPLETED: '완료',
    CANCELLED: '취소',
  }

  let mockEncounters = [
    {
      encounter_id:
        '30000000-0000-0000-0000-000000000002',
      encounter_number: 'E-2026-0002',
      encounter_type: 'OUTPATIENT',
      encounter_type_label: '외래',
      status: 'ARRIVED' as string,
      status_label: '도착',
      patient_id:
        mockPatientDirectory[1].patient_id,
      patient_number:
        mockPatientDirectory[1]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[1].name,
      patient_birth_date:
        mockPatientDirectory[1].birth_date,
      patient_sex:
        mockPatientDirectory[1].sex,
      appointment_id:
        mockAppointments[1].appointment_id,
      scheduled_at:
        mockAppointments[1].scheduled_at,
      appointment_reason:
        mockAppointments[1].reason,
      department_name: '영상의학과',
      arrived_at:
        '2026-08-04T10:20:00+09:00' as string | null,
      started_at: null as string | null,
      completed_at: null as string | null,
      created_at:
        '2026-08-04T10:20:00+09:00',
    },
    {
      encounter_id:
        '30000000-0000-0000-0000-000000000001',
      encounter_number: 'E-2026-0001',
      encounter_type: 'OUTPATIENT',
      encounter_type_label: '외래',
      status: 'IN_PROGRESS' as string,
      status_label: '진료 중',
      patient_id:
        mockPatientDirectory[0].patient_id,
      patient_number:
        mockPatientDirectory[0]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[0].name,
      patient_birth_date:
        mockPatientDirectory[0].birth_date,
      patient_sex:
        mockPatientDirectory[0].sex,
      appointment_id:
        mockAppointments[0].appointment_id,
      scheduled_at:
        mockAppointments[0].scheduled_at,
      appointment_reason:
        mockAppointments[0].reason,
      department_name: '영상의학과',
      arrived_at:
        '2026-08-03T08:50:00+09:00' as string | null,
      started_at:
        '2026-08-03T09:03:00+09:00' as string | null,
      completed_at: null as string | null,
      created_at:
        '2026-08-03T08:50:00+09:00',
    },
    {
      encounter_id:
        '30000000-0000-0000-0000-000000000003',
      encounter_number: 'E-2026-0003',
      encounter_type: 'OUTPATIENT',
      encounter_type_label: '외래',
      status: 'COMPLETED' as string,
      status_label: '완료',
      patient_id:
        mockPatientDirectory[2].patient_id,
      patient_number:
        mockPatientDirectory[2]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[2].name,
      patient_birth_date:
        mockPatientDirectory[2].birth_date,
      patient_sex:
        mockPatientDirectory[2].sex,
      appointment_id: null as string | null,
      scheduled_at:
        '2026-08-02T13:30:00+09:00' as string | null,
      appointment_reason: '검사 결과 상담' as string | null,
      department_name: '영상의학과',
      arrived_at:
        '2026-08-02T13:20:00+09:00' as string | null,
      started_at:
        '2026-08-02T13:32:00+09:00' as string | null,
      completed_at:
        '2026-08-02T14:05:00+09:00' as string | null,
      created_at:
        '2026-08-02T13:20:00+09:00',
    },
    {
      encounter_id:
        '30000000-0000-0000-0000-000000000004',
      encounter_number: 'E-2026-0004',
      encounter_type: 'OUTPATIENT',
      encounter_type_label: '외래',
      status: 'COMPLETED' as string,
      status_label: '완료',
      patient_id:
        mockPatientDirectory[0].patient_id,
      patient_number:
        mockPatientDirectory[0]
          .medical_record_number,
      patient_name:
        mockPatientDirectory[0].name,
      patient_birth_date:
        mockPatientDirectory[0].birth_date,
      patient_sex:
        mockPatientDirectory[0].sex,
      appointment_id: null as string | null,
      scheduled_at:
        '2026-07-15T10:00:00+09:00' as string | null,
      appointment_reason: '두통 추적 진료' as string | null,
      department_name: '영상의학과',
      arrived_at:
        '2026-07-15T09:50:00+09:00' as string | null,
      started_at:
        '2026-07-15T10:02:00+09:00' as string | null,
      completed_at:
        '2026-07-15T10:35:00+09:00' as string | null,
      created_at:
        '2026-07-15T09:50:00+09:00',
    },
  ]

  type MockClinicalRecord = {
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

  const mockEncounterRecords: Record<
    string,
    MockClinicalRecord
  > = {
    '30000000-0000-0000-0000-000000000001': {
      clinical_record_id:
        '31000000-0000-0000-0000-000000000001',
      recorded_at:
        '2026-08-03T09:25:00+09:00',
      chief_complaint: '간헐적인 두통과 어지럼증',
      subjective: '3일 전부터 두통이 반복됨',
      objective: '의식 명료, CT 영상 확인 중',
      assessment: '영상 판독 후 추가 평가 필요',
      plan: 'CT 분석 결과 확인 및 약물 처방',
      patient_visible_summary:
        'CT 결과 확인 후 치료 계획을 안내할 예정입니다.',
      created_at:
        '2026-08-03T09:25:00+09:00',
      updated_at:
        '2026-08-03T09:25:00+09:00',
    },
    '30000000-0000-0000-0000-000000000003': {
      clinical_record_id:
        '31000000-0000-0000-0000-000000000003',
      recorded_at:
        '2026-08-02T14:00:00+09:00',
      chief_complaint: '검사 결과 상담',
      subjective: '특이 증상 없음',
      objective: 'CT 결과 안정적',
      assessment: '추적 관찰',
      plan: '외래 추적 진료',
      patient_visible_summary:
        '현재 검사 결과는 안정적이며 추적 진료가 필요합니다.',
      created_at:
        '2026-08-02T14:00:00+09:00',
      updated_at:
        '2026-08-02T14:00:00+09:00',
    },
    '30000000-0000-0000-0000-000000000004': {
      clinical_record_id:
        '31000000-0000-0000-0000-000000000004',
      recorded_at:
        '2026-07-15T10:30:00+09:00',
      chief_complaint: '반복되는 두통',
      subjective: '최근 일주일간 오후에 두통이 심해짐',
      objective: '신경학적 이상 소견 없음',
      assessment: '긴장성 두통 의심',
      plan: '생활 습관 교정 및 필요 시 진통제 복용',
      patient_visible_summary:
        '생활 습관을 조절하고 증상이 지속되면 재진해주세요.',
      created_at:
        '2026-07-15T10:30:00+09:00',
      updated_at:
        '2026-07-15T10:30:00+09:00',
    },
  }

  const buildMockEncounterDetail = (
    encounter: (typeof mockEncounters)[number],
  ) => ({
    ...encounter,
    clinician_id:
      'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
    clinician_name: '김브레인',
    hospital_name: hospitals[0].hospital_name,
    clinical_record:
      mockEncounterRecords[encounter.encounter_id]
      ?? null,
    prescriptions: mockPrescriptions
      .filter(
        (prescription) =>
          prescription.encounter_id
          === encounter.encounter_id,
      )
      .map((prescription) => ({
        prescription_id:
          prescription.prescription_id,
        status: prescription.status,
        status_label:
          prescription.status_label,
        prescribed_at:
          prescription.prescribed_at,
        medicine_names:
          prescription.items.map(
            (item) => item.medicine_name,
          ),
      })),
    ct_cases: mockCtAnalyses
      .filter(
        (analysis) =>
          analysis.patient_id
          === encounter.patient_id,
      )
      .map((analysis) => ({
        case_id: analysis.case_id,
        study_type:
          analysis.study_type.includes('혈관')
            ? 'CTA'
            : 'NCCT',
        study_type_label: analysis.study_type,
        status: analysis.case_status,
        status_label:
          analysis.case_status_label,
        performed_at: analysis.performed_at,
        created_at: analysis.created_at,
      })),
  })

  const mockActivities = [
  {
    activity_id: 1,
    occurred_at:
      '2026-08-03T09:10:00+09:00',
    message:
      '홍길동 환자의 진료 기록이 등록되었습니다.',
    type: 'medical_record',
  },
  {
    activity_id: 2,
    occurred_at:
      '2026-08-03T09:40:00+09:00',
    message:
      '김영희 환자의 검사 결과가 등록되었습니다.',
    type: 'test_result',
  },
  {
    activity_id: 3,
    occurred_at:
      '2026-08-03T10:00:00+09:00',
    message:
      '이민수 환자의 협진 답변이 등록되었습니다.',
    type: 'consultation',
  },
  {
    activity_id: 4,
    occurred_at:
      '2026-08-03T10:30:00+09:00',
    message:
      '홍길동 환자의 CT 분석이 완료되었습니다.',
    type: 'ct_analysis',
  },
  {
    activity_id: 5,
    occurred_at:
      '2026-08-03T11:00:00+09:00',
    message:
      '김영희 환자의 처방전이 작성되었습니다.',
    type: 'prescription',
  },
]

  const mockSchedules = [
    {
      schedule_id: 1,
      start_at:
        '2026-08-03T09:00:00+09:00',
      patient_id: 'P-2026-001',
      patient_name: '홍길동',
      room: '신경외과 제1진료실',
      status: 'completed',
    },
    {
      schedule_id: 2,
      start_at:
        '2026-08-03T10:30:00+09:00',
      patient_id: 'P-2026-002',
      patient_name: '김영희',
      room: '영상검사실',
      status: 'in_progress',
    },
    {
      schedule_id: 3,
      start_at:
        '2026-08-03T13:00:00+09:00',
      patient_id: 'P-2026-003',
      patient_name: '이민수',
      room: '재활치료실',
      status: 'scheduled',
    },
  ]

  function sendJson(
    response: import('node:http').ServerResponse,
    status: number,
    body: unknown,
  ) {
    response.statusCode = status
    response.setHeader('Content-Type', 'application/json; charset=utf-8')
    response.end(JSON.stringify(body))
  }

  async function readJson(
    request: import('node:http').IncomingMessage,
  ): Promise<Record<string, unknown>> {
    const chunks: Buffer[] = []

    for await (const chunk of request) {
      chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk))
    }

    if (chunks.length === 0) return {}

    try {
      return JSON.parse(Buffer.concat(chunks).toString('utf8')) as Record<
        string,
        unknown
      >
    } catch {
      return {}
    }
  }

  return {
    name: 'brainon-mock-api',
    configureServer(server) {
      server.middlewares.use(async (request, response, next) => {
        const url = new URL(request.url ?? '/', 'http://localhost')

        if (
          request.method === 'POST'
          && url.pathname
            === '/api/v1/notifications/devices/register/'
        ) {
          const body = await readJson(request)
          const platform = String(
            body.platform ?? '',
          )
          const clientType = String(
            body.client_type ?? '',
          )
          const deviceIdentifier = String(
            body.device_identifier ?? '',
          )
          const fcmToken = String(
            body.fcm_token ?? '',
          )

          if (
            platform !== 'WEB'
            || clientType
              !== 'CLINICIAN_WEB'
            || !deviceIdentifier
            || !fcmToken
          ) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',
                message:
                  '웹 알림 기기 정보를 확인해주세요.',
                details: {},
              },
            })

            return
          }

          const now =
            new Date().toISOString()

          const existingIndex =
            mockNotificationDevices.findIndex(
              (device) =>
                device.device_identifier
                  === deviceIdentifier
                || device.fcm_token
                  === fcmToken,
            )

          const registeredAt =
            existingIndex >= 0
              ? mockNotificationDevices[
                existingIndex
              ].registered_at
              : now

          const device = {
            device_id:
              existingIndex >= 0
                ? mockNotificationDevices[
                  existingIndex
                ].device_id
                : crypto.randomUUID(),
            platform:
              'WEB' as const,
            client_type:
              'CLINICIAN_WEB' as const,
            device_identifier:
              deviceIdentifier,
            fcm_token:
              fcmToken,
            device_name:
              String(
                body.device_name ?? '',
              ),
            app_version:
              String(
                body.app_version ?? '',
              ),
            is_active:
              true,
            registered_at:
              registeredAt,
            last_used_at:
              now,
          }

          if (existingIndex >= 0) {
            mockNotificationDevices = [
              ...mockNotificationDevices.slice(
                0,
                existingIndex,
              ),
              device,
              ...mockNotificationDevices.slice(
                existingIndex + 1,
              ),
            ]
          } else {
            mockNotificationDevices = [
              ...mockNotificationDevices,
              device,
            ]
          }

          sendJson(
            response,
            existingIndex >= 0 ? 200 : 201,
            {
              data: {
                device_id:
                  device.device_id,
                platform:
                  device.platform,
                client_type:
                  device.client_type,
                device_identifier:
                  device.device_identifier,
                device_name:
                  device.device_name,
                app_version:
                  device.app_version,
                is_active:
                  device.is_active,
                registered_at:
                  device.registered_at,
                last_used_at:
                  device.last_used_at,
              },
            },
          )

          return
        }

        if (
          request.method === 'POST'
          && url.pathname
            === '/api/v1/notifications/devices/unregister/'
        ) {
          const body = await readJson(request)
          const deviceIdentifier = String(
            body.device_identifier ?? '',
          )
          const clientType = String(
            body.client_type ?? '',
          )
          const now =
            new Date().toISOString()
          let updatedCount = 0

          mockNotificationDevices =
            mockNotificationDevices.map(
              (device) => {
                if (
                  device.device_identifier
                    !== deviceIdentifier
                  || device.client_type
                    !== clientType
                  || !device.is_active
                ) {
                  return device
                }

                updatedCount += 1

                return {
                  ...device,
                  is_active: false,
                  last_used_at: now,
                }
              },
            )

          sendJson(response, 200, {
            data: {
              updated_count:
                updatedCount,
            },
          })

          return
        }

        if (
          request.method === 'GET'
          && url.pathname === '/api/v1/encounters/'
        ) {
          const dateFrom =
            url.searchParams.get('date_from') ?? ''
          const dateTo =
            url.searchParams.get('date_to') ?? ''
          const requestedStatus = (
            url.searchParams.get('status') ?? ''
          ).toUpperCase()
          const search = (
            url.searchParams.get('search') ?? ''
          ).trim().toLowerCase()
          const page = Math.max(
            1,
            Number(url.searchParams.get('page') ?? 1),
          )
          const pageSize = Math.min(
            100,
            Math.max(
              1,
              Number(
                url.searchParams.get('page_size')
                ?? 20,
              ),
            ),
          )
          const filtered = mockEncounters
            .filter((encounter) => {
              const activityDate = (
                encounter.arrived_at
                ?? encounter.created_at
              ).slice(0, 10)
              const matchesDate = (
                (!dateFrom || activityDate >= dateFrom)
                && (!dateTo || activityDate <= dateTo)
              )
              const matchesStatus = (
                !requestedStatus
                || encounter.status === requestedStatus
              )
              const matchesSearch = (
                !search
                || encounter.patient_name
                  .toLowerCase().includes(search)
                || (encounter.patient_number ?? '')
                  .toLowerCase().includes(search)
                || encounter.encounter_number
                  .toLowerCase().includes(search)
              )

              return matchesDate
                && matchesStatus
                && matchesSearch
            })
            .sort((left, right) => (
              right.created_at.localeCompare(
                left.created_at,
              )
            ))
          const startIndex = (page - 1) * pageSize

          sendJson(response, 200, {
            data: filtered.slice(
              startIndex,
              startIndex + pageSize,
            ),
            meta: {
              page,
              page_size: pageSize,
              total_count: filtered.length,
              total_pages: Math.max(
                1,
                Math.ceil(filtered.length / pageSize),
              ),
            },
          })
          return
        }

        const encounterRecordMatch =
          url.pathname.match(
            /^\/api\/v1\/encounters\/([^/]+)\/clinical-record\/$/,
          )

        if (
          request.method === 'PUT'
          && encounterRecordMatch
        ) {
          const encounterId = decodeURIComponent(
            encounterRecordMatch[1],
          )
          const encounter = mockEncounters.find(
            (item) => item.encounter_id === encounterId,
          )

          if (!encounter) {
            sendJson(response, 404, {
              error: {
                code: 'NOT_FOUND',
                message: '진료 건을 찾을 수 없습니다.',
                details: {},
              },
            })
            return
          }

          const body = await readJson(request)
          const now = new Date().toISOString()
          const existing =
            mockEncounterRecords[encounterId]
          const saved: MockClinicalRecord = {
            clinical_record_id:
              existing?.clinical_record_id
              ?? crypto.randomUUID(),
            recorded_at: now,
            chief_complaint: String(
              body.chief_complaint ?? '',
            ),
            subjective: String(body.subjective ?? ''),
            objective: String(body.objective ?? ''),
            assessment: String(body.assessment ?? ''),
            plan: String(body.plan ?? ''),
            patient_visible_summary: String(
              body.patient_visible_summary ?? '',
            ),
            created_at: existing?.created_at ?? now,
            updated_at: now,
          }

          mockEncounterRecords[encounterId] = saved
          sendJson(response, existing ? 200 : 201, {
            data: saved,
          })
          return
        }

        const encounterStatusMatch =
          url.pathname.match(
            /^\/api\/v1\/encounters\/([^/]+)\/status\/$/,
          )

        if (
          request.method === 'PATCH'
          && encounterStatusMatch
        ) {
          const encounterId = decodeURIComponent(
            encounterStatusMatch[1],
          )
          const index = mockEncounters.findIndex(
            (item) => item.encounter_id === encounterId,
          )
          const body = await readJson(request)
          const nextStatus = String(body.status ?? '')

          if (index < 0) {
            sendJson(response, 404, {
              error: {
                code: 'NOT_FOUND',
                message: '진료 건을 찾을 수 없습니다.',
                details: {},
              },
            })
            return
          }

          const current = mockEncounters[index]
          const validTransition = (
            current.status === 'ARRIVED'
            && nextStatus === 'IN_PROGRESS'
          ) || (
            current.status === 'IN_PROGRESS'
            && nextStatus === 'COMPLETED'
          )

          if (!validTransition) {
            sendJson(response, 400, {
              error: {
                code: 'INVALID_STATUS_TRANSITION',
                message: '허용되지 않은 진료 상태 변경입니다.',
                details: {},
              },
            })
            return
          }

          if (
            nextStatus === 'COMPLETED'
            && !mockEncounterRecords[encounterId]
          ) {
            sendJson(response, 400, {
              error: {
                code: 'CLINICAL_RECORD_REQUIRED',
                message:
                  '진료기록을 저장한 후 진료를 완료해주세요.',
                details: {},
              },
            })
            return
          }

          const now = new Date().toISOString()
          const updated = {
            ...current,
            status: nextStatus,
            status_label:
              encounterStatusLabels[nextStatus]
              ?? nextStatus,
            started_at:
              nextStatus === 'IN_PROGRESS'
                ? current.started_at ?? now
                : current.started_at,
            completed_at:
              nextStatus === 'COMPLETED'
                ? now
                : current.completed_at,
          }
          mockEncounters = [
            ...mockEncounters.slice(0, index),
            updated,
            ...mockEncounters.slice(index + 1),
          ]

          sendJson(response, 200, {
            data: buildMockEncounterDetail(updated),
          })
          return
        }

        const encounterDetailMatch =
          url.pathname.match(
            /^\/api\/v1\/encounters\/([^/]+)\/$/,
          )

        if (
          request.method === 'GET'
          && encounterDetailMatch
        ) {
          const encounterId = decodeURIComponent(
            encounterDetailMatch[1],
          )
          const encounter = mockEncounters.find(
            (item) => item.encounter_id === encounterId,
          )

          if (!encounter) {
            sendJson(response, 404, {
              error: {
                code: 'NOT_FOUND',
                message: '진료 건을 찾을 수 없습니다.',
                details: {},
              },
            })
            return
          }

          sendJson(response, 200, {
            data: buildMockEncounterDetail(encounter),
          })
          return
        }

        if (
          request.method === 'GET'
          && url.pathname
            === '/api/v1/reports/clinician-details/'
        ) {
          const detailType =
            url.searchParams.get('type') ?? ''
          const startDate =
            url.searchParams.get('start_date') ?? ''
          const endDate =
            url.searchParams.get('end_date') ?? ''
          const requestedStatus = (
            url.searchParams.get('status') ?? ''
          ).toUpperCase()
          const requestedMedicine =
            url.searchParams.get('medicine') ?? ''
          const page = Math.max(
            1,
            Number(url.searchParams.get('page') ?? 1),
          )
          const pageSize = Math.min(
            100,
            Math.max(
              1,
              Number(
                url.searchParams.get('page_size')
                ?? 20,
              ),
            ),
          )
          const validTypes = [
            'encounters',
            'appointments',
            'prescriptions',
            'ct_analyses',
          ]
          const datePattern = /^\d{4}-\d{2}-\d{2}$/
          const startTime = new Date(
            `${startDate}T00:00:00Z`,
          ).getTime()
          const endTime = new Date(
            `${endDate}T00:00:00Z`,
          ).getTime()

          if (
            !validTypes.includes(detailType)
            || !datePattern.test(startDate)
            || !datePattern.test(endDate)
            || Number.isNaN(startTime)
            || Number.isNaN(endTime)
            || endTime < startTime
            || endTime - startTime
              > 366 * 24 * 60 * 60 * 1000
          ) {
            sendJson(response, 400, {
              error: {
                code: 'VALIDATION_ERROR',
                message: '상세 조회 조건을 확인해주세요.',
                details: {},
              },
            })
            return
          }

          const inPeriod = (value: string) => {
            const date = value.slice(0, 10)

            return date >= startDate
              && date <= endDate
          }
          let details: Array<{
            record_id: string
            type: string
            patient_id: string | null
            patient_number: string | null
            patient_name: string
            occurred_at: string
            reference: string
            status: string
            status_label: string
            details: Record<string, unknown>
          }> = []

          if (detailType === 'encounters') {
            details = mockAppointments
              .filter(
                (appointment) =>
                  appointment.status === 'COMPLETED'
                  && inPeriod(
                    appointment.scheduled_at,
                  ),
              )
              .map((appointment, index) => ({
                record_id:
                  `35000000-0000-0000-0000-${String(
                    index + 1,
                  ).padStart(12, '0')}`,
                type: detailType,
                patient_id: appointment.patient_id,
                patient_number:
                  appointment.patient_number,
                patient_name:
                  appointment.patient_name,
                occurred_at:
                  appointment.scheduled_at,
                reference:
                  `E-2026-${String(index + 1)
                    .padStart(4, '0')}`,
                status: 'COMPLETED',
                status_label: '완료',
                details: {
                  encounter_type: '외래',
                  started_at:
                    appointment.scheduled_at,
                  completed_at:
                    appointment.scheduled_at,
                },
              }))
          }

          if (detailType === 'appointments') {
            const statusLabels: Record<string, string> = {
              SCHEDULED: '예약',
              CONFIRMED: '확정',
              CHECKED_IN: '접수',
              COMPLETED: '완료',
              CANCELLED: '취소',
              NO_SHOW: '노쇼',
            }

            details = mockAppointments
              .filter(
                (appointment) =>
                  inPeriod(appointment.scheduled_at)
                  && (
                    !requestedStatus
                    || appointment.status
                      === requestedStatus
                  ),
              )
              .map((appointment) => ({
                record_id:
                  appointment.appointment_id,
                type: detailType,
                patient_id: appointment.patient_id,
                patient_number:
                  appointment.patient_number,
                patient_name:
                  appointment.patient_name,
                occurred_at:
                  appointment.scheduled_at,
                reference:
                  `예약 ${appointment.appointment_id}`,
                status: appointment.status,
                status_label:
                  statusLabels[appointment.status]
                  ?? appointment.status,
                details: {
                  duration_minutes:
                    appointment.duration_minutes,
                  location: appointment.location,
                  reason: appointment.reason,
                  cancellation_reason:
                    appointment.status === 'CANCELLED'
                      ? '환자 요청으로 취소'
                      : '',
                },
              }))
          }

          if (detailType === 'prescriptions') {
            details = mockPrescriptions
              .filter(
                (prescription) =>
                  inPeriod(prescription.prescribed_at)
                  && (
                    !requestedStatus
                    || prescription.status
                      === requestedStatus
                  )
                  && (
                    !requestedMedicine
                    || prescription.items.some(
                      (item) =>
                        item.medicine_name
                          === requestedMedicine,
                    )
                  ),
              )
              .map((prescription) => ({
                record_id:
                  prescription.prescription_id,
                type: detailType,
                patient_id: prescription.patient_id,
                patient_number:
                  prescription.patient_number,
                patient_name:
                  prescription.patient_name,
                occurred_at:
                  prescription.prescribed_at,
                reference:
                  prescription.encounter_number,
                status: prescription.status,
                status_label:
                  prescription.status_label,
                details: {
                  notes: prescription.notes,
                  items: prescription.items.map(
                    (item) => ({
                      medicine_name:
                        item.medicine_name,
                      dosage: item.dosage,
                      dose_unit: item.dose_unit,
                      frequency: item.frequency,
                      route: item.route,
                    }),
                  ),
                },
              }))
          }

          if (detailType === 'ct_analyses') {
            details = mockCtAnalyses
              .filter((analysis) =>
                inPeriod(analysis.created_at),
              )
              .map((analysis) => ({
                record_id: analysis.case_id,
                type: detailType,
                patient_id: analysis.patient_id,
                patient_number:
                  analysis.patient_number,
                patient_name: analysis.patient_name,
                occurred_at: analysis.created_at,
                reference: `CT ${analysis.case_id}`,
                status:
                  analysis.status === 'completed'
                    ? 'SUCCEEDED'
                    : 'RUNNING',
                status_label:
                  analysis.status === 'completed'
                    ? '완료'
                    : '추론 중',
                details: {
                  study_type: analysis.study_type,
                  case_status: analysis.case_status,
                  case_status_label:
                    analysis.case_status_label,
                  description: analysis.description,
                  performed_at: analysis.performed_at,
                },
              }))
          }

          details.sort((left, right) =>
            right.occurred_at.localeCompare(
              left.occurred_at,
            ),
          )
          const startIndex = (page - 1) * pageSize

          sendJson(response, 200, {
            data: details.slice(
              startIndex,
              startIndex + pageSize,
            ),
            meta: {
              page,
              page_size: pageSize,
              total_count: details.length,
              total_pages: Math.max(
                1,
                Math.ceil(details.length / pageSize),
              ),
            },
          })
          return
        }

        if (
          request.method === 'GET'
          && url.pathname
            === '/api/v1/notifications/settings/'
        ) {
          sendJson(response, 200, {
            data:
              mockNotificationSettings,
          })

          return
        }

        if (
          request.method === 'PATCH'
          && url.pathname
            === '/api/v1/notifications/settings/'
        ) {
          const body = await readJson(request)

          const globalSetting =
            body.global_setting

          const preferences =
            body.preferences

          if (
            !globalSetting
            || typeof globalSetting
              !== 'object'
            || !Array.isArray(preferences)
          ) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',
                message:
                  '알림 설정 값을 확인해주세요.',
                details: {},
              },
            })

            return
          }

          const globalSettingData =
            globalSetting as
              Record<string, unknown>

          const quietHoursEnabled =
            Boolean(
              globalSettingData
                .quiet_hours_enabled,
            )

          const quietHoursStart =
            typeof globalSettingData
              .quiet_hours_start === 'string'
              ? globalSettingData
                .quiet_hours_start
              : null

          const quietHoursEnd =
            typeof globalSettingData
              .quiet_hours_end === 'string'
              ? globalSettingData
                .quiet_hours_end
              : null

          if (
            quietHoursEnabled
            && (
              !quietHoursStart
              || !quietHoursEnd
              || quietHoursStart
                === quietHoursEnd
            )
          ) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',
                message:
                  '방해금지 시간을 확인해주세요.',
                details: {},
              },
            })

            return
          }

          const allowedTypes = [
            'APPOINTMENT',
            'TEST_RESULT',
            'CONSULTATION',
            'SYSTEM',
          ]

          const nextPreferences =
            preferences.map(
              (value) => {
                const item = value as
                  Record<string, unknown>

                return {
                  notification_type:
                    String(
                      item.notification_type
                      ?? '',
                    ),
                  push_enabled:
                    Boolean(
                      item.push_enabled,
                    ),
                  email_enabled:
                    Boolean(
                      item.email_enabled,
                    ),
                }
              },
            )

          const invalidPreference =
            nextPreferences.some(
              (preference) =>
                !allowedTypes.includes(
                  preference.notification_type,
                ),
            )

          if (invalidPreference) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',
                message:
                  '지원하지 않는 알림 유형입니다.',
                details: {},
              },
            })

            return
          }

          mockNotificationSettings = {
            global_setting: {
              quiet_hours_enabled:
                quietHoursEnabled,
              quiet_hours_start:
                quietHoursStart,
              quiet_hours_end:
                quietHoursEnd,
            },
            preferences:
              nextPreferences,
          }

          sendJson(response, 200, {
            data:
              mockNotificationSettings,
          })

          return
        }

        if (
          request.method === 'GET'
          && url.pathname
            === '/api/v1/notifications/'
        ) {
          sendJson(response, 200, {
            data:
              mockNotifications,

            meta: {
              unread_count:
                mockNotifications.filter(
                  (notification) =>
                    !notification.is_read,
                ).length,
            },
          })

          return
        }

        const notificationReadMatch =
          url.pathname.match(
            /^\/api\/v1\/notifications\/([^/]+)\/read\/$/,
          )

        if (
          request.method === 'PATCH'
          && notificationReadMatch
        ) {
          const notificationId =
            decodeURIComponent(
              notificationReadMatch[1],
            )

          const notificationIndex =
            mockNotifications.findIndex(
              (notification) =>
                notification.notification_id
                === notificationId,
            )

          if (notificationIndex < 0) {
            sendJson(response, 404, {
              error: {
                code:
                  'NOTIFICATION_NOT_FOUND',

                message:
                  '알림을 찾을 수 없습니다.',

                details: {},
              },
            })

            return
          }

          const currentNotification =
            mockNotifications[
              notificationIndex
            ]

          const updatedNotification = {
            ...currentNotification,

            is_read:
              true,

            read_at:
              currentNotification.read_at
              ?? new Date().toISOString(),
          }

          mockNotifications = [
            ...mockNotifications.slice(
              0,
              notificationIndex,
            ),

            updatedNotification,

            ...mockNotifications.slice(
              notificationIndex + 1,
            ),
          ]

          sendJson(response, 200, {
            data:
              updatedNotification,
          })

          return
        }

        if (
          request.method === 'POST'
          && url.pathname
            === '/api/v1/notifications/read-all/'
        ) {
          const readAt =
            new Date().toISOString()

          const updatedCount =
            mockNotifications.filter(
              (notification) =>
                !notification.is_read,
            ).length

          mockNotifications =
            mockNotifications.map(
              (notification) => ({
                ...notification,

                is_read:
                  true,

                read_at:
                  notification.read_at
                  ?? readAt,
              }),
            )

          sendJson(response, 200, {
            data: {
              updated_count:
                updatedCount,
            },
          })

          return
        }

        if (
          request.method === 'GET'
          && url.pathname === '/api/v1/hospitals/'
        ) {
          const keyword = (url.searchParams.get('search') ?? '').toLowerCase()
          const results = hospitals.filter((hospital) =>
            [
              hospital.hospital_name,
              hospital.hospital_code,
              hospital.address,
            ]
              .join(' ')
              .toLowerCase()
              .includes(keyword),
          )

          sendJson(response, 200, {
            data: results,
            meta: {
              page: 1,
              page_size: 20,
              total_count: results.length,
              total_pages: 1,
            },
          })
          return
        }

        if (
          request.method === 'GET'
          && url.pathname
            === '/api/v1/appointments/'
        ) {
          const dateFrom =
            url.searchParams.get(
              'date_from',
            )

          const dateTo =
            url.searchParams.get(
              'date_to',
            )

          const requestedStatus =
            url.searchParams.get(
              'status',
            )

          const results =
            mockAppointments
              .filter((appointment) => {
                const appointmentDate =
                  appointment.scheduled_at
                    .slice(0, 10)

                const matchesStart =
                  !dateFrom
                  || appointmentDate
                    >= dateFrom

                const matchesEnd =
                  !dateTo
                  || appointmentDate
                    <= dateTo

                const matchesStatus =
                  !requestedStatus
                  || appointment.status
                    === requestedStatus

                return (
                  matchesStart
                  && matchesEnd
                  && matchesStatus
                )
              })
              .sort(
                (left, right) =>
                  new Date(
                    left.scheduled_at,
                  ).getTime()
                  - new Date(
                    right.scheduled_at,
                  ).getTime(),
              )

          sendJson(response, 200, {
            data: results,

            meta: {
              total_count:
                results.length,
            },
          })

          return
        }

        if (
          request.method === 'POST'
          && url.pathname
            === '/api/v1/appointments/'
        ) {
          const body =
            await readJson(request)

          const patientId =
            String(
              body.patient_id
              ?? '',
            )

          const scheduledAt =
            String(
              body.scheduled_at
              ?? '',
            )

          const durationMinutes =
            Number(
              body.duration_minutes
              ?? DEFAULT_APPOINTMENT_DURATION_MINUTES,
            )

          const validDuration =
            APPOINTMENT_DURATION_OPTIONS.some(
              (minutes) =>
                minutes
                === durationMinutes,
            )

          const patient =
            mockPatientDirectory.find(
              (item) =>
                item.patient_id
                === patientId,
            )

          if (
            !patient
            || !scheduledAt
            || !validDuration
            || Number.isNaN(
              new Date(
                scheduledAt,
              ).getTime(),
            )
          ) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',

                message:
                  '환자, 예약 일시, 예상 진료시간을 확인해주세요.',

                details: {},
              },
            })

            return
          }

          const requestedStart =
            new Date(
              scheduledAt,
            ).getTime()

          const requestedEnd =
            requestedStart
            + durationMinutes
              * 60_000

          const overlapping =
            mockAppointments.some(
              (appointment) => {
                if (
                  [
                    'CANCELLED',
                    'NO_SHOW',
                  ].includes(
                    appointment.status,
                  )
                ) {
                  return false
                }

                const existingStart =
                  new Date(
                    appointment.scheduled_at,
                  ).getTime()

                const existingEnd =
                  existingStart
                  + appointment
                    .duration_minutes
                    * 60_000

                return (
                  requestedStart
                    < existingEnd
                  && requestedEnd
                    > existingStart
                )
              },
            )

          if (overlapping) {
            sendJson(response, 409, {
              error: {
                code:
                  'APPOINTMENT_CONFLICT',

                message:
                  '해당 시간에는 이미 다른 예약이 있습니다.',

                details: {},
              },
            })

            return
          }

          const created = {
            appointment_id:
              crypto.randomUUID(),

            patient_id:
              patient.patient_id,

            patient_number:
              patient
                .medical_record_number,

            patient_name:
              patient.name,

            clinician_id:
              'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',

            clinician_name:
              '김브레인',

            department_code:
              'RADIOLOGY',

            department_name:
              '영상의학과',

            hospital_id:
              hospitals[0].hospital_id,

            hospital_name:
              hospitals[0].hospital_name,

            scheduled_at:
              scheduledAt,

            duration_minutes:
              durationMinutes,

            location:
              String(
                body.location
                ?? '',
              ),

            reason:
              String(
                body.reason
                ?? '',
              ),

            status:
              'SCHEDULED',
          }

          mockAppointments = [
            ...mockAppointments,
            created,
          ]

          sendJson(response, 201, {
            data: created,
          })

          return
        }

        const appointmentDetailMatch =
          url.pathname.match(
            /^\/api\/v1\/appointments\/([^/]+)\/$/,
          )

        if (
          request.method === 'PATCH'
          && appointmentDetailMatch
        ) {
          const appointmentId =
            decodeURIComponent(
              appointmentDetailMatch[1],
            )

          const body =
            await readJson(request)

          const appointmentIndex =
            mockAppointments.findIndex(
              (appointment) =>
                appointment.appointment_id
                === appointmentId,
            )

          if (appointmentIndex < 0) {
            sendJson(response, 404, {
              error: {
                code:
                  'APPOINTMENT_NOT_FOUND',

                message:
                  '예약을 찾을 수 없습니다.',

                details: {},
              },
            })

            return
          }

          const currentAppointment =
            mockAppointments[
              appointmentIndex
            ]

          if (
            currentAppointment.status
            === 'COMPLETED'
          ) {
            sendJson(response, 409, {
              error: {
                code:
                  'APPOINTMENT_ALREADY_COMPLETED',

                message:
                  '완료된 예약은 취소할 수 없습니다.',

                details: {},
              },
            })

            return
          }

          let updatedAppointment

          if (
            body.status
            === 'CANCELLED'
          ) {
            updatedAppointment = {
              ...currentAppointment,
              status:
                'CANCELLED',
            }
          } else {
            if (
              currentAppointment.status
              === 'CANCELLED'
            ) {
              sendJson(response, 409, {
                error: {
                  code:
                    'APPOINTMENT_ALREADY_CANCELLED',

                  message:
                    '취소된 예약은 변경할 수 없습니다.',

                  details: {},
                },
              })

              return
            }

            const scheduledAt =
              String(
                body.scheduled_at
                ?? currentAppointment
                  .scheduled_at,
              )

            const durationMinutes =
              Number(
                body.duration_minutes
                ?? currentAppointment
                  .duration_minutes,
              )

            const validDuration =
              APPOINTMENT_DURATION_OPTIONS.some(
                (minutes) =>
                  minutes
                  === durationMinutes,
              )

            if (
              !scheduledAt
              || !validDuration
              || Number.isNaN(
                new Date(
                  scheduledAt,
                ).getTime(),
              )
            ) {
              sendJson(response, 400, {
                error: {
                  code:
                    'VALIDATION_ERROR',

                  message:
                    '예약 일시와 예상 진료시간을 확인해주세요.',

                  details: {},
                },
              })

              return
            }

            const requestedStart =
              new Date(
                scheduledAt,
              ).getTime()

            const requestedEnd =
              requestedStart
              + durationMinutes
                * 60_000

            const overlapping =
              mockAppointments.some(
                (appointment, index) => {
                  if (
                    index === appointmentIndex
                    || [
                      'CANCELLED',
                      'NO_SHOW',
                    ].includes(
                      appointment.status,
                    )
                  ) {
                    return false
                  }

                  const existingStart =
                    new Date(
                      appointment.scheduled_at,
                    ).getTime()

                  const existingEnd =
                    existingStart
                    + appointment
                      .duration_minutes
                      * 60_000

                  return (
                    requestedStart
                      < existingEnd
                    && requestedEnd
                      > existingStart
                  )
                },
              )

            if (overlapping) {
              sendJson(response, 409, {
                error: {
                  code:
                    'APPOINTMENT_CONFLICT',

                  message:
                    '해당 시간에는 이미 다른 예약이 있습니다.',

                  details: {},
                },
              })

              return
            }

            updatedAppointment = {
              ...currentAppointment,
              scheduled_at:
                scheduledAt,
              duration_minutes:
                durationMinutes,
              location:
                String(
                  body.location
                  ?? currentAppointment
                    .location,
                ),
              reason:
                String(
                  body.reason
                  ?? currentAppointment
                    .reason,
                ),
            }
          }

          mockAppointments = [
            ...mockAppointments.slice(
              0,
              appointmentIndex,
            ),

            updatedAppointment,

            ...mockAppointments.slice(
              appointmentIndex + 1,
            ),
          ]

          sendJson(response, 200, {
            data:
              updatedAppointment,
          })

          return
        }

        const clinicianPatientHistoryMatch =
          url.pathname.match(
            /^\/api\/v1\/patients\/([^/]+)\/medical-history\/$/,
          )

        if (
          request.method === 'GET'
          && clinicianPatientHistoryMatch
        ) {
          const patientId = decodeURIComponent(
            clinicianPatientHistoryMatch[1],
          )
          const patient = mockPatientDirectory.find(
            (item) => item.patient_id === patientId,
          )

          if (!patient) {
            sendJson(response, 404, {
              error: {
                code: 'NOT_FOUND',
                message: '환자를 찾을 수 없습니다.',
                details: {},
              },
            })
            return
          }

          const page = Math.max(
            1,
            Number(url.searchParams.get('page') ?? 1),
          )
          const pageSize = Math.min(
            100,
            Math.max(
              1,
              Number(
                url.searchParams.get('page_size')
                ?? 10,
              ),
            ),
          )
          const completedHistory = mockEncounters
            .filter(
              (encounter) =>
                encounter.patient_id === patientId
                && encounter.status === 'COMPLETED'
                && Boolean(
                  mockEncounterRecords[
                    encounter.encounter_id
                  ],
                ),
            )
            .sort((left, right) => (
              (right.completed_at ?? right.created_at)
                .localeCompare(
                  left.completed_at ?? left.created_at,
                )
            ))
          const startIndex = (page - 1) * pageSize

          sendJson(response, 200, {
            data: completedHistory
              .slice(startIndex, startIndex + pageSize)
              .map(buildMockEncounterDetail),
            meta: {
              page,
              page_size: pageSize,
              total_count: completedHistory.length,
              total_pages: Math.max(
                1,
                Math.ceil(
                  completedHistory.length / pageSize,
                ),
              ),
            },
          })
          return
        }

        const clinicianPatientDetailMatch =
          url.pathname.match(
            /^\/api\/v1\/patients\/([^/]+)\/$/,
          )

        if (
          request.method === 'GET'
          && clinicianPatientDetailMatch
        ) {
          const patientId = decodeURIComponent(
            clinicianPatientDetailMatch[1],
          )
          const patient = mockPatientDirectory.find(
            (item) => item.patient_id === patientId,
          )

          if (!patient) {
            sendJson(response, 404, {
              error: {
                code: 'NOT_FOUND',
                message: '환자를 찾을 수 없습니다.',
                details: {},
              },
            })
            return
          }

          sendJson(response, 200, {
            data: {
              ...patient,
              user_id: null,
              username: null,
              email: null,
              emergency_contact: '010-9999-0000',
              address: '서울특별시 강남구',
              merged_into_id: null,
              created_at:
                '2026-07-01T09:00:00+09:00',
              updated_at:
                '2026-08-01T09:00:00+09:00',
            },
          })
          return
        }

        if (
          request.method === 'GET'
          && url.pathname
            === '/api/v1/patients/'
        ) {
          const keyword =
            (
              url.searchParams.get(
                'search',
              )
              ?? ''
            )
              .trim()
              .toLowerCase()

          const requestedStatus =
            (
              url.searchParams.get(
                'status',
              )
              ?? ''
            )
              .trim()
              .toUpperCase()

          const page = Math.max(
            1,
            Number(
              url.searchParams.get(
                'page',
              )
              ?? 1,
            ),
          )

          const pageSize = Math.max(
            1,
            Number(
              url.searchParams.get(
                'page_size',
              )
              ?? 20,
            ),
          )

          const filteredPatients =
            mockPatientDirectory.filter(
              (patient) => {
                const matchesSearch =
                  !keyword
                  || [
                    patient.name,
                    patient
                      .medical_record_number,
                    patient.phone,
                  ]
                    .join(' ')
                    .toLowerCase()
                    .includes(keyword)

                const matchesStatus =
                  !requestedStatus
                  || patient.status
                    === requestedStatus

                return (
                  matchesSearch
                  && matchesStatus
                )
              },
            )

          const startIndex =
            (page - 1) * pageSize

          const results =
            filteredPatients.slice(
              startIndex,
              startIndex + pageSize,
            )

          sendJson(response, 200, {
            data:
              results,

            meta: {
              page,

              page_size:
                pageSize,

              total_count:
                filteredPatients.length,

              total_pages:
                Math.max(
                  1,
                  Math.ceil(
                    filteredPatients.length
                    / pageSize,
                  ),
                ),
            },
          })

          return
        }
        if (
          request.method === 'GET'
          && url.pathname === '/api/v1/clinicians/departments'
        ) {
          sendJson(response, 200, {
            data: departments,
            meta: {
              page: 1,
              page_size: 100,
              total_count: departments.length,
              total_pages: 1,
            },
          })
          return
        }

        if (
          request.method === 'GET'
          && url.pathname
            === '/api/v1/reports/clinician-summary/'
        ) {
          const startDate =
            url.searchParams.get('start_date')
            ?? ''
          const endDate =
            url.searchParams.get('end_date')
            ?? ''
          const datePattern = /^\d{4}-\d{2}-\d{2}$/
          const startTime = new Date(
            `${startDate}T00:00:00Z`,
          ).getTime()
          const endTime = new Date(
            `${endDate}T00:00:00Z`,
          ).getTime()

          if (
            !datePattern.test(startDate)
            || !datePattern.test(endDate)
            || Number.isNaN(startTime)
            || Number.isNaN(endTime)
            || endTime < startTime
            || endTime - startTime
              > 366 * 24 * 60 * 60 * 1000
          ) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',
                message:
                  '조회 기간을 확인해주세요.',
                details: {},
              },
            })

            return
          }

          const inPeriod = (value: string) => {
            const date = value.slice(0, 10)

            return date >= startDate
              && date <= endDate
          }
          const appointments =
            mockAppointments.filter(
              (appointment) =>
                inPeriod(
                  appointment.scheduled_at,
                ),
            )
          const prescriptions =
            mockPrescriptions.filter(
              (prescription) =>
                inPeriod(
                  prescription.prescribed_at,
                ),
            )
          const completedAppointments =
            appointments.filter(
              (appointment) =>
                appointment.status
                  === 'COMPLETED',
            )
          const patientCount = new Set(
            completedAppointments.map(
              (appointment) =>
                appointment.patient_id,
            ),
          ).size
          const dailyEncounters = []

          for (
            let current = startTime;
            current <= endTime;
            current += 24 * 60 * 60 * 1000
          ) {
            const date = new Date(current)
              .toISOString()
              .slice(0, 10)

            dailyEncounters.push({
              date,
              count:
                completedAppointments.filter(
                  (appointment) =>
                    appointment.scheduled_at
                      .startsWith(date),
                ).length,
            })
          }

          const appointmentStatusLabels = {
            SCHEDULED: '예약',
            CONFIRMED: '확정',
            CHECKED_IN: '접수',
            COMPLETED: '완료',
            CANCELLED: '취소',
            NO_SHOW: '노쇼',
          }
          const appointmentStatuses =
            Object.entries(
              appointmentStatusLabels,
            ).map(([status, label]) => ({
              status,
              label,
              count: appointments.filter(
                (appointment) =>
                  appointment.status === status,
              ).length,
            }))
          const prescriptionStatuses =
            Object.entries(
              prescriptionStatusLabels,
            ).map(([status, label]) => ({
              status,
              label,
              count: prescriptions.filter(
                (prescription) =>
                  prescription.status === status,
              ).length,
            }))
          const medicineCounts = new Map<
            string,
            number
          >()

          prescriptions.forEach(
            (prescription) => {
              prescription.items.forEach((item) => {
                medicineCounts.set(
                  item.medicine_name,
                  (
                    medicineCounts.get(
                      item.medicine_name,
                    ) ?? 0
                  ) + 1,
                )
              })
            },
          )

          const topMedicines = [
            ...medicineCounts.entries(),
          ]
            .map(([medicineName, count]) => ({
              medicine_name: medicineName,
              count,
            }))
            .sort(
              (left, right) =>
                right.count - left.count
                || left.medicine_name
                  .localeCompare(
                    right.medicine_name,
                  ),
            )
            .slice(0, 5)
          const ctAnalysisCount =
            mockCtAnalyses.filter(
              (analysis) =>
                inPeriod(analysis.created_at),
            ).length

          sendJson(response, 200, {
            data: {
              clinician: {
                clinician_id:
                  'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
                name: '김브레인',
              },
              period: {
                start_date: startDate,
                end_date: endDate,
              },
              summary: {
                patient_count: patientCount,
                appointment_completion_rate:
                  appointments.length
                    ? Number((
                      completedAppointments.length
                      / appointments.length
                      * 100
                    ).toFixed(1))
                    : 0,
                prescription_count:
                  prescriptions.length,
                ct_analysis_count:
                  ctAnalysisCount,
              },
              daily_encounters:
                dailyEncounters,
              appointment_statuses:
                appointmentStatuses,
              prescription_statuses:
                prescriptionStatuses,
              top_medicines:
                topMedicines,
            },
          })

          return
        }

        if (
          request.method === 'GET'
          && url.pathname
            === '/api/v1/prescriptions/contexts/'
        ) {
          const search = (
            url.searchParams.get('search')
            ?? ''
          ).trim().toLowerCase()

          const contexts = search
            ? mockPrescriptionContexts.filter(
              (context) =>
                context.patient_name
                  .toLowerCase()
                  .includes(search)
                || context.patient_number
                  .toLowerCase()
                  .includes(search),
            )
            : mockPrescriptionContexts

          sendJson(response, 200, {
            data: contexts,
          })

          return
        }

        if (
          request.method === 'GET'
          && url.pathname
            === '/api/v1/prescriptions/'
        ) {
          const search = (
            url.searchParams.get('search')
            ?? ''
          ).trim().toLowerCase()
          const requestedStatus = (
            url.searchParams.get('status')
            ?? ''
          ).trim().toUpperCase()
          const page = Math.max(
            1,
            Number(
              url.searchParams.get('page')
              ?? 1,
            ),
          )
          const pageSize = Math.max(
            1,
            Number(
              url.searchParams.get('page_size')
              ?? 20,
            ),
          )

          const filtered =
            mockPrescriptions.filter(
              (prescription) => {
                const statusMatches =
                  !requestedStatus
                  || prescription.status
                    === requestedStatus
                const searchMatches =
                  !search
                  || prescription.patient_name
                    .toLowerCase()
                    .includes(search)
                  || prescription.patient_number
                    .toLowerCase()
                    .includes(search)
                  || prescription.items.some(
                    (item) =>
                      item.medicine_name
                        .toLowerCase()
                        .includes(search),
                  )

                return statusMatches
                  && searchMatches
              },
            )

          const startIndex =
            (page - 1) * pageSize

          sendJson(response, 200, {
            data: filtered.slice(
              startIndex,
              startIndex + pageSize,
            ),
            meta: {
              page,
              page_size: pageSize,
              total_count: filtered.length,
              total_pages: Math.max(
                1,
                Math.ceil(
                  filtered.length / pageSize,
                ),
              ),
            },
          })

          return
        }

        if (
          request.method === 'POST'
          && url.pathname
            === '/api/v1/prescriptions/'
        ) {
          const body = await readJson(request)
          const clinicalRecordId = String(
            body.clinical_record_id ?? '',
          )
          const requestedStatus = String(
            body.status ?? 'ACTIVE',
          ).toUpperCase()
          const context =
            mockPrescriptionContexts.find(
              (item) =>
                item.clinical_record_id
                  === clinicalRecordId,
            )
          const itemValues = Array.isArray(
            body.items,
          )
            ? body.items
            : []

          if (
            !context
            || ![
              'DRAFT',
              'ACTIVE',
            ].includes(requestedStatus)
            || itemValues.length === 0
          ) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',
                message:
                  '진료기록과 처방 약품을 확인해주세요.',
                details: {},
              },
            })

            return
          }

          const invalidItem =
            itemValues.some((value) => {
              const item = value as
                Record<string, unknown>

              return (
                !String(
                  item.medicine_name ?? '',
                ).trim()
                || Number(item.dosage ?? 0)
                  <= 0
                || !String(
                  item.dose_unit ?? '',
                ).trim()
                || !String(
                  item.frequency ?? '',
                ).trim()
                || !String(
                  item.start_date ?? '',
                )
              )
            })

          if (invalidItem) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',
                message:
                  '처방 약품 입력값을 확인해주세요.',
                details: {},
              },
            })

            return
          }

          const now = new Date().toISOString()
          const statusKey =
            requestedStatus as
              keyof typeof prescriptionStatusLabels

          const created = {
            prescription_id:
              crypto.randomUUID(),
            encounter_id:
              context.encounter_id,
            encounter_number:
              context.encounter_number,
            clinical_record_id:
              context.clinical_record_id,
            patient_id:
              context.patient_id,
            patient_number:
              context.patient_number,
            patient_name:
              context.patient_name,
            clinician_name: '김브레인',
            status: requestedStatus,
            status_label:
              prescriptionStatusLabels[
                statusKey
              ],
            notes: String(
              body.notes ?? '',
            ),
            prescribed_at: now,
            discontinued_at:
              null as string | null,
            items: itemValues.map(
              (value) => {
                const item = value as
                  Record<string, unknown>

                return {
                  prescription_item_id:
                    crypto.randomUUID(),
                  medicine_name:
                    String(
                      item.medicine_name
                      ?? '',
                    ),
                  dosage:
                    Number(
                      item.dosage ?? 0,
                    ).toFixed(4),
                  dose_unit:
                    String(
                      item.dose_unit ?? '',
                    ),
                  frequency:
                    String(
                      item.frequency ?? '',
                    ),
                  route:
                    String(
                      item.route ?? '',
                    ),
                  instructions:
                    String(
                      item.instructions ?? '',
                    ),
                  start_date:
                    String(
                      item.start_date ?? '',
                    ),
                  end_date:
                    item.end_date
                      ? String(item.end_date)
                      : null,
                }
              },
            ),
            created_at: now,
            updated_at: now,
          }

          mockPrescriptions = [
            created,
            ...mockPrescriptions,
          ]

          sendJson(response, 201, {
            data: created,
          })

          return
        }

        const prescriptionStatusMatch =
          url.pathname.match(
            /^\/api\/v1\/prescriptions\/([^/]+)\/status\/$/,
          )

        if (
          request.method === 'PATCH'
          && prescriptionStatusMatch
        ) {
          const prescriptionId =
            decodeURIComponent(
              prescriptionStatusMatch[1],
            )
          const body = await readJson(request)
          const nextStatus = String(
            body.status ?? '',
          ).toUpperCase()
          const index =
            mockPrescriptions.findIndex(
              (prescription) =>
                prescription.prescription_id
                  === prescriptionId,
            )

          if (index < 0) {
            sendJson(response, 404, {
              error: {
                code: 'NOT_FOUND',
                message:
                  '처방전을 찾을 수 없습니다.',
                details: {},
              },
            })
            return
          }

          const transitions:
          Record<string, string[]> = {
            DRAFT: [
              'ACTIVE',
              'CANCELLED',
            ],
            ACTIVE: [
              'COMPLETED',
              'DISCONTINUED',
              'CANCELLED',
            ],
            COMPLETED: [],
            DISCONTINUED: [],
            CANCELLED: [],
          }
          const current =
            mockPrescriptions[index]

          if (
            !transitions[current.status]
              ?.includes(nextStatus)
          ) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',
                message:
                  '현재 상태에서는 요청한 상태로 변경할 수 없습니다.',
                details: {},
              },
            })
            return
          }

          const now = new Date().toISOString()
          const statusKey =
            nextStatus as
              keyof typeof prescriptionStatusLabels
          const updated = {
            ...current,
            status: nextStatus,
            status_label:
              prescriptionStatusLabels[
                statusKey
              ],
            discontinued_at:
              nextStatus === 'DISCONTINUED'
                ? now
                : null,
            updated_at: now,
          }

          mockPrescriptions = [
            ...mockPrescriptions.slice(0, index),
            updated,
            ...mockPrescriptions.slice(index + 1),
          ]

          sendJson(response, 200, {
            data: updated,
          })

          return
        }

        const prescriptionDetailMatch =
          url.pathname.match(
            /^\/api\/v1\/prescriptions\/([^/]+)\/$/,
          )

        if (
          request.method === 'GET'
          && prescriptionDetailMatch
        ) {
          const prescription =
            mockPrescriptions.find(
              (item) =>
                item.prescription_id
                  === decodeURIComponent(
                    prescriptionDetailMatch[1],
                  ),
            )

          if (!prescription) {
            sendJson(response, 404, {
              error: {
                code: 'NOT_FOUND',
                message:
                  '처방전을 찾을 수 없습니다.',
                details: {},
              },
            })
            return
          }

          sendJson(response, 200, {
            data: prescription,
          })

          return
        }

        if (
          request.method === 'GET'
          && url.pathname
            === '/api/v1/auth/me/'
        ) {
          sendJson(response, 200, {
            data:
              getMockCurrentAccount(),
          })

          return
        }

        if (
          request.method === 'PATCH'
          && url.pathname
            === '/api/v1/auth/me/'
        ) {
          const body = await readJson(request)
          const email = String(
            body.email ?? '',
          ).trim()

          if (
            !email
            || !email.includes('@')
          ) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',
                message:
                  '올바른 이메일을 입력해주세요.',
                details: {},
              },
            })

            return
          }

          mockAccountEmail = email

          sendJson(response, 200, {
            data:
              getMockCurrentAccount(),
          })

          return
        }

        if (
          request.method === 'POST'
          && url.pathname
            === '/api/v1/auth/password/change/'
        ) {
          const body = await readJson(request)
          const currentPassword = String(
            body.current_password ?? '',
          )
          const newPassword = String(
            body.new_password ?? '',
          )
          const newPasswordConfirm = String(
            body.new_password_confirm ?? '',
          )

          if (
            currentPassword
              !== mockAccountPassword
            || newPassword.length < 8
            || newPassword
              !== newPasswordConfirm
          ) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',
                message:
                  '비밀번호 입력값을 확인해주세요.',
                details: {},
              },
            })

            return
          }

          mockAccountPassword =
            newPassword

          sendJson(response, 200, {
            data: {
              changed: true,
            },
          })

          return
        }

        if (
          request.method === 'POST'
          && url.pathname === '/api/v1/auth/clinician/login/'
        ) {
          const body = await readJson(request)
          const validLogin =
            body.hospital_id === hospitals[0].hospital_id
            && body.department_code === 'RADIOLOGY'
            && body.license_number === '123456'
            && body.password
              === mockAccountPassword

          if (!validLogin) {
            sendJson(response, 400, {
              error: {
                code: 'VALIDATION_ERROR',
                message: '병원, 진료과, 면허번호 또는 비밀번호가 올바르지 않습니다.',
                details: {},
              },
            })
            return
          }

          sendJson(response, 200, {
            data: {
              access: 'mock-access-token',
              refresh: 'mock-refresh-token',
              ...getMockCurrentAccount(),
            },
          })
          return
        }

        if (
          request.method === 'POST'
          && url.pathname === '/api/v1/auth/token/refresh/'
        ) {
          sendJson(response, 200, {
            data: {
              access: 'mock-access-token-refreshed',
              refresh: 'mock-refresh-token-refreshed',
            },
          })
          return
        }

        if (
          request.method === 'GET'
          && url.pathname
            === '/api/v1/clinicians/clinicians/me/dashboard'
        ) {
          const selectedDate =
            url.searchParams.get('date')

          const filteredSchedules =
            selectedDate
              ? mockSchedules.filter(
                (schedule) =>
                  schedule.start_at.startsWith(
                    selectedDate,
                  ),
              )
              : mockSchedules


          sendJson(response, 200, {
            data: {
              clinician: {
                clinician_id:
                  'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
              
                user_id:
                  'dddddddd-dddd-dddd-dddd-dddddddddddd',
              
                name: '김브레인',
              
                license_number: '123456',
              
                approval_status: 'APPROVED',
              
                created_at:
                  '2026-08-01T09:00:00+09:00',
              
                updated_at:
                  '2026-08-01T09:00:00+09:00',
              
                hospital: {
                  hospital_id:
                    '11111111-1111-1111-1111-111111111111',
                
                  hospital_code: 'BRN001',
                
                  hospital_name:
                    '브레인온 서울병원',
                
                  address:
                    '서울특별시 강남구 테헤란로 100',
                
                  phone:
                    '02-1234-5678',
                },
              
                department: {
                  department_id:
                    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                
                  code: 'RADIOLOGY',
                
                  name: '영상의학과',
                
                  is_active: true,
                },
              },
                summary: {
                  appointments: {
                    total:
                      mockPatients.length,

                    confirmed:
                      mockPatients.filter(
                        (item) =>
                          item.status === 'confirmed',
                      ).length,

                    waiting:
                      mockPatients.filter(
                        (item) =>
                          item.status === 'waiting',
                      ).length,
                  },

                  consultations: {
                    total:
                      mockConsultations.length,

                    waiting:
                      mockConsultations.filter(
                        (item) =>
                          item.status === 'requested'
                          || item.status === 'waiting',
                      ).length,

                    answered:
                      mockConsultations.filter(
                        (item) =>
                          item.status === 'answered'
                          || item.status === 'completed',
                      ).length,
                  },

                  tests: {
                    total:
                      mockTests.length,

                    processing:
                      mockTests.filter(
                        (item) =>
                          item.status === 'processing',
                      ).length,

                    result_waiting:
                      mockTests.filter(
                        (item) =>
                          item.status === 'result_waiting',
                      ).length,
                  },

                  ct_analyses: {
                    total:
                      mockCtAnalyses.length,

                    processing:
                      mockCtAnalyses.filter(
                        (item) =>
                          item.status === 'processing',
                      ).length,

                    completed:
                      mockCtAnalyses.filter(
                        (item) =>
                          item.status === 'completed',
                      ).length,
                  },
                },

                patients:
                  mockPatients,

                consultations:
                  mockConsultations,

                activities:
                  mockActivities,

                schedules:
                  filteredSchedules,
              },
          })
        
          return
        }

        if (request.method === 'GET' && url.pathname === '/history/') {
          sendJson(response, 200, {
            count: 1,
            results: [
              {
                ct_id: 1,
                display_id: 'CT-2026-0001',
                patient_id: 'P-2026-001',
                patient_name: '홍길동',
                gender: 'M',
                age: 67,
                status: 'completed',
                progress: 100,
                created_at: '2026-08-02T08:10:00+09:00',
              },
            ],
          })
          return
        }

        if (request.method === 'POST' && url.pathname === '/predict/') {
          sendJson(response, 200, {
            ct_id: 2,
            display_id: 'CT-2026-0002',
            job_id: 'mock-job-2',
            status: 'processing',
            progress: 10,
            message: 'Mock CT 분석을 시작했습니다.',
          })
          return
        }

        if (request.method === 'GET' && url.pathname.startsWith('/status/')) {
          sendJson(response, 200, {
            ct_id: 2,
            display_id: 'CT-2026-0002',
            status: 'completed',
            progress: 100,
            elapsed_time: 2,
            error_code: '',
            error_message: '',
          })
          return
        }

        next()
      })
    },
  }
}

export default defineConfig(({ mode }) => {
  const plugins: PluginOption[] = [react()]

  if (mode === 'mock') {
    plugins.push(mockApiPlugin())
  }

  return {
    plugins,

    envDir: '..',

    server: {
      port: 5173,
    },
  }
})
