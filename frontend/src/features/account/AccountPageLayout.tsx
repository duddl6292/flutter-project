import {
  useEffect,
  useRef,
  useState,
} from 'react'

import type {
  ReactNode,
} from 'react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  logout,
} from '../../core/api/authApi'

import {
  useAuthStore,
} from '../../core/auth/authStore'

import {
  DashboardHeader,
} from '../dashboard/components/DashboardHeader'

import {
  DashboardSidebar,
} from '../dashboard/components/DashboardSidebar'

import '../dashboard/dashboard.css'

interface AccountPageLayoutProps {
  children: ReactNode
}

export function AccountPageLayout({
  children,
}: AccountPageLayoutProps) {
  const navigate = useNavigate()
  const searchInputRef =
    useRef<HTMLInputElement>(null)
  const [searchText, setSearchText] =
    useState('')

  const clinician = useAuthStore(
    (state) => state.clinician,
  )

  useEffect(() => {
    const handleShortcut = (
      event: KeyboardEvent,
    ) => {
      if (
        (event.ctrlKey || event.metaKey)
        && event.key.toLowerCase() === 'k'
      ) {
        event.preventDefault()
        searchInputRef.current?.focus()
      }
    }

    window.addEventListener(
      'keydown',
      handleShortcut,
    )

    return () => {
      window.removeEventListener(
        'keydown',
        handleShortcut,
      )
    }
  }, [])

  const handleSearch = () => {
    const keyword = searchText.trim()

    navigate(
      keyword
        ? `/patients?search=${
          encodeURIComponent(keyword)
        }`
        : '/patients',
    )
  }

  const doctor = {
    name: clinician?.name ?? '의료진',
    department:
      clinician?.department_name ?? '-',
    title: '의료진',
  }

  return (
    <div className="brainon-dashboard">
      <DashboardSidebar />

      <div className="main-area">
        <DashboardHeader
          searchInputRef={searchInputRef}
          searchText={searchText}
          doctor={doctor}
          onSearchTextChange={setSearchText}
          onSearch={handleSearch}
          onLogout={() => {
            logout()
            navigate(
              '/login',
              { replace: true },
            )
          }}
        />

        {children}
      </div>
    </div>
  )
}
