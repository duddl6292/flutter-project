import assert from 'node:assert/strict';
import test from 'node:test';

import { requestsProtectedPatientData } from '../src/flows/assistantFlow.js';

test('patient-specific record requests are blocked before model invocation', () => {
  assert.equal(
    requestsProtectedPatientData(
      '담당 환자의 최근 진료와 검사결과를 요약해 주세요.',
    ),
    true,
  );
  assert.equal(
    requestsProtectedPatientData('테스트환자A의 예약 시간을 알려줘.'),
    true,
  );
});

test('public hospital lookup remains available to MCP tools', () => {
  assert.equal(
    requestsProtectedPatientData('서울 지역 병원을 5개 알려줘.'),
    false,
  );
});

test('general knowledge questions remain available to Gemini without tools', () => {
  assert.equal(
    requestsProtectedPatientData('뇌졸중의 일반적인 전조 증상을 설명해 줘'),
    false,
  );
});

test('a named patient appointment request is treated as protected data', () => {
  assert.equal(
    requestsProtectedPatientData('이현우 환자 예약 시간 알려줘'),
    true,
  );
});

test('a patient first-person medication request is protected data', () => {
  assert.equal(
    requestsProtectedPatientData('오늘 내가 먹어야 할 약 알려줘'),
    true,
  );
});
