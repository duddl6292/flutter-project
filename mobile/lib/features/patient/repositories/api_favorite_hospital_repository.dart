import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/patient/repositories/favorite_hospital_repository.dart';
import 'package:brainon_mobile/shared/models/hospital.dart';
import 'package:dio/dio.dart';

class ApiFavoriteHospitalRepository implements FavoriteHospitalRepository {
  const ApiFavoriteHospitalRepository(this._dio);
  final Dio _dio;

  @override
  Future<List<Hospital>> searchHospitals(String query) => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/hospitals/',
      queryParameters: {'search': query, 'page_size': 100},
    );
    return _rows(response.data).map(Hospital.fromJson).toList();
  });

  @override
  Future<List<Hospital>> getFavoriteHospitals() => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/patients/me/favorite-hospitals/',
      queryParameters: {'page_size': 100},
    );
    return _rows(response.data)
        .map((json) => Hospital.fromJson(json).copyWith(isFavorite: true))
        .toList();
  });

  @override
  Future<void> addFavoriteHospital(Hospital hospital) => runApiRequest(() async {
    await _dio.post<void>(
      '/api/v1/patients/me/favorite-hospitals/',
      data: {'hospital_id': hospital.hospitalId},
    );
  });

  @override
  Future<void> removeFavoriteHospital(String hospitalId) => runApiRequest(() async {
    await _dio.delete<void>('/api/v1/patients/me/favorite-hospitals/$hospitalId/');
  });

  List<Map<String, dynamic>> _rows(Map<String, dynamic>? body) =>
      (body?['data'] as List<dynamic>? ?? const [])
          .cast<Map<String, dynamic>>();
}
