import 'package:brainon_mobile/core/auth/auth_state.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('initial auth state is unauthenticated', () {
    const state = AuthState();

    expect(state.status, AuthStatus.unauthenticated);
    expect(state.user, isNull);
  });
}
