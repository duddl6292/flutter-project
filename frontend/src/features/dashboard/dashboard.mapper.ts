import type {
  BackendDashboardResponse,
} from './dashboard.backend-types'

import type {
  DashboardResponse,
} from './dashboard.types'

export function mapDashboardResponse(
  response: BackendDashboardResponse,
  selectedDate: string,
): DashboardResponse {
  const clinician =
    response.data.clinician

  return {
    date: selectedDate,

    doctor: {
      name:
        clinician.name,

      department:
        clinician.department.name,

      title:
        '의료진',
    },

    summary:
      response.data.summary ?? {
        appointments: {
          total: 0,
          confirmed: 0,
          waiting: 0,
        },

        consultations: {
          total: 0,
          waiting: 0,
          answered: 0,
        },

        tests: {
          total: 0,
          processing: 0,
          result_waiting: 0,
        },

        ct_analyses: {
          total: 0,
          processing: 0,
          completed: 0,
        },
      },

    patients:
      response.data.patients ?? [],

    activities:
      response.data.activities ?? [],

    schedules:
      response.data.schedules ?? [],

    consultations:
      response.data.consultations ?? [],
  }
}