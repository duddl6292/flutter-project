// 환자 홈 화면 UI에서 사용할 임시 Mock 데이터
//
// 추후 Django API가 연결되면
// 이 데이터를 API 응답으로 교체예정

const Map<String, dynamic> patientHomeMock = {
  'patient': {'name': '황민현', 'notification_count': 3},

  'next_appointment': {
    'date': '5.20',
    'day': '화요일',
    'd_day': 'D-1',
    'time': '10:30',
    'type': '진료',
    'hospital_name': '서울아산병원',
    'department': '내과',
    'doctor_name': '김준수 교수',
    'location': '본관 2층 내과 진료실',
  },

  'upcoming_dates': [
    {'day': '일', 'date': '11', 'is_selected': false, 'has_schedule': true},
    {'day': '월', 'date': '12', 'is_selected': false, 'has_schedule': false},
    {'day': '화', 'date': '13', 'is_selected': false, 'has_schedule': false},
    {'day': '수', 'date': '14', 'is_selected': false, 'has_schedule': false},
    {'day': '목', 'date': '15', 'is_selected': false, 'has_schedule': false},
    {'day': '금', 'date': '16', 'is_selected': true, 'has_schedule': true},
    {'day': '토', 'date': '17', 'is_selected': false, 'has_schedule': true},
  ],

  'medication': {
    'date': '5월 16일 (금)',
    'completed_count': 0,
    'total_count': 2,

    'items': [
      {
        'name': '점심약 1회',
        'time': '오후 1:00',
        'status': '복용 전',
        'icon_type': 'purple',
        'is_completed': false,
      },
      {
        'name': '저녁약 1회',
        'time': '오후 7:00',
        'status': '복용 전',
        'icon_type': 'blue',
        'is_completed': false,
      },
    ],
  },
};
