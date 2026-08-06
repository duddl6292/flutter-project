import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/features/patient/providers/patient_profile_provider.dart';
import 'package:brainon_mobile/features/patient/repositories/api_patient_profile_repository.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ApiPatientProfileRepository', () {
    test('gets patients/me and parses the data envelope', () async {
      late RequestOptions captured;
      final dio = Dio(BaseOptions(baseUrl: 'https://example.test'));
      dio.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) {
            captured = options;
            handler.resolve(
              Response<Map<String, dynamic>>(
                requestOptions: options,
                statusCode: 200,
                data: {
                  'data': {
                    'patient_id': 'fd911ac9-3965-4a76-bc72-13d207f0fa41',
                    'user_id': '90a6c756-2168-4492-a4cc-bf92291cafe8',
                    'username': 'patient01',
                    'email': 'patient01@example.com',
                    'medical_record_number': 'BRN-2026-000006',
                    'name': '강승현',
                    'birth_date': '1987-07-13',
                    'sex': 'F',
                    'phone': '010-0000-0006',
                    'emergency_contact': '010-9000-0006',
                    'address': '서울특별시 종로구',
                    'status': 'ACTIVE',
                  },
                },
              ),
            );
          },
        ),
      );
      final repository = ApiPatientProfileRepository(dio);

      final profile = await repository.getMyProfile();

      expect(captured.method, 'GET');
      expect(captured.path, '/api/v1/patients/me/');
      expect(profile.id, 'fd911ac9-3965-4a76-bc72-13d207f0fa41');
      expect(profile.patientNumber, 'BRN-2026-000006');
      expect(profile.birthDate, DateTime(1987, 7, 13));
      expect(profile.sex, 'F');
    });

    test('passes a Dio failure through as an ApiException', () async {
      final dio = Dio(BaseOptions(baseUrl: 'https://example.test'));
      dio.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) {
            handler.reject(
              DioException(
                requestOptions: options,
                type: DioExceptionType.badResponse,
                response: Response<Map<String, dynamic>>(
                  requestOptions: options,
                  statusCode: 503,
                  data: {
                    'error': {
                      'code': 'SERVICE_UNAVAILABLE',
                      'message': '잠시 후 다시 시도해 주세요.',
                    },
                  },
                ),
              ),
            );
          },
        ),
      );
      final repository = ApiPatientProfileRepository(dio);

      await expectLater(
        repository.getMyProfile(),
        throwsA(
          isA<ApiException>()
              .having((error) => error.code, 'code', 'SERVICE_UNAVAILABLE')
              .having((error) => error.statusCode, 'statusCode', 503),
        ),
      );
    });
  });

  test('patientProfileRepositoryProvider selects the API repository', () {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    expect(
      container.read(patientProfileRepositoryProvider),
      isA<ApiPatientProfileRepository>(),
    );
  });
}
