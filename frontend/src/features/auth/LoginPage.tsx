import {
  type FormEvent,
  type KeyboardEvent,
  useEffect,
  useState,
} from 'react'
import {
  Navigate,
  useNavigate,
} from 'react-router-dom'

import {
  type Department,
  getDepartments,
  loginClinician,
  searchHospitals,
  type Hospital,
} from '../../core/api/authApi'
import { ApiError } from '../../core/api/apiError'
import { useAuthStore } from '../../core/auth/authStore'

import './login.css'

export function LoginPage() {
  const navigate = useNavigate()

  const accessToken = useAuthStore(
    (state) => state.accessToken,
  )

  const [
    hospitalSearch,
    setHospitalSearch,
  ] = useState('')

  const [
    hospitals,
    setHospitals,
  ] = useState<Hospital[]>([])

  const [
    selectedHospitalId,
    setSelectedHospitalId,
  ] = useState('')

  const [
    departments,
    setDepartments,
  ] = useState<Department[]>([])

  const [
    selectedDepartmentCode,
    setSelectedDepartmentCode,
  ] = useState('')

  const [
    licenseNumber,
    setLicenseNumber,
  ] = useState('')

  const [
    password,
    setPassword,
  ] = useState('')

  const [
    hospitalLoading,
    setHospitalLoading,
  ] = useState(false)

  const [
    departmentLoading,
    setDepartmentLoading,
  ] = useState(true)

  const [
    loginLoading,
    setLoginLoading,
  ] = useState(false)

  const [
    errorMessage,
    setErrorMessage,
  ] = useState('')

  useEffect(() => {
    let mounted = true

    async function loadInitialData() {
      setDepartmentLoading(true)
      setHospitalLoading(true)

      try {
        const [
          departmentData,
          hospitalData,
        ] = await Promise.all([
          getDepartments(),
          searchHospitals(''),
        ])

        if (!mounted) {
          return
        }

        setDepartments(departmentData)
        setHospitals(hospitalData)
      } catch (error) {
        if (!mounted) {
          return
        }

        setErrorMessage(
          error instanceof ApiError
            ? error.message
            : '로그인 정보를 불러오지 못했습니다.',
        )
      } finally {
        if (mounted) {
          setDepartmentLoading(false)
          setHospitalLoading(false)
        }
      }
    }

    void loadInitialData()

    return () => {
      mounted = false
    }
  }, [])

  if (accessToken) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    )
  }

  async function handleHospitalSearch() {
    setHospitalLoading(true)
    setErrorMessage('')

    try {
      const data =
        await searchHospitals(
          hospitalSearch.trim(),
        )

      setHospitals(data)

      if (
        selectedHospitalId
        && !data.some(
          (hospital) =>
            hospital.hospital_id
            === selectedHospitalId,
        )
      ) {
        setSelectedHospitalId('')
      }
    } catch (error) {
      setErrorMessage(
        error instanceof ApiError
          ? error.message
          : '병원 목록을 불러오지 못했습니다.',
      )
    } finally {
      setHospitalLoading(false)
    }
  }

  function handleLoginEnter(
    event: KeyboardEvent<HTMLInputElement>,
  ) {
    if (
      event.key !== 'Enter'
      || event.nativeEvent.isComposing
      || loginLoading
      || departmentLoading
    ) {
      return
    }

    event.preventDefault()
    event.currentTarget.form?.requestSubmit()
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()
    setErrorMessage('')

    if (!selectedHospitalId) {
      setErrorMessage(
        '병원을 선택해 주세요.',
      )
      return
    }

    if (!selectedDepartmentCode) {
      setErrorMessage(
        '진료과를 선택해 주세요.',
      )
      return
    }

    if (!/^\d{6}$/.test(licenseNumber)) {
      setErrorMessage(
        '면허번호는 숫자 6자리입니다.',
      )
      return
    }

    if (!password) {
      setErrorMessage(
        '비밀번호를 입력해 주세요.',
      )
      return
    }

    setLoginLoading(true)

    try {
      await loginClinician({
        hospital_id:
          selectedHospitalId,
        department_code:
          selectedDepartmentCode,
        license_number:
          licenseNumber,
        password,
      })

      navigate(
        '/dashboard',
        { replace: true },
      )
    } catch (error) {
      setErrorMessage(
        error instanceof ApiError
          ? error.message
          : '로그인에 실패했습니다.',
      )
    } finally {
      setLoginLoading(false)
    }
  }

  return (
    <main className="login-page">
      <form
        className="login-card"
        onSubmit={handleSubmit}
      >
        <header className="login-header">
          <div className="login-logo">
            B
          </div>

          <h1>BrainOn</h1>
          <p>의료진 로그인</p>
        </header>

        <section className="hospital-search">
          <label className="login-field">
            <span>병원 검색</span>

            <div className="search-row">
              <input
                type="search"
                enterKeyHint="search"
                value={hospitalSearch}
                placeholder="병원 이름 또는 주소"
                disabled={
                  hospitalLoading
                  || loginLoading
                }
                onChange={(event) =>
                  setHospitalSearch(
                    event.target.value,
                  )
                }
                onKeyDown={(event) => {
                  if (
                    event.key !== 'Enter'
                    || event.nativeEvent.isComposing
                  ) {
                    return
                  }

                  event.preventDefault()
                  void handleHospitalSearch()
                }}
              />

              <button
                type="button"
                disabled={
                  hospitalLoading
                  || loginLoading
                }
                onClick={() => {
                  void handleHospitalSearch()
                }}
              >
                {hospitalLoading
                  ? '검색 중'
                  : '검색'}
              </button>
            </div>
          </label>
        </section>

        <label className="login-field">
          <span>병원</span>

          <select
            value={selectedHospitalId}
            disabled={
              hospitalLoading
              || loginLoading
            }
            onChange={(event) =>
              setSelectedHospitalId(
                event.target.value,
              )
            }
          >
            <option value="">
              병원을 선택해 주세요
            </option>

            {hospitals.map((hospital) => (
              <option
                key={hospital.hospital_id}
                value={hospital.hospital_id}
              >
                {hospital.hospital_name}
                {hospital.address
                  ? ` · ${hospital.address}`
                  : ''}
              </option>
            ))}
          </select>
        </label>

        <label className="login-field">
          <span>진료과</span>

          <select
            value={
              selectedDepartmentCode
            }
            disabled={
              departmentLoading
              || loginLoading
            }
            onChange={(event) =>
              setSelectedDepartmentCode(
                event.target.value,
              )
            }
          >
            <option value="">
              {departmentLoading
                ? '진료과를 불러오는 중...'
                : '진료과를 선택해 주세요'}
            </option>

            {departments.map(
              (department) => (
                <option
                  key={
                    department.department_id
                  }
                  value={department.code}
                >
                  {department.name}
                </option>
              ),
            )}
          </select>
        </label>

        <label className="login-field">
          <span>면허번호</span>

          <input
            type="text"
            inputMode="numeric"
            autoComplete="username"
            maxLength={6}
            value={licenseNumber}
            placeholder="숫자 6자리"
            disabled={loginLoading}
            onChange={(event) => {
              const numbersOnly =
                event.target.value.replace(
                  /\D/g,
                  '',
                )

              setLicenseNumber(
                numbersOnly,
              )
            }}
            onKeyDown={handleLoginEnter}
          />
        </label>

        <label className="login-field">
          <span>비밀번호</span>

          <input
            type="password"
            autoComplete="current-password"
            value={password}
            placeholder="비밀번호"
            disabled={loginLoading}
            onChange={(event) =>
              setPassword(
                event.target.value,
              )
            }
            onKeyDown={handleLoginEnter}
          />
        </label>

        {errorMessage && (
          <p
            className="login-error"
            role="alert"
          >
            {errorMessage}
          </p>
        )}

        <button
          className="login-submit"
          type="submit"
          disabled={
            loginLoading
            || departmentLoading
          }
        >
          {loginLoading
            ? '로그인 중...'
            : '로그인'}
        </button>
      </form>
    </main>
  )
}
