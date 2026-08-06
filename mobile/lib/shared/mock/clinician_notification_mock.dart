const clinicianNotificationMock = <Map<String, dynamic>>[
  {
    'id': 'n-001',
    'type': 'consultation',
    'title': '새 협진 요청',
    'message': '신경외과에서 협진을 요청했습니다.',
    'created_at': '2026-08-05T09:00:00+09:00',
    'is_read': false,
  },
  {
    'id': 'n-002',
    'type': 'test_result',
    'title': '검사 결과 도착',
    'message': '김민준 환자의 MRI 결과가 도착했습니다.',
    'created_at': '2026-08-05T08:30:00+09:00',
    'is_read': false,
  },
  {
    'id': 'n-003',
    'type': 'schedule',
    'title': '일정 변경',
    'message': '오후 진료 일정이 변경되었습니다.',
    'created_at': '2026-08-04T18:00:00+09:00',
    'is_read': false,
  },
];
