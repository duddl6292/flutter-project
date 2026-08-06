# Consultations

의료진 웹의 협진 요청·응답·상태 관리 화면이다.

## 현재 구현

- 전체·받은·보낸 협진 목록과 검색·필터
- 진료 건 및 협진 의료진을 선택하는 신규 요청
- 요청 내용과 순차 메시지 상세
- 받은 요청 수락, 최종 소견 등록 및 완료
- 보낸 요청 취소
- 대시보드 및 사이드바 연결

`npm run dev:mock`에서는 `vite.config.ts`의 Mock API가 실제 API와 같은
`/api/v1/consultations/` 계약을 제공한다. 실제 백엔드 연결 시
`consultation.api.ts`를 변경하지 않고 환경의 API base URL만 전환한다.
