class PatientSignupRequest {
  final String username;
  final String password;
  final String passwordConfirm;
  final String name;
  final String birthDate;
  final String sex;

  const PatientSignupRequest({
    required this.username,
    required this.password,
    required this.passwordConfirm,
    required this.name,
    required this.birthDate,
    required this.sex,
  });

  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'password': password,
      'password_confirm': passwordConfirm,
      'name': name,
      'birth_date': birthDate,
      'sex': sex,
    };
  }
}
