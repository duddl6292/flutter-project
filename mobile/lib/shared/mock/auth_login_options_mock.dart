/// Development-only fallback shaped exactly like the public Django directory
/// API responses. Production builds never use these values.
const List<Map<String, dynamic>> authHospitalMockData = [
  {
    'hospital_id': '11111111-1111-4111-8111-111111111111',
    'hospital_code': 'H001',
    'hospital_name': '서울대학교병원',
    'address': '서울특별시 종로구 대학로 101',
    'phone': '02-2072-2114',
  },
  {
    'hospital_id': '22222222-2222-4222-8222-222222222222',
    'hospital_code': 'H002',
    'hospital_name': '삼성서울병원',
    'address': '서울특별시 강남구 일원로 81',
    'phone': '02-3410-2114',
  },
];

const List<Map<String, dynamic>> authDepartmentMockData = [
  {
    'department_id': '11111111-1111-4111-8111-111111111111',
    'code': 'NEU',
    'name': '신경과',
    'is_active': true,
  },
  {
    'department_id': '22222222-2222-4222-8222-222222222222',
    'code': 'RADIOLOGY',
    'name': '영상의학과',
    'is_active': true,
  },
];
