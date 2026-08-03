import type {
  AuthUser,
  ClinicianProfile,
} from '../auth/authStore'
import { useAuthStore } from '../auth/authStore'
import { apiRequest } from './apiClient'

interface ApiEnvelope<T> {
  data: T
}

interface PaginationMeta {
  page: number
  page_size: number
  total_count: number
  total_pages: number
}

export interface Hospital {
  hospital_id: string
  hospital_code: string
  hospital_name: string
  address: string
  phone: string
}

interface HospitalListResponse {
  data: Hospital[]
  meta: PaginationMeta
}

interface ClinicianLoginInput {
  hospital_id: string
  department_code: string
  license_number: string
  password: string
}

interface ClinicianLoginData {
  access: string
  refresh: string
  user: AuthUser
  clinician: ClinicianProfile
}

export async function searchHospitals(
  search: string,
): Promise<Hospital[]> {
  const response =
    await apiRequest<HospitalListResponse>(
      `/api/v1/hospitals/?search=${encodeURIComponent(search)}`,
      {
        retryAfterRefresh: false,
      },
    )

  return response.data
}

export async function loginClinician(
  input: ClinicianLoginInput,
): Promise<ClinicianLoginData> {
  const response =
    await apiRequest<
      ApiEnvelope<ClinicianLoginData>
    >(
      '/api/v1/auth/clinician/login/',
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify(input),
        retryAfterRefresh: false,
      },
    )

  useAuthStore
    .getState()
    .setSession({
      accessToken:
        response.data.access,
      refreshToken:
        response.data.refresh,
      user:
        response.data.user,
      clinician:
        response.data.clinician,
    })

  return response.data
}

export function logout(): void {
  useAuthStore
    .getState()
    .clearSession()
}

export interface Department {
  department_id: string
  code: string
  name: string
  is_active: boolean
}

interface DepartmentListResponse {
  data: Department[]
  meta: PaginationMeta
}

export async function getDepartments():
Promise<Department[]> {
  const response =
    await apiRequest<DepartmentListResponse>(
      '/api/v1/clinicians/departments?page_size=100',
      {
        retryAfterRefresh: false,
      },
    )

  return response.data
}