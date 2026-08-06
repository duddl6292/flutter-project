class Hospital {
  final String hospitalId;
  final String hospitalName;
  final String address;
  final String phone;

  // 화면 표시용 값
  // hospitals 테이블의 실제 컬럼은 아님
  final bool isFavorite;

  const Hospital({
    required this.hospitalId,
    required this.hospitalName,
    this.address = '',
    this.phone = '',
    this.isFavorite = false,
  });

  factory Hospital.fromJson(Map<String, dynamic> json) {
    return Hospital(
      // 실제 Django 응답은 id/name을 사용하는 방향
      // 기존 Mock도 임시로 호환되도록 두 키 모두 처리
      hospitalId:
          json['id']?.toString() ?? json['hospital_id']?.toString() ?? '',
      hospitalName:
          json['name']?.toString() ?? json['hospital_name']?.toString() ?? '',
      address: json['address']?.toString() ?? '',
      phone: json['phone']?.toString() ?? '',
      isFavorite: json['is_favorite'] == true,
    );
  }

  Hospital copyWith({
    String? hospitalId,
    String? hospitalName,
    String? address,
    String? phone,
    bool? isFavorite,
  }) {
    return Hospital(
      hospitalId: hospitalId ?? this.hospitalId,
      hospitalName: hospitalName ?? this.hospitalName,
      address: address ?? this.address,
      phone: phone ?? this.phone,
      isFavorite: isFavorite ?? this.isFavorite,
    );
  }
}
