enum AuthStatus { unauthenticated, authenticating, authenticated }

class AuthUser {
  const AuthUser({
    required this.id,
    required this.username,
    required this.role,
  });

  final int id;
  final String username;
  final String role;

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    return AuthUser(
      id: json['id'] as int,
      username: json['username'] as String,
      role: json['role'] as String,
    );
  }
}

class AuthState {
  const AuthState({this.status = AuthStatus.unauthenticated, this.user});

  final AuthStatus status;
  final AuthUser? user;
}
