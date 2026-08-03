import {
  apiRequest,
} from '../../core/api/apiClient'

import type {
  Appointment,
  AppointmentCreateInput,
  AppointmentListResponse,
  AppointmentStatus,
} from './appointment.types'

interface GetAppointmentsParams {
  dateFrom: string
  dateTo: string
  status?: AppointmentStatus | ''
  signal?: AbortSignal
}

export function getAppointments({
  dateFrom,
  dateTo,
  status = '',
  signal,
}: GetAppointmentsParams):
Promise<AppointmentListResponse> {
  const searchParams =
    new URLSearchParams({
      date_from: dateFrom,
      date_to: dateTo,
    })

  if (status) {
    searchParams.set(
      'status',
      status,
    )
  }

  return apiRequest<AppointmentListResponse>(
    `/api/v1/appointments/?${
      searchParams.toString()
    }`,
    {
      signal,
    },
  )
}

interface AppointmentCreateResponse {
  data: Appointment
}

export async function createAppointment(
  input: AppointmentCreateInput,
): Promise<Appointment> {
  const response =
    await apiRequest<
      AppointmentCreateResponse
    >(
      '/api/v1/appointments/',
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify(input),
      },
    )

  return response.data
}

interface AppointmentCancelResponse {
  data: Appointment
}

export async function cancelAppointment(
  appointmentId: string,
): Promise<Appointment> {
  const response =
    await apiRequest<
      AppointmentCancelResponse
    >(
      `/api/v1/appointments/${
        encodeURIComponent(
          appointmentId,
        )
      }/`,
      {
        method: 'PATCH',

        headers: {
          'Content-Type':
            'application/json',
        },

        body: JSON.stringify({
          status: 'CANCELLED',
        }),
      },
    )

  return response.data
}