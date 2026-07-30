# Mock MOSEC

실제 nnU-Net 모델과 GPU 없이 Gateway와 MOSEC 사이의 HTTP 통신, strict v1
계약과 오류 처리를 검증하는 개발 전용 서버입니다. 실제 의료 영상을 처리하거나
의료적 의미가 있는 결과를 생성하지 않습니다.

저장소 루트에서 다음 명령으로 실행합니다.

```powershell
docker compose -f inference\compose.mock.yaml up --build
```
