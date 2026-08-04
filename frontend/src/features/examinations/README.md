# Examinations

일반 검사결과 목록, 측정값 등록, 판독 확정, 환자 공개 기능을 담당합니다.

- 웹 개발 환경에서는 `vite.config.ts`의 Mock API를 사용합니다.
- 운영 API 계약은 Django `apps.diagnostics`와 동일합니다.
- CT 원본 업로드와 AI 분석은 별도 CT 분석 기능에서 관리합니다.
