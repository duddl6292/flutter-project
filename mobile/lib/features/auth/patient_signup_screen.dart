import 'package:brainon_mobile/shared/models/patient_signup_request.dart';
import 'package:brainon_mobile/features/auth/repositories/auth_repository.dart';
import 'package:flutter/material.dart';

class PatientSignupScreen extends StatefulWidget {
  const PatientSignupScreen({super.key});

  @override
  State<PatientSignupScreen> createState() => _PatientSignupScreenState();
}

class _PatientSignupScreenState extends State<PatientSignupScreen> {
  final _formKey = GlobalKey<FormState>();

  final AuthRepository _authRepository = AuthRepository();

  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _passwordConfirmController = TextEditingController();

  final _medicalRecordNumberController = TextEditingController();
  final _patientNameController = TextEditingController();
  final _birthDateController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emergencyContactController = TextEditingController();
  final _addressController = TextEditingController();

  String _selectedSex = 'UNKNOWN';

  bool _obscurePassword = true;
  bool _obscurePasswordConfirm = true;
  bool _agreePrivacy = false;
  bool _agreeSensitiveInfo = false;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _lastNameController.dispose();
    _firstNameController.dispose();
    _passwordController.dispose();
    _passwordConfirmController.dispose();
    _medicalRecordNumberController.dispose();
    _patientNameController.dispose();
    _birthDateController.dispose();
    _phoneController.dispose();
    _emergencyContactController.dispose();
    _addressController.dispose();

    super.dispose();
  }

  Future<void> _selectBirthDate() async {
    final today = DateTime.now();

    final selectedDate = await showDatePicker(
      context: context,
      initialDate: DateTime(today.year - 30),
      firstDate: DateTime(1900),
      lastDate: today,
      helpText: '생년월일 선택',
      cancelText: '취소',
      confirmText: '확인',
    );

    if (selectedDate == null) {
      return;
    }

    _birthDateController.text =
        '${selectedDate.year}-'
        '${selectedDate.month.toString().padLeft(2, '0')}-'
        '${selectedDate.day.toString().padLeft(2, '0')}';
  }

  Future<void> _submitSignup() async {
    FocusScope.of(context).unfocus();

    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (!_agreePrivacy || !_agreeSensitiveInfo) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('필수 약관에 모두 동의해 주세요.')));
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final request = PatientSignupRequest(
        username: _usernameController.text.trim(),
        password: _passwordController.text,
        email: _emailController.text.trim(),
        firstName: _firstNameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        medicalRecordNumber: _medicalRecordNumberController.text.trim(),
        patientName: _patientNameController.text.trim(),
        birthDate: _birthDateController.text.trim(),
        sex: _selectedSex,
        phone: _phoneController.text.trim(),
        emergencyContact: _emergencyContactController.text.trim(),
        address: _addressController.text.trim(),
      );

      await _authRepository.signupPatient(request);

      if (!mounted) {
        return;
      }

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('회원가입이 완료되었습니다.')));

      Navigator.of(context).pop();
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        elevation: 0,
        title: const Text(
          '환자 회원가입',
          style: TextStyle(
            color: Color(0xFF111827),
            fontSize: 20,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 24, 20, 40),
            children: [
              const Text(
                '계정 정보',
                style: TextStyle(
                  color: Color(0xFF111827),
                  fontSize: 21,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                '로그인에 사용할 계정 정보를 입력해 주세요.',
                style: TextStyle(color: Color(0xFF6B7280), fontSize: 14),
              ),
              const SizedBox(height: 20),

              _SignupTextField(
                controller: _usernameController,
                label: '아이디',
                hintText: '영문, 숫자, 밑줄 포함 4자 이상',
                prefixIcon: Icons.person_outline,
                validator: (value) {
                  final text = value?.trim() ?? '';

                  if (text.isEmpty) {
                    return '아이디를 입력해 주세요.';
                  }

                  if (text.length < 4) {
                    return '아이디는 4자 이상 입력해 주세요.';
                  }

                  final pattern = RegExp(r'^[a-zA-Z0-9_]+$');

                  if (!pattern.hasMatch(text)) {
                    return '영문, 숫자, 밑줄만 사용할 수 있습니다.';
                  }

                  return null;
                },
              ),
              const SizedBox(height: 14),

              _SignupTextField(
                controller: _emailController,
                label: '이메일',
                hintText: 'example@email.com',
                prefixIcon: Icons.email_outlined,
                keyboardType: TextInputType.emailAddress,
                validator: (value) {
                  final text = value?.trim() ?? '';

                  if (text.isEmpty) {
                    return '이메일을 입력해 주세요.';
                  }

                  if (!text.contains('@')) {
                    return '올바른 이메일 형식을 입력해 주세요.';
                  }

                  return null;
                },
              ),
              const SizedBox(height: 14),

              Row(
                children: [
                  Expanded(
                    child: _SignupTextField(
                      controller: _lastNameController,
                      label: '성',
                      hintText: '남',
                      validator: _requiredValidator,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _SignupTextField(
                      controller: _firstNameController,
                      label: '이름',
                      hintText: '지원',
                      validator: _requiredValidator,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),

              _SignupTextField(
                controller: _passwordController,
                label: '비밀번호',
                hintText: '8자 이상 입력',
                prefixIcon: Icons.lock_outline,
                obscureText: _obscurePassword,
                suffixIcon: IconButton(
                  onPressed: () {
                    setState(() {
                      _obscurePassword = !_obscurePassword;
                    });
                  },
                  icon: Icon(
                    _obscurePassword
                        ? Icons.visibility_off_outlined
                        : Icons.visibility_outlined,
                  ),
                ),
                validator: (value) {
                  final text = value ?? '';

                  if (text.isEmpty) {
                    return '비밀번호를 입력해 주세요.';
                  }

                  if (text.length < 8) {
                    return '비밀번호는 8자 이상 입력해 주세요.';
                  }

                  return null;
                },
              ),
              const SizedBox(height: 14),

              _SignupTextField(
                controller: _passwordConfirmController,
                label: '비밀번호 확인',
                hintText: '비밀번호를 다시 입력',
                prefixIcon: Icons.lock_reset_outlined,
                obscureText: _obscurePasswordConfirm,
                suffixIcon: IconButton(
                  onPressed: () {
                    setState(() {
                      _obscurePasswordConfirm = !_obscurePasswordConfirm;
                    });
                  },
                  icon: Icon(
                    _obscurePasswordConfirm
                        ? Icons.visibility_off_outlined
                        : Icons.visibility_outlined,
                  ),
                ),
                validator: (value) {
                  if ((value ?? '').isEmpty) {
                    return '비밀번호 확인을 입력해 주세요.';
                  }

                  if (value != _passwordController.text) {
                    return '비밀번호가 일치하지 않습니다.';
                  }

                  return null;
                },
              ),

              const SizedBox(height: 32),

              const Text(
                '환자 정보',
                style: TextStyle(
                  color: Color(0xFF111827),
                  fontSize: 21,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                '병원에 등록된 환자 정보와 동일하게 입력해 주세요.',
                style: TextStyle(color: Color(0xFF6B7280), fontSize: 14),
              ),
              const SizedBox(height: 20),

              _SignupTextField(
                controller: _medicalRecordNumberController,
                label: '병원 환자번호',
                hintText: '병원에서 발급받은 환자번호',
                prefixIcon: Icons.badge_outlined,
                validator: _requiredValidator,
              ),
              const SizedBox(height: 14),

              _SignupTextField(
                controller: _patientNameController,
                label: '환자 이름',
                hintText: '병원 등록 이름',
                prefixIcon: Icons.account_circle_outlined,
                validator: _requiredValidator,
              ),
              const SizedBox(height: 14),

              _SignupTextField(
                controller: _birthDateController,
                label: '생년월일',
                hintText: 'YYYY-MM-DD',
                prefixIcon: Icons.calendar_month_outlined,
                readOnly: true,
                onTap: _selectBirthDate,
                validator: _requiredValidator,
              ),
              const SizedBox(height: 14),

              DropdownButtonFormField<String>(
                initialValue: _selectedSex,
                decoration: _inputDecoration(
                  label: '성별',
                  prefixIcon: Icons.wc_outlined,
                ),
                items: const [
                  DropdownMenuItem(value: 'M', child: Text('남성')),
                  DropdownMenuItem(value: 'F', child: Text('여성')),
                  DropdownMenuItem(value: 'UNKNOWN', child: Text('선택 안 함')),
                ],
                onChanged: (value) {
                  setState(() {
                    _selectedSex = value ?? 'UNKNOWN';
                  });
                },
              ),
              const SizedBox(height: 14),

              _SignupTextField(
                controller: _phoneController,
                label: '휴대전화번호',
                hintText: '010-0000-0000',
                prefixIcon: Icons.phone_outlined,
                keyboardType: TextInputType.phone,
                validator: _requiredValidator,
              ),
              const SizedBox(height: 14),

              _SignupTextField(
                controller: _emergencyContactController,
                label: '비상 연락처',
                hintText: '보호자 또는 가족 연락처',
                prefixIcon: Icons.contact_emergency_outlined,
                keyboardType: TextInputType.phone,
              ),
              const SizedBox(height: 14),

              _SignupTextField(
                controller: _addressController,
                label: '주소',
                hintText: '거주지 주소',
                prefixIcon: Icons.home_outlined,
                maxLines: 2,
              ),

              const SizedBox(height: 24),

              CheckboxListTile(
                value: _agreePrivacy,
                onChanged: (value) {
                  setState(() {
                    _agreePrivacy = value ?? false;
                  });
                },
                contentPadding: EdgeInsets.zero,
                controlAffinity: ListTileControlAffinity.leading,
                title: const Text(
                  '개인정보 수집 및 이용에 동의합니다. (필수)',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                ),
              ),
              CheckboxListTile(
                value: _agreeSensitiveInfo,
                onChanged: (value) {
                  setState(() {
                    _agreeSensitiveInfo = value ?? false;
                  });
                },
                contentPadding: EdgeInsets.zero,
                controlAffinity: ListTileControlAffinity.leading,
                title: const Text(
                  '민감정보 및 건강정보 처리에 동의합니다. (필수)',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                ),
              ),

              const SizedBox(height: 20),

              FilledButton(
                onPressed: _isSubmitting ? null : _submitSignup,
                style: FilledButton.styleFrom(
                  minimumSize: const Size.fromHeight(56),
                  backgroundColor: const Color(0xFF2563EB),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: _isSubmitting
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: Colors.white,
                        ),
                      )
                    : const Text(
                        '회원가입',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String? _requiredValidator(String? value) {
    if ((value?.trim() ?? '').isEmpty) {
      return '필수 입력 항목입니다.';
    }

    return null;
  }
}

class _SignupTextField extends StatelessWidget {
  const _SignupTextField({
    required this.controller,
    required this.label,
    this.hintText,
    this.prefixIcon,
    this.suffixIcon,
    this.keyboardType,
    this.obscureText = false,
    this.readOnly = false,
    this.maxLines = 1,
    this.onTap,
    this.validator,
  });

  final TextEditingController controller;
  final String label;
  final String? hintText;
  final IconData? prefixIcon;
  final Widget? suffixIcon;
  final TextInputType? keyboardType;
  final bool obscureText;
  final bool readOnly;
  final int maxLines;
  final VoidCallback? onTap;
  final String? Function(String?)? validator;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      readOnly: readOnly,
      maxLines: obscureText ? 1 : maxLines,
      onTap: onTap,
      validator: validator,
      decoration: _inputDecoration(
        label: label,
        hintText: hintText,
        prefixIcon: prefixIcon,
        suffixIcon: suffixIcon,
      ),
    );
  }
}

InputDecoration _inputDecoration({
  required String label,
  String? hintText,
  IconData? prefixIcon,
  Widget? suffixIcon,
}) {
  return InputDecoration(
    labelText: label,
    hintText: hintText,
    prefixIcon: prefixIcon == null
        ? null
        : Icon(prefixIcon, color: const Color(0xFF64748B)),
    suffixIcon: suffixIcon,
    filled: true,
    fillColor: Colors.white,
    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 17),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(color: Color(0xFFD8DEE9)),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(color: Color(0xFFD8DEE9)),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
    ),
    errorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(color: Color(0xFFDC2626)),
    ),
    focusedErrorBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(color: Color(0xFFDC2626), width: 1.5),
    ),
  );
}
