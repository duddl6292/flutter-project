import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/core/auth/auth_repository.dart';
import 'package:brainon_mobile/core/auth/auth_state.dart';
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
  AuthState build() => const AuthState();

  Future<void> login({
    required String username,
    required String password,
    required String expectedRole,
  }) async {
    state = const AuthState(status: AuthStatus.authenticating);
    try {
      final user = await ref
          .read(authRepositoryProvider)
          .login(
            username: username,
            password: password,
            expectedRole: expectedRole,
          );
      state = AuthState(status: AuthStatus.authenticated, user: user);
    } on Object {
      state = const AuthState();
      rethrow;
    }
  }

  Future<void> logout() async {
    await ref.read(authRepositoryProvider).logout();
    signedOut();
  }

  void signedOut() {
    state = const AuthState();
  }
}
