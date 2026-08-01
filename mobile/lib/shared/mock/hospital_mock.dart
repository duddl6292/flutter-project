/// 의료진 로그인 화면의 병원 자동완성에 사용할 Mock 데이터.
///
/// 실제 병원 검색 API가 연결되면 이 목록은 Repository/API 응답으로 교체한다.
///
/// hospital_id:
/// - 서버와 통신할 때 사용할 병원 식별자 후보
///
/// hospital_name:
/// - 사용자 화면에 표시할 병원명
const List<Map<String, String>> hospitalMockList = [
  {
    'hospital_id': '11111111-1111-4111-8111-111111111111', //
    'hospital_name': '서울대학교병원',
  },
  {
    'hospital_id': '22222222-2222-4222-8222-222222222222',
    'hospital_name': '삼성서울병원',
  },
  {
    'hospital_id': '33333333-3333-4333-8333-333333333333',
    'hospital_name': '세브란스병원',
  },
  {
    'hospital_id': '44444444-4444-4444-8444-444444444444',
    'hospital_name': '서울아산병원',
  },
  {
    'hospital_id': '55555555-5555-4555-8555-555555555555',
    'hospital_name': '가톨릭대학교 서울성모병원',
  },
  {
    'hospital_id': '66666666-6666-4666-8666-666666666666',
    'hospital_name': '분당서울대학교병원',
  },
];
