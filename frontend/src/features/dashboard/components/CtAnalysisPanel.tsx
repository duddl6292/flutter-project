import type {
  ChangeEventHandler,
  DragEvent,
  DragEventHandler,
  RefObject,
} from 'react'
import { UploadCloud } from 'lucide-react'

import type {
  CtHistoryItem,
  CtStatus,
  DashboardPatient,
} from '../dashboard.types'
import {
  ctStatusLabel,
  ctStatusTone,
  formatDateTime,
  genderLabel,
  PanelTitle,
  StatusBadge,
} from './dashboardUi'

interface CtAnalysisPanelProps {
  patients: DashboardPatient[]
  history: CtHistoryItem[]
  selectedPatientId: string
  selectedFile: File | null
  currentStatus: CtStatus | null
  currentProgress: number
  dashboardLoading: boolean
  historyLoading: boolean
  uploading: boolean
  uploadError: string
  historyError: string
  fileInputRef:
    RefObject<HTMLInputElement | null>
  onPatientChange: (patientId: string) => void
  onFileChange: ChangeEventHandler<HTMLInputElement>
  onDrop: DragEventHandler<HTMLButtonElement>
}

export function CtAnalysisPanel({
  patients,
  history,
  selectedPatientId,
  selectedFile,
  currentStatus,
  currentProgress,
  dashboardLoading,
  historyLoading,
  uploading,
  uploadError,
  historyError,
  fileInputRef,
  onPatientChange,
  onFileChange,
  onDrop,
}: CtAnalysisPanelProps) {
  return (
    <article className="dashboard-panel ct-panel">
      <PanelTitle title="CT 분석 요청 및 결과" />
      <p className="section-caption">
        새로운 CT 분석 요청
      </p>

      <select
        aria-label="CT 분석 대상 환자"
        value={selectedPatientId}
        onChange={(event) =>
          onPatientChange(event.target.value)
        }
        disabled={dashboardLoading || uploading}
        style={{
          width: '100%',
          minHeight: 42,
          marginBottom: 12,
          padding: '0 12px',
          border: '1px solid #d9dce5',
          borderRadius: 10,
          background: '#fff',
        }}
      >
        <option value="">
          환자를 선택해주세요
        </option>
        {patients.map((patient) => (
          <option
            key={patient.patient_id}
            value={patient.patient_id}
          >
            {patient.patient_id} · {patient.name}
          </option>
        ))}
      </select>

      <input
        ref={fileInputRef}
        type="file"
        accept=".dcm,.nii,.nii.gz"
        hidden
        onChange={onFileChange}
      />

      <button
        className="upload-box"
        type="button"
        disabled={uploading || !selectedPatientId}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(
          event: DragEvent<HTMLButtonElement>,
        ) => event.preventDefault()}
        onDrop={onDrop}
      >
        <UploadCloud size={35} />
        <div>
          <strong>
            {uploading
              ? `${
                currentStatus
                  ? ctStatusLabel(currentStatus)
                  : '업로드 중'
              } (${currentProgress}%)`
              : selectedFile?.name
                ?? 'CT 파일을 끌어오거나 클릭하여 업로드'}
          </strong>
          <span>
            지원 형식: DICOM (.dcm), NIfTI
            (.nii, .nii.gz)
          </span>
        </div>
        <span className="file-button">
          {uploading
            ? '분석 진행 중'
            : '파일 선택'}
        </span>
      </button>

      {uploading && (
        <progress
          value={currentProgress}
          max={100}
          style={{
            width: '100%',
            marginTop: 10,
          }}
        />
      )}

      {uploadError && (
        <p
          role="alert"
          className="upload-error"
          style={{ color: '#b42318' }}
        >
          {uploadError}
        </p>
      )}

      <p className="section-caption recent-caption">
        최근 분석 결과
      </p>

      {historyError && (
        <p
          role="alert"
          style={{ color: '#b42318' }}
        >
          {historyError}
        </p>
      )}

      <div className="ct-result-list">
        {history.map((result) => (
          <div
            className="ct-result-item"
            key={String(result.ct_id)}
          >
            <strong>{result.display_id}</strong>
            <span>
              {result.patient_name} ({
                genderLabel(result.gender)
              }/{result.age})
            </span>
            <StatusBadge
              tone={ctStatusTone(result.status)}
            >
              {ctStatusLabel(result.status)}
            </StatusBadge>
            <time>
              {formatDateTime(result.created_at)}
            </time>
          </div>
        ))}

        {!historyLoading && history.length === 0 && (
          <p style={{ textAlign: 'center' }}>
            최근 CT 분석 이력이 없습니다.
          </p>
        )}
      </div>
    </article>
  )
}
