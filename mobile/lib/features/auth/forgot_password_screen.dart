import 'package:flutter/material.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();

  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _verificationCodeController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _newPasswordConfirmController = TextEditingController();

  bool _isCodeSent = false;
  bool _isVerified = false;
  bool _isSendingCode = false;
  bool _isVerifyingCode = false;
  bool _isChangingPassword = false;

  bool _obscureNewPassword = true;
  bool _obscureNewPasswordConfirm = true;

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _verificationCodeController.dispose();
    _newPasswordController.dispose();
    _newPasswordConfirmController.dispose();
    super.dispose();
  }

  Future<void> _sendVerificationCode() async {
    FocusScope.of(context).unfocus();

    final username = _usernameController.text.trim();
    final email = _emailController.text.trim();

    if (username.isEmpty) {
      _showMessage('아이디를 입력해 주세요.');
      return;
    }

    if (email.isEmpty || !email.contains('@')) {
      _showMessage('올바른 이메일을 입력해 주세요.');
      return;
    }

    setState(() {
      _isSendingCode = true;
    });

    try {
      // TODO: Django 인증번호 발송 API 연결
      await Future<void>.delayed(const Duration(milliseconds: 700));

      if (!mounted) {
        return;
      }

      setState(() {
        _isCodeSent = true;
        _isVerified = false;
      });

      _showMessage('인증번호가 발송되었습니다.');
    } finally {
      if (mounted) {
        setState(() {
          _isSendingCode = false;
        });
      }
    }
  }

  Future<void> _verifyCode() async {
    FocusScope.of(context).unfocus();

    final code = _verificationCodeController.text.trim();

    if (code.isEmpty) {
      _showMessage('인증번호를 입력해 주세요.');
      return;
    }

    setState(() {
      _isVerifyingCode = true;
    });

    try {
      // TODO: Django 인증번호 확인 API 연결
      await Future<void>.delayed(const Duration(milliseconds: 600));

      if (!mounted) {
        return;
      }

      if (code != '123456') {
        _showMessage('인증번호가 올바르지 않습니다.');
        return;
      }

      setState(() {
        _isVerified = true;
      });

      _showMessage('인증이 완료되었습니다.');
    } finally {
      if (mounted) {
        setState(() {
          _isVerifyingCode = false;
        });
      }
    }
  }

  Future<void> _changePassword() async {
    FocusScope.of(context).unfocus();

    if (!_isVerified) {
      _showMessage('먼저 인증을 완료해 주세요.');
      return;
    }

    if (!(_formKey.currentState?.validate() ?? false)) {
      return;
    }

    setState(() {
      _isChangingPassword = true;
    });

    try {
      // TODO: Django 비밀번호 변경 API 연결
      await Future<void>.delayed(const Duration(milliseconds: 800));

      if (!mounted) {
        return;
      }

      _showMessage('비밀번호가 변경되었습니다.');

      await Future<void>.delayed(const Duration(milliseconds: 400));

      if (mounted) {
        Navigator.of(context).pop();
      }
    } finally {
      if (mounted) {
        setState(() {
          _isChangingPassword = false;
        });
      }
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        elevation: 0,
        title: const Text(
          '비밀번호 찾기',
          style: TextStyle(
            color: Color(0xFF111827),
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
              const Icon(
                Icons.lock_reset_outlined,
                size: 56,
                color: Color(0xFF2563EB),
              ),
              const SizedBox(height: 16),
              const Text(
                '비밀번호를 재설정해요',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Color(0xFF111827),
                  fontSize: 23,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                '가입할 때 사용한 아이디와 이메일을 입력해 주세요.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Color(0xFF6B7280),
                  fontSize: 14,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 32),

              _SectionCard(
                title: '계정 확인',
                child: Column(
                  children: [
                    _ForgotPasswordField(
                      controller: _usernameController,
                      label: '아이디',
                      hintText: '아이디를 입력해 주세요.',
                      prefixIcon: Icons.person_outline,
                      enabled: !_isVerified,
                    ),
                    const SizedBox(height: 14),
                    _ForgotPasswordField(
                      controller: _emailController,
                      label: '이메일',
                      hintText: 'example@email.com',
                      prefixIcon: Icons.email_outlined,
                      keyboardType: TextInputType.emailAddress,
                      enabled: !_isVerified,
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      height: 52,
                      child: OutlinedButton(
                        onPressed: _isSendingCode || _isVerified
                            ? null
                            : _sendVerificationCode,
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFF2563EB),
                          side: const BorderSide(color: Color(0xFF2563EB)),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                        child: _isSendingCode
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.2,
                                ),
                              )
                            : Text(
                                _isCodeSent ? '인증번호 다시 받기' : '인증번호 받기',
                                style: const TextStyle(
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                      ),
                    ),
                  ],
                ),
              ),

              if (_isCodeSent) ...[
                const SizedBox(height: 18),
                _SectionCard(
                  title: '이메일 인증',
                  child: Column(
                    children: [
                      _ForgotPasswordField(
                        controller: _verificationCodeController,
                        label: '인증번호',
                        hintText: '6자리 인증번호',
                        prefixIcon: Icons.verified_outlined,
                        keyboardType: TextInputType.number,
                        enabled: !_isVerified,
                      ),
                      const SizedBox(height: 8),
                      const Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          '테스트 인증번호: 123456',
                          style: TextStyle(
                            color: Color(0xFF6B7280),
                            fontSize: 12,
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        height: 52,
                        child: FilledButton(
                          onPressed: _isVerifyingCode || _isVerified
                              ? null
                              : _verifyCode,
                          style: FilledButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                            ),
                          ),
                          child: _isVerifyingCode
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2.2,
                                  ),
                                )
                              : Text(
                                  _isVerified ? '인증 완료' : '인증 확인',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              if (_isVerified) ...[
                const SizedBox(height: 18),
                _SectionCard(
                  title: '새 비밀번호 설정',
                  child: Column(
                    children: [
                      _ForgotPasswordField(
                        controller: _newPasswordController,
                        label: '새 비밀번호',
                        hintText: '8자 이상 입력해 주세요.',
                        prefixIcon: Icons.lock_outline,
                        obscureText: _obscureNewPassword,
                        suffixIcon: IconButton(
                          onPressed: () {
                            setState(() {
                              _obscureNewPassword = !_obscureNewPassword;
                            });
                          },
                          icon: Icon(
                            _obscureNewPassword
                                ? Icons.visibility_off_outlined
                                : Icons.visibility_outlined,
                          ),
                        ),
                        validator: (value) {
                          final text = value ?? '';

                          if (text.isEmpty) {
                            return '새 비밀번호를 입력해 주세요.';
                          }

                          if (text.length < 8) {
                            return '비밀번호는 8자 이상이어야 합니다.';
                          }

                          return null;
                        },
                      ),
                      const SizedBox(height: 14),
                      _ForgotPasswordField(
                        controller: _newPasswordConfirmController,
                        label: '새 비밀번호 확인',
                        hintText: '비밀번호를 다시 입력해 주세요.',
                        prefixIcon: Icons.lock_reset_outlined,
                        obscureText: _obscureNewPasswordConfirm,
                        suffixIcon: IconButton(
                          onPressed: () {
                            setState(() {
                              _obscureNewPasswordConfirm =
                                  !_obscureNewPasswordConfirm;
                            });
                          },
                          icon: Icon(
                            _obscureNewPasswordConfirm
                                ? Icons.visibility_off_outlined
                                : Icons.visibility_outlined,
                          ),
                        ),
                        validator: (value) {
                          if ((value ?? '').isEmpty) {
                            return '비밀번호 확인을 입력해 주세요.';
                          }

                          if (value != _newPasswordController.text) {
                            return '비밀번호가 일치하지 않습니다.';
                          }

                          return null;
                        },
                      ),
                      const SizedBox(height: 20),
                      SizedBox(
                        width: double.infinity,
                        height: 56,
                        child: FilledButton(
                          onPressed: _isChangingPassword
                              ? null
                              : _changePassword,
                          style: FilledButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                          ),
                          child: _isChangingPassword
                              ? const SizedBox(
                                  width: 22,
                                  height: 22,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2.4,
                                  ),
                                )
                              : const Text(
                                  '비밀번호 변경',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE5E7EB)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D000000),
            blurRadius: 18,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: Color(0xFF111827),
              fontSize: 18,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 18),
          child,
        ],
      ),
    );
  }
}

class _ForgotPasswordField extends StatelessWidget {
  const _ForgotPasswordField({
    required this.controller,
    required this.label,
    required this.hintText,
    required this.prefixIcon,
    this.keyboardType,
    this.obscureText = false,
    this.enabled = true,
    this.suffixIcon,
    this.validator,
  });

  final TextEditingController controller;
  final String label;
  final String hintText;
  final IconData prefixIcon;
  final TextInputType? keyboardType;
  final bool obscureText;
  final bool enabled;
  final Widget? suffixIcon;
  final String? Function(String?)? validator;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      enabled: enabled,
      validator: validator,
      decoration: InputDecoration(
        labelText: label,
        hintText: hintText,
        prefixIcon: Icon(prefixIcon, color: const Color(0xFF64748B)),
        suffixIcon: suffixIcon,
        filled: true,
        fillColor: enabled ? Colors.white : const Color(0xFFF1F5F9),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 17,
        ),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
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
      ),
    );
  }
}
