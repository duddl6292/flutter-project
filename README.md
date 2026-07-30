# BrainOn

BrainOn 의료 서비스 모노레포입니다. 환자용 Flutter 앱, 의료진용 React 웹,
Django REST API, 의료 영상 추론 서비스를 한 저장소에서 관리합니다.

이 저장소에는 실제 환자 정보나 운영 비밀키를 저장하지 않습니다.

## 디렉터리

| 경로 | 역할 |
| --- | --- |
| `mobile/` | Flutter 환자용 앱 |
| `frontend/` | React 의료진용 웹 |
| `backend/` | Django REST API |
| `inference/` | FastAPI, MOSEC, nnU-Net 추론 |
| `contracts/` | 서비스 간 API 요청·응답 예시 |
| `docs/` | 설치, 구조, API 문서 |
| `scripts/` | Windows PowerShell 실행 및 관리 스크립트 |

모델 학습 코드는 이 저장소의 범위에 포함하지 않습니다.

## 시작하기

1. `.env.example`을 참고해 로컬 전용 `.env`를 만듭니다.
2. PostgreSQL이 필요하면 `docker compose up -d postgres`를 실행합니다.
3. Flutter 앱은 `Set-Location mobile` 후 `flutter run`으로 실행합니다.

각 서비스의 구체적인 설치 방법은 해당 디렉터리의 `README.md`에 추가합니다.
