# 프론트엔드 시작 전 결정사항

## 확정됨

- Flutter 앱에는 환자 모드와 의료진 모드가 모두 존재한다.
- React 웹은 의료진 전용 CDSS다.
- Django REST API를 Flutter와 React가 공통으로 사용한다.
- PostgreSQL 17을 사용한다.
- React 로컬 포트는 5173이다.
- Django 로컬 포트는 8000이다.
- Gateway 로컬 포트는 8100이다.
- MOSEC 로컬 포트는 8001이다.
- Flutter 알림은 FCM과 로컬 알림을 사용한다.
- AI는 Genkit + Gemini + MCP 구조를 검토·구현한다.
- CT 추론은 FastAPI Gateway → MOSEC → nnU-Net 경로를 사용한다.

## 팀 결정 필요

- Flutter 라우팅 패키지
- Flutter 상태 관리 패키지
- Flutter HTTP 클라이언트
- React 라우팅 방식
- React 서버 상태 관리 방식
- React 전역 상태 관리 방식
- JWT 저장 및 갱신 방식
- 사용자와 역할 데이터 모델
- API endpoint와 요청·응답 필드
- Genkit 서비스 포트
- MCP 서버 포트
- 의료진 앱에서 허용할 쓰기 기능 범위

## 현재 확인된 식별자

- Android application ID와 Firebase Android package name은 사용자 승인에 따라 `com.brainon.app`으로 설정되어 있다.
- 식별자를 다시 변경할 경우 Firebase Console 등록과 `google-services.json` 재생성이 필요하다.

위 “팀 결정 필요” 항목을 구현 담당자가 임의로 확정하거나 관련 패키지를 설치하지 않는다.
