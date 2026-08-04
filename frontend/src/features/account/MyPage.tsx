import {
  Building2,
  Hospital,
  IdCard,
  Mail,
  Settings,
  Stethoscope,
} from 'lucide-react'

import {
  useEffect,
  useState,
} from 'react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  useAuthStore,
} from '../../core/auth/authStore'

import {
  getCurrentAccount,
} from './account.api'

import type {
  CurrentAccount,
} from './account.api'

import {
  AccountPageLayout,
} from './AccountPageLayout'

import './account.css'

export function MyPage() {
  const navigate = useNavigate()
  const storedUser = useAuthStore(
    (state) => state.user,
  )
  const storedClinician = useAuthStore(
    (state) => state.clinician,
  )
  const updateUser = useAuthStore(
    (state) => state.updateUser,
  )

  const [account, setAccount] =
    useState<CurrentAccount>({
      user: storedUser!,
      clinician: storedClinician,
    })
  const [loading, setLoading] =
    useState(true)
  const [error, setError] =
    useState('')

  useEffect(() => {
    let active = true

    const loadAccount = async () => {
      try {
        const nextAccount =
          await getCurrentAccount()

        if (!active) return

        setAccount(nextAccount)
        updateUser(nextAccount.user)
      } catch (requestError) {
        if (!active) return

        setError(
          requestError instanceof Error
            ? requestError.message
            : '내 정보를 불러오지 못했습니다.',
        )
      } finally {
        if (active) setLoading(false)
      }
    }

    void loadAccount()

    return () => {
      active = false
    }
  }, [updateUser])

  const clinician =
    account.clinician
    ?? storedClinician
  const name =
    clinician?.name
    ?? account.user?.username
    ?? '의료진'
  const avatarText =
    name.trim().charAt(0) || '의'

  return (
    <AccountPageLayout>
      <main className="account-page">
        <header className="account-page-heading">
          <div>
            <h1>마이페이지</h1>
            <p>
              병원에서 등록한 의료진 정보를 확인합니다.
            </p>
          </div>

          <button
            type="button"
            className="account-primary-button"
            onClick={() =>
              navigate('/settings/account')
            }
          >
            <Settings size={17} />
            계정 설정
          </button>
        </header>

        {loading && (
          <p className="account-message">
            내 정보를 불러오는 중입니다.
          </p>
        )}

        {error && (
          <p
            role="alert"
            className="account-error"
          >
            {error}
          </p>
        )}

        <section className="profile-overview-card">
          <div className="profile-large-avatar">
            {avatarText}
          </div>

          <div>
            <h2>{name}</h2>
            <p>
              {clinician?.department_name ?? '-'}
              {' · '}
              의료진
            </p>
          </div>
        </section>

        <section className="account-card">
          <header>
            <div>
              <h2>기본 정보</h2>
              <p>
                의료진 소속 정보는 병원 관리자에게 문의해 변경합니다.
              </p>
            </div>
          </header>

          <dl className="profile-information-grid">
            <div>
              <dt>
                <IdCard size={17} />
                이름
              </dt>
              <dd>{name}</dd>
            </div>

            <div>
              <dt>
                <Mail size={17} />
                이메일
              </dt>
              <dd>
                {account.user?.email || '-'}
              </dd>
            </div>

            <div>
              <dt>
                <Stethoscope size={17} />
                면허번호
              </dt>
              <dd>
                {clinician?.license_number ?? '-'}
              </dd>
            </div>

            <div>
              <dt>
                <Hospital size={17} />
                소속 병원
              </dt>
              <dd>
                {clinician?.hospital_name ?? '-'}
              </dd>
            </div>

            <div>
              <dt>
                <Building2 size={17} />
                진료과
              </dt>
              <dd>
                {clinician?.department_name ?? '-'}
              </dd>
            </div>
          </dl>
        </section>
      </main>
    </AccountPageLayout>
  )
}
