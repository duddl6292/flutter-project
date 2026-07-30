# 배포 작업 경계

## 서버·DB·배포 담당

- PostgreSQL 운영, 백업, 복원 절차
- Dockerfile, Compose, Nginx와 배포 파이프라인
- Django, React, AI, Gateway, MOSEC 런타임 배포
- Cloud Run과 GPU 서버 설정
- Secret, 로그, health check와 모니터링

## 다른 담당자와 합의가 필요한 변경

- Django 모델과 migration: Django 담당자가 작성
- API 계약: Django·Flutter·React 담당자가 합의
- AI 및 MCP 포트: Django·AI·MCP 담당자와 합의
- inference 런타임: 추론 담당 로직을 보존하고 배포 설정만 협의

서버 담당자는 Django 테이블을 직접 SQL로 생성하거나 모델과 다른 스키마를 운영하지 않는다.
