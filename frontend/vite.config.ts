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
    { id: 1, status: 'processing' },
    { id: 2, status: 'completed' },
  ]

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

          if (
            body.status
            !== 'CANCELLED'
          ) {
            sendJson(response, 400, {
              error: {
                code:
                  'VALIDATION_ERROR',

                message:
                  '현재 Mock API에서는 예약 취소만 가능합니다.',

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

          const updatedAppointment = {
            ...currentAppointment,

            status:
              'CANCELLED',
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
          request.method === 'POST'
          && url.pathname === '/api/v1/auth/clinician/login/'
        ) {
          const body = await readJson(request)
          const validLogin =
            body.hospital_id === hospitals[0].hospital_id
            && body.department_code === 'RADIOLOGY'
            && body.license_number === '123456'
            && body.password === 'brainon123!'

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
              user: {
                id: 'dddddddd-dddd-dddd-dddd-dddddddddddd',
                username: '123456',
                email: 'doctor@brainon.test',
                role: 'CLINICIAN',
              },
              clinician: {
                id: 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
                name: '김브레인',
                license_number: '123456',
                approval_status: 'APPROVED',
                hospital_id: hospitals[0].hospital_id,
                hospital_name: hospitals[0].hospital_name,
                department_id: departments[0].department_id,
                department_code: departments[0].code,
                department_name: departments[0].name,
              },
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
    server: {
      port: 5173,
    },
  }
})
