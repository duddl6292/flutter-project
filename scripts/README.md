# Windows PowerShell 스크립트

Windows 11과 PowerShell 기준의 로컬 실행, migration, 안전한 가상 샘플 데이터, 테스트 및 검증 스크립트를 둘 영역이다.

- 저장소 루트에서 실행하는 방식을 기본으로 한다.
- 실제 비밀값과 의료 데이터를 스크립트에 포함하지 않는다.
- 서버·DB·배포 담당자가 공통 실행 방식을 관리한다.
- Django 모델과 migration은 Django 담당자가 작성하며 배포 스크립트가 임의로 SQL 테이블을 생성하지 않는다.
- 현재 최소 검증 명령은 `verify/README.md`를 참고한다.
