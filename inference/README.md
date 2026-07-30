# BrainOn Inference

CT 추론 런타임은 `duddl6292/medical-cdss` 저장소의 `react` 브랜치
커밋 `fb24d0eb299697e00ab55df768cf6345b15b5079`에서 이관했습니다.
FastAPI Gateway, MOSEC Worker, nnU-Net 로딩·추론, NIfTI 전후처리,
Mock 서버와 strict v1 요청·응답 계약을 보존합니다.

## 구조

- `gateway/`: Django와 MOSEC 사이의 FastAPI Gateway
- `app/`: MOSEC Worker와 nnU-Net 추론 파이프라인
- `mock_mosec/`: 모델 없이 계약을 검증하는 Mock 서버
- `mosec/`: 실제 GPU 런타임 Docker 설정과 inference-only trainer shim
- `model_artifacts/`: 모델 번들 형식 문서와 manifest 예시
- `tests/`: 전처리, 측정, 모델 로더 및 계약 테스트
- `compose.mock.yaml`: Gateway와 Mock 서버의 로컬 통합 환경
- `compose.yaml`, `compose.gpu.yaml`: 실제 MOSEC GPU 환경

모델 체크포인트, 학습 코드, notebook, 학습 데이터, 의료 영상과 기존 환경
파일은 포함하지 않습니다. 원본 trainer의 학습 루프 대신 저장된 trainer
이름을 해석하는 최소 runtime shim만 유지합니다.

## Mock 통합 실행

저장소 루트에서 실행합니다.

```powershell
docker compose -f inference\compose.mock.yaml up --build
```

- Gateway: `http://localhost:8001`
- Mock MOSEC: `http://localhost:8000`
- Health check: `GET http://localhost:8001/health`
- Inference: `POST http://localhost:8001/api/v1/inference`

요청과 응답 예시는 루트 `contracts/`에 있습니다.
