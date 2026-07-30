# 서버·DB·배포 문서

서버·DB·배포 담당자는 다음 범위를 관리한다.

- PostgreSQL 17 실행과 운영
- Docker 및 Compose
- Django 컨테이너
- React/Nginx 컨테이너
- AI 서비스 컨테이너
- FastAPI Gateway 및 MOSEC
- Cloud Run
- GPU 추론 서버
- 환경변수와 Secret 관리
- DB 백업
- 로그와 health check

Django 모델과 테이블 구조를 직접 SQL로 만들지 않는다. Django 담당자가 관리하는 모델과 migration을 배포 과정에서 실행한다.
