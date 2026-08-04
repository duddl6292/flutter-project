import {
  KeyRound,
  Mail,
  ShieldCheck,
} from 'lucide-react'

import {
  useEffect,
  useState,
} from 'react'

import {
  useAuthStore,
} from '../../core/auth/authStore'

import {
  changePassword,
  getCurrentAccount,
  updateAccountEmail,
} from './account.api'

import {
  AccountPageLayout,
} from './AccountPageLayout'

import './account.css'

export function AccountSettingsPage() {
  const user = useAuthStore(
    (state) => state.user,
  )
  const updateUser = useAuthStore(
    (state) => state.updateUser,
  )

  const [email, setEmail] =
    useState(user?.email ?? '')
  const [emailSaving, setEmailSaving] =
    useState(false)
  const [emailMessage, setEmailMessage] =
    useState('')
  const [emailError, setEmailError] =
    useState('')

  const [currentPassword, setCurrentPassword] =
    useState('')
  const [newPassword, setNewPassword] =
    useState('')
  const [newPasswordConfirm, setNewPasswordConfirm] =
    useState('')
  const [passwordSaving, setPasswordSaving] =
    useState(false)
  const [passwordMessage, setPasswordMessage] =
    useState('')
  const [passwordError, setPasswordError] =
    useState('')

  useEffect(() => {
    let active = true

    void getCurrentAccount()
      .then((account) => {
        if (!active) return

        setEmail(account.user.email)
        updateUser(account.user)
      })
      .catch(() => {
        // The stored email remains available when loading fails.
      })

    return () => {
      active = false
    }
  }, [updateUser])

  const handleEmailSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()
    setEmailMessage('')
    setEmailError('')

    if (!email.trim()) {
      setEmailError('이메일을 입력해주세요.')
      return
    }

    setEmailSaving(true)

    try {
      const account =
        await updateAccountEmail(
          email.trim(),
        )

      updateUser(account.user)
      setEmail(account.user.email)
      setEmailMessage(
        '이메일을 변경했습니다.',
      )
    } catch (requestError) {
      setEmailError(
        requestError instanceof Error
          ? requestError.message
          : '이메일을 변경하지 못했습니다.',
      )
    } finally {
      setEmailSaving(false)
    }
  }

  const handlePasswordSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()
    setPasswordMessage('')
    setPasswordError('')

    if (newPassword.length < 8) {
      setPasswordError(
        '새 비밀번호는 8자 이상이어야 합니다.',
      )
      return
    }

    if (newPassword !== newPasswordConfirm) {
      setPasswordError(
        '새 비밀번호가 일치하지 않습니다.',
      )
      return
    }

    setPasswordSaving(true)

    try {
      await changePassword({
        currentPassword,
        newPassword,
        newPasswordConfirm,
      })

      setCurrentPassword('')
      setNewPassword('')
      setNewPasswordConfirm('')
      setPasswordMessage(
        '비밀번호를 변경했습니다.',
      )
    } catch (requestError) {
      setPasswordError(
        requestError instanceof Error
          ? requestError.message
          : '비밀번호를 변경하지 못했습니다.',
      )
    } finally {
      setPasswordSaving(false)
    }
  }

  return (
    <AccountPageLayout>
      <main className="account-page">
        <header className="account-page-heading">
          <div>
            <h1>계정 설정</h1>
            <p>
              로그인 계정의 이메일과 비밀번호를 관리합니다.
            </p>
          </div>
        </header>

        <div className="account-settings-grid">
          <form
            className="account-card account-form"
            onSubmit={(event) => {
              void handleEmailSubmit(event)
            }}
          >
            <header>
              <div className="account-card-icon">
                <Mail size={20} />
              </div>
              <div>
                <h2>이메일 설정</h2>
                <p>
                  이메일 알림을 받을 주소로 사용합니다.
                </p>
              </div>
            </header>

            <label>
              <span>로그인 아이디</span>
              <input
                value={user?.username ?? ''}
                readOnly
                disabled
              />
            </label>

            <label>
              <span>이메일</span>
              <input
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                required
              />
            </label>

            {emailError && (
              <p className="account-inline-error">
                {emailError}
              </p>
            )}

            {emailMessage && (
              <p className="account-inline-success">
                {emailMessage}
              </p>
            )}

            <button
              type="submit"
              className="account-primary-button"
              disabled={emailSaving}
            >
              {emailSaving
                ? '저장 중'
                : '이메일 저장'}
            </button>
          </form>

          <form
            className="account-card account-form"
            onSubmit={(event) => {
              void handlePasswordSubmit(event)
            }}
          >
            <header>
              <div className="account-card-icon">
                <KeyRound size={20} />
              </div>
              <div>
                <h2>비밀번호 변경</h2>
                <p>
                  현재 비밀번호 확인 후 새 비밀번호를 저장합니다.
                </p>
              </div>
            </header>

            <label>
              <span>현재 비밀번호</span>
              <input
                type="password"
                autoComplete="current-password"
                value={currentPassword}
                onChange={(event) =>
                  setCurrentPassword(
                    event.target.value,
                  )
                }
                required
              />
            </label>

            <label>
              <span>새 비밀번호</span>
              <input
                type="password"
                autoComplete="new-password"
                minLength={8}
                value={newPassword}
                onChange={(event) =>
                  setNewPassword(
                    event.target.value,
                  )
                }
                required
              />
            </label>

            <label>
              <span>새 비밀번호 확인</span>
              <input
                type="password"
                autoComplete="new-password"
                minLength={8}
                value={newPasswordConfirm}
                onChange={(event) =>
                  setNewPasswordConfirm(
                    event.target.value,
                  )
                }
                required
              />
            </label>

            {passwordError && (
              <p className="account-inline-error">
                {passwordError}
              </p>
            )}

            {passwordMessage && (
              <p className="account-inline-success">
                {passwordMessage}
              </p>
            )}

            <button
              type="submit"
              className="account-primary-button"
              disabled={passwordSaving}
            >
              <ShieldCheck size={17} />
              {passwordSaving
                ? '변경 중'
                : '비밀번호 변경'}
            </button>
          </form>
        </div>
      </main>
    </AccountPageLayout>
  )
}
