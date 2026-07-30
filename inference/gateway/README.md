# FastAPI Inference Gateway

Django와 MOSEC 사이에서 strict v1 추론 요청을 검증하고 전달합니다.

```text
Flutter/React → Django REST API → FastAPI Gateway → MOSEC → nnU-Net
```

주요 책임은 요청·응답 검증, MOSEC timeout과 HTTP 오류 변환, 응답 표준화,
health check 제공입니다.

## 로컬 실행

```powershell
Set-Location inference\gateway
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8001
```
