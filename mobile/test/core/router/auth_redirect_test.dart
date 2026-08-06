import 'package:brainon_mobile/core/auth/auth_state.dart';
import 'package:brainon_mobile/core/router/app_router.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:flutter_test/flutter_test.dart';

AuthState authenticated(UserRole role) {
  return AuthState(
    status: AuthStatus.authenticated,
    user: AuthUser(id: 'user-id', username: 'user', role: role),
  );
}

void main() {
  test('clinician is sent to the clinician home', () {
    expect(authRedirect(authenticated(UserRole.clinician), '/'), '/clinician');
    expect(
      authRedirect(authenticated(UserRole.clinician), '/patient'),
      '/clinician',
    );
    expect(
      authRedirect(authenticated(UserRole.clinician), '/patient/signup'),
      '/clinician',
    );
    expect(
      authRedirect(authenticated(UserRole.clinician), '/clinician'),
      isNull,
    );
  });

  test('patient is sent to the patient home', () {
    expect(authRedirect(authenticated(UserRole.patient), '/'), '/patient');
    expect(
      authRedirect(authenticated(UserRole.patient), '/clinician'),
      '/patient',
    );
    expect(authRedirect(authenticated(UserRole.patient), '/patient'), isNull);
  });

  test('unauthenticated users cannot enter protected routes', () {
    expect(authRedirect(const AuthState(), '/clinician'), '/');
    expect(authRedirect(const AuthState(), '/patient'), '/');
    expect(authRedirect(const AuthState(), '/login'), isNull);
  });
}
