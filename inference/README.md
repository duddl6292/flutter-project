# BrainOn Inference

기존 FastAPI, MOSEC, nnU-Net 추론 코드를 보존하여 배치할 서비스 위치입니다.

## 예정 구조

- `app/`: API와 추론 서비스 소스
- `app/api/`: FastAPI 라우트와 요청 검증
- `app/services/`: MOSEC 및 nnU-Net 연동 계층
- `tests/`: API 계약과 Mock 추론 테스트

모델 파일, 체크포인트, 의료 영상 및 추론 결과는 Git에 포함하지 않습니다.
모델 학습 기능은 이 저장소 범위에서 제외합니다.

