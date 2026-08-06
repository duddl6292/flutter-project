import 'package:brainon_mobile/core/auth/auth_repository.dart';
import 'package:brainon_mobile/core/storage/token_storage.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    FlutterSecureStorage.setMockInitialValues({});
  });

  test('uses the clinician endpoint and parses the data envelope', () async {
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
                  'access': 'access-token',
                  'refresh': 'refresh-token',
                  'user': {
                    'id': 'user-id',
                    'username': 'doctor',
                    'email': '',
                    'role': 'CLINICIAN',
                  },
                  'clinician': {
                    'id': 'clinician-id',
                    'name': 'Doctor Kim',
                    'license_number': '123456',
                    'approval_status': 'APPROVED',
                    'hospital_id': 'hospital-id',
                    'hospital_name': 'Hospital',
                    'department_id': 'department-id',
                    'department_code': 'D',
                    'department_name': 'Neurology',
                  },
                },
              },
            ),
          );
        },
      ),
    );
    final storage = TokenStorage();
    final repository = AuthRepository(dio, storage);

    final user = await repository.login(
      role: UserRole.clinician,
      password: 'password',
      hospitalId: 'hospital-id',
      departmentCode: 'D',
      licenseNumber: '123456',
    );

    expect(captured.path, '/api/v1/auth/clinician/login/');
    expect(captured.data, {
      'hospital_id': 'hospital-id',
      'department_code': 'D',
      'license_number': '123456',
      'password': 'password',
    });
    expect(user.role, UserRole.clinician);
    expect(await storage.readAccessToken(), 'access-token');
    expect(await storage.readRefreshToken(), 'refresh-token');
  });

  test('uses the patient login endpoint', () async {
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
                  'access': 'access-token',
                  'refresh': 'refresh-token',
                  'user': {
                    'id': 'user-id',
                    'username': 'patient',
                    'email': '',
                    'role': 'PATIENT',
                  },
                  'patient': {
                    'id': 'patient-id',
                    'name': 'Patient',
                    'birth_date': null,
                    'sex': 'UNKNOWN',
                    'phone': '',
                  },
                },
              },
            ),
          );
        },
      ),
    );
    final repository = AuthRepository(dio, TokenStorage());

    final user = await repository.login(
      role: UserRole.patient,
      username: 'patient',
      password: 'password',
    );

    expect(captured.path, '/api/v1/auth/patient/login/');
    expect(captured.data, {'username': 'patient', 'password': 'password'});
    expect(user.role, UserRole.patient);
  });
}
