# 환자 병합 API — 후순위 설계안

신원미상으로 임시 생성된 환자와 기존 환자가 동일인임을 확인했을 때 PK를 변경하지 않고 병합합니다.

## 권장 엔드포인트

| Method | Endpoint | 기능 |
|---|---|---|
| POST | `/api/v1/patients/{source_patient_id}/merge` | source를 target으로 병합 |
| GET | `/api/v1/patients/{patient_id}/merge-history` | 병합 이력 |

## 요청 예시

```json
{
  "target_patient_id": "기존-patient-uuid",
  "reason": "본인 확인 완료",
  "verification_method": "MRN_AND_IDENTITY_CHECK"
}
```

## 핵심 규칙

- `source_patient_id`를 삭제하지 않고 `MERGED` 상태로 남깁니다.
- `merged_into_patient_id`로 정식 환자를 가리킵니다.
- 과거 처방·검사·예약의 원본 ID와 감사 기록을 보존합니다.
- source 또는 target ID로 검색해도 최종 정식 환자를 반환할 수 있습니다.
- 병합은 관리자 또는 제한된 의료진만 수행합니다.
- 역병합은 별도의 감사 승인 절차 없이는 허용하지 않습니다.

이 API는 DB FK 재연결, 중복 데이터 규칙, 감사 로그 정책을 먼저 확정한 후 구현합니다.
