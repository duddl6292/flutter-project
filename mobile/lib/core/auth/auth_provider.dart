import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/core/auth/auth_repository.dart';
import 'package:brainon_mobile/core/auth/auth_state.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(
    ref.watch(apiClientProvider),
    ref.watch(tokenStorageProvider),
  );
});

final authProvider = NotifierProvider<AuthNotifier, AuthState>(
  AuthNotifier.new,
);

class AuthNotifier extends Notifier<AuthState> {
  @override
  AuthState build() {
    Future<void>.microtask(_restoreSession);

    return const AuthState(status: AuthStatus.restoring);
  }

  // ==========================================================
  // 앱 시작 시 저장된 로그인 세션 복원
  // ==========================================================
  Future<void> _restoreSession() async {
    final repository = ref.read(authRepositoryProvider);

    if (!await repository.hasStoredTokens()) {
      state = const AuthState();
      return;
    }

    try {
      final user = await repository.me();

      state = AuthState(status: AuthStatus.authenticated, user: user);
    } on Object {
      await repository.logout();
      state = const AuthState();
    }
  }

  // ==========================================================
  // 실제 로그인 API
  //
  // 현재 개발용 우회를 사용하더라도 이 코드는 삭제하지 않는다.
  // login_screen.dart에서 개발 우회 설정을 false로 바꾸면
  // 다시 이 함수가 호출된다.
  // ==========================================================
  Future<void> login({
    required UserRole role,
    required String password,
    String? username,
    String? hospitalId,
    String? departmentCode,
    String? licenseNumber,
  }) async {
    state = const AuthState(status: AuthStatus.authenticating);

    try {
      final user = await ref
          .read(authRepositoryProvider)
          .login(
            role: role,
            password: password,
            username: username,
            hospitalId: hospitalId,
            departmentCode: departmentCode,
            licenseNumber: licenseNumber,
          );

      state = AuthState(status: AuthStatus.authenticated, user: user);
    } on Object {
      state = const AuthState();
      rethrow;
    }
  }

  Future<void> refreshAccount() async {
    final user = await ref.read(authRepositoryProvider).me();
    state = AuthState(status: AuthStatus.authenticated, user: user);
  }

  Future<void> updateEmail(String email) async {
    final user = await ref.read(authRepositoryProvider).updateEmail(email);
    state = AuthState(status: AuthStatus.authenticated, user: user);
  }

  // ==========================================================
  // 로그아웃
  // ==========================================================
  Future<void> logout() async {
    await ref.read(authRepositoryProvider).logout();
    signedOut();
  }

  // ==========================================================
  // 개발용 의료진 임시 로그인
  //
  // 로그인 API 연결 전 의료진 화면을 확인하기 위한 우회 코드다.
  // kDebugMode에서만 실행할 수 있다.
  // ==========================================================
  void startDevelopmentClinicianSession() {
    if (!kDebugMode) {
      throw StateError('Development clinician login is disabled.');
    }

    state = const AuthState(
      status: AuthStatus.authenticated,
      user: AuthUser(
        id: 'development-clinician',
        username: 'development-clinician',
        role: UserRole.clinician,
        clinician: AuthClinician(
          id: 'development-clinician',
          name: '이현우',
          licenseNumber: '',
          approvalStatus: 'APPROVED',
          hospitalId: '',
          hospitalName: '',
          departmentId: '',
          departmentCode: 'NEU',
          departmentName: '신경과',
        ),
      ),
    );
  }

  // ==========================================================
  // 개발용 환자 임시 로그인
  //
  // 로그인 API 연결 전 환자 화면을 확인하기 위한 우회 코드다.
  // 단순 화면 이동만 하는 것이 아니라 AuthState를 authenticated로
  // 변경하기 때문에 GoRouter의 인증 redirect도 정상 통과한다.
  // ==========================================================
  void startDevelopmentPatientSession() {
    if (!kDebugMode) {
      throw StateError('Development patient login is disabled.');
    }

    state = const AuthState(
      status: AuthStatus.authenticated,
      user: AuthUser(
        id: 'development-patient',
        username: 'development-patient',
        role: UserRole.patient,
      ),
    );
  }

  // ==========================================================
  // 인증 상태 초기화
  // ==========================================================
  void signedOut() {
    state = const AuthState();
  }
}
