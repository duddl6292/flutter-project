import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/shared/models/patient_signup_request.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class PatientSignupScreen extends ConsumerStatefulWidget {
  const PatientSignupScreen({super.key});

  @override
  ConsumerState<PatientSignupScreen> createState() =>
      _PatientSignupScreenState();
}

class _PatientSignupScreenState extends ConsumerState<PatientSignupScreen> {
  final _formKey = GlobalKey<FormState>();

  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _passwordConfirmController = TextEditingController();

  final _patientNameController = TextEditingController();
  final _birthDateController = TextEditingController();

  String _selectedSex = 'UNKNOWN';

  bool _obscurePassword = true;
  bool _obscurePasswordConfirm = true;
  bool _agreePrivacy = false;
  bool _agreeSensitiveInfo = false;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _passwordConfirmController.dispose();
    _patientNameController.dispose();
    _birthDateController.dispose();

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
        passwordConfirm: _passwordConfirmController.text,
        name: _patientNameController.text.trim(),
        birthDate: _birthDateController.text.trim(),
        sex: _selectedSex,
      );

      await ref.read(authRepositoryProvider).signupPatient(request);

      if (!mounted) {
        return;
      }

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('회원가입이 완료되었습니다.')));

      Navigator.of(context).pop();
    } on Object catch (error) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(SnackBar(content: Text(error.toString())));
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

              const SizedBox(height: 20),

              _SignupTextField(
                controller: _patientNameController,
                label: '환자 이름',
                hintText: '이름 입력',
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
    this.obscureText = false,
    this.readOnly = false,
    this.onTap,
    this.validator,
  });

  final TextEditingController controller;
  final String label;
  final String? hintText;
  final IconData? prefixIcon;
  final Widget? suffixIcon;
  final bool obscureText;
  final bool readOnly;
  final VoidCallback? onTap;
  final String? Function(String?)? validator;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      obscureText: obscureText,
      readOnly: readOnly,
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
