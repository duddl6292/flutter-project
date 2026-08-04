import {
  apiRequest,
} from '../../core/api/apiClient'

import type {
  ReportDetailResponse,
  ReportDetailType,
  ClinicianSummaryReport,
} from './report.types'

interface ReportResponse {
  data: ClinicianSummaryReport
}

export async function getClinicianSummaryReport(
  startDate: string,
  endDate: string,
  signal?: AbortSignal,
): Promise<ClinicianSummaryReport> {
  const searchParams = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  })
  const response =
    await apiRequest<ReportResponse>(
      `/api/v1/reports/clinician-summary/?${
        searchParams.toString()
      }`,
      { signal },
    )

  return response.data
}

export async function getClinicianReportDetails({
  type,
  startDate,
  endDate,
  status = '',
  medicine = '',
  page = 1,
  pageSize = 20,
  signal,
}: {
  type: ReportDetailType
  startDate: string
  endDate: string
  status?: string
  medicine?: string
  page?: number
  pageSize?: number
  signal?: AbortSignal
}): Promise<ReportDetailResponse> {
  const searchParams = new URLSearchParams({
    type,
    start_date: startDate,
    end_date: endDate,
    page: String(page),
    page_size: String(pageSize),
  })

  if (status) searchParams.set('status', status)
  if (medicine) {
    searchParams.set('medicine', medicine)
  }

  return apiRequest<ReportDetailResponse>(
    `/api/v1/reports/clinician-details/?${
      searchParams.toString()
    }`,
    { signal },
  )
}
