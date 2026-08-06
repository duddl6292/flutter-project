import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/shared/models/hospital.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final hospitalRepositoryProvider = Provider(
  (ref) => HospitalRepository(ref.watch(apiClientProvider)),
);

class HospitalRepository {
  const HospitalRepository(this._dio);
  final Dio _dio;
  Future<List<Hospital>> getHospitals() => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/hospitals/',
      queryParameters: {'page_size': 100},
    );
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows.map((row) => Hospital.fromJson(row as Map<String, dynamic>)).toList();
  });
}
