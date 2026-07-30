# 브랜치 및 병합 가이드

## 브랜치 구조

```text
main
└─ dev
   ├─ feature/mobile-ui
   ├─ feature/react-cdss
   ├─ feature/backend-domain
   ├─ feature/fcm-foundation
   └─ feature/genkit-mcp-poc
```

## 규칙

- 모든 작업 브랜치는 최신 `dev`에서 생성한다.
- 개인 브랜치에서 `main`으로 직접 PR을 만들지 않는다.
- PR 대상 브랜치는 `dev`다.
- 작업 시작 전에 `git fetch origin`을 실행한다.
- 작업 중 `dev`가 변경되면 개인 브랜치에 `origin/dev`를 병합한다.
- push 전에 담당 영역의 테스트와 빌드를 실행한다.
- API 계약 변경은 팀 합의 후 진행한다.
- 실제 의료 데이터와 비밀키를 커밋하지 않는다.
- `.env`, 서비스 계정 키, 모델 체크포인트를 커밋하지 않는다.

## 작업 브랜치 생성

```powershell
git fetch origin
git checkout dev
git pull origin dev
git checkout -b feature/작업명
```

## 작업 중 최신 dev 반영

```powershell
git fetch origin
git merge origin/dev
```

충돌을 해결한 뒤 담당 영역 테스트를 다시 실행하고 push한다.
