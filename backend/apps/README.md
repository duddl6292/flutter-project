# Django 애플리케이션

현재 구현됨:

- `accounts`: Custom User, `PATIENT`·`CLINICIAN`·`ADMIN` 역할, JWT 인증과 역할 Permission
- `patients`: 최소 PatientProfile
- `clinicians`: 최소 ClinicianProfile
- `core`: 공개 health API, 공통 오류 응답과 페이지네이션

후속 업무 앱 예정:

- `appointments`
- `prescriptions`
- `examinations`
- `clinical_records`
- `consultations`
- `notifications`
- `ai_assistant`

`notifications`는 FCM 기기 등록·발송·이력을, `ai_assistant`는 인증된 Django와 Genkit 간 중계를 담당합니다. 예정 영역은 데이터 모델과 API 계약 합의 전까지 실제 앱이나 migration으로 만들지 않습니다.
