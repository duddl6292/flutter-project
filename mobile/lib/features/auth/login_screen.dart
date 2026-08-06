import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/core/auth/auth_state.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart';
import 'package:go_router/go_router.dart';

import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:flutter/material.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({required this.role, super.key});

  /// 역할 선택 화면에서 전달받은 사용자 역할
  ///
  /// patient   → 환자 로그인 폼
  /// clinician → 의료진 로그인 폼
  final UserRole role;

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  // ============================================================
  // 개발용 임시 로그인 우회 설정
  //
  // true:
  //   로그인 API를 호출하지 않고 환자/의료진 메인 화면으로 이동한다.
  //
  // false:
  //   아래 _submit()의 실제 로그인 API 코드를 실행한다.
  //
  // 실제 Django 로그인 API 연결이 완료되면 false로 변경한다.
  // ============================================================
  static const bool _enableDevelopmentLoginBypass = true;
  // ============================================================
  // Form 및 입력 Controller
  // ============================================================

  final _formKey = GlobalKey<FormState>();

  /// 환자 로그인용 아이디 입력값
  ///
  /// 의료진 로그인에서는 사용하지 않는다.
  final _usernameController = TextEditingController();

  /// 환자·의료진 공통 비밀번호
  final _passwordController = TextEditingController();

  /// 의료진 개인 면허번호
  final _licenseNumberController = TextEditingController();

  // ============================================================
  // 로그인 화면 상태
  // ============================================================

  /// 비밀번호 보이기/숨기기
  bool _obscurePassword = true;

  /// 로그인 버튼 처리 중 여부
  bool _isSubmitting = false;

  /// 의료진이 선택한 D/R/P 코드
  String? _selectedDepartmentCode;

  /// 의료진이 선택한 병원 ID
  ///
  /// 병원명을 직접 입력하는 것과 실제 병원을 선택하는 것을 구분하기 위해
  /// 이름과 ID를 별도로 관리한다.
  String? _selectedHospitalId;

  /// 화면에 표시하거나 임시 검증에 사용할 병원명
  String _selectedHospitalName = '';

  List<AuthHospital> _hospitals = const [];
  List<AuthDepartment> _departments = const [];

  /// 현재 화면이 의료진 로그인 화면인지 확인
  bool get _isClinician => widget.role == UserRole.clinician;

  @override
  void initState() {
    super.initState();
    if (_isClinician) {
      Future<void>.microtask(_loadClinicianLoginOptions);
    }
  }

  Future<void> _loadClinicianLoginOptions() async {
    try {
      final repository = ref.read(authRepositoryProvider);
      final results = await Future.wait([
        repository.getHospitals(),
        repository.getDepartments(),
      ]);
      if (!mounted) {
        return;
      }
      setState(() {
        _hospitals = results[0] as List<AuthHospital>;
        _departments = results[1] as List<AuthDepartment>;
      });
    } on Object catch (error) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error.toString())));
    }
  }

  @override
  void dispose() {
    // TextEditingController는 화면이 제거될 때 반드시 dispose한다.
    _usernameController.dispose();
    _passwordController.dispose();
    _licenseNumberController.dispose();
    super.dispose();
  }

  // ============================================================
  // 로그인 버튼 동작
  // ============================================================

  Future<void> _submit() async {
    // 키보드 완료와 로그인 버튼이 거의 동시에 실행되더라도
    // 진행 중인 로그인 요청이 있으면 같은 요청을 다시 보내지 않는다.
    if (_isSubmitting) {
      return;
    }

    // ==========================================================
    // 1. 개발용 임시 로그인 우회
    //
    // 현재 로그인 API가 연결되지 않은 동안 사용하는 코드다.
    // 입력값 검증과 API 요청 없이 역할에 맞는 임시 인증 상태를 만들고,
    // 환자는 환자 메인, 의료진은 의료진 메인으로 이동한다.
    //
    // 실제 API 연결 후에는:
    //   _enableDevelopmentLoginBypass = false
    // 로 바꾸면 아래 실제 로그인 코드가 다시 실행된다.
    // ==========================================================
    if (kDebugMode && _enableDevelopmentLoginBypass) {
      if (_isClinician) {
        // 의료진 임시 인증 상태 생성
        ref.read(authProvider.notifier).startDevelopmentClinicianSession();

        if (!mounted) {
          return;
        }

        // 의료진 메인 화면으로 이동
        context.goNamed(RouteNames.clinicianHome);
        return;
      }

      // 환자 임시 인증 상태 생성
      ref.read(authProvider.notifier).startDevelopmentPatientSession();

      if (!mounted) {
        return;
      }

      // 환자 메인 화면으로 이동
      context.goNamed(RouteNames.patientMain);
      return;
    }

    // ==========================================================
    // 2. 실제 로그인 API 처리
    //
    // 개발용 우회 설정이 false일 때만 실행된다.
    // 이 코드는 삭제하지 않고 그대로 보관한다.
    // ==========================================================

    // TextFormField와 Dropdown의 validator를 실행한다.
    final isFormValid = _formKey.currentState?.validate() ?? false;

    if (!isFormValid) {
      return;
    }

    // 의료진은 자동추천 목록에서 병원을 실제로 선택해야 한다.
    if (_isClinician && _selectedHospitalId == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('자동추천 목록에서 병원을 선택해주세요.')));
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      // 실제 Django 로그인 API 호출
      await ref
          .read(authProvider.notifier)
          .login(
            role: widget.role,
            password: _passwordController.text,
            username: _isClinician ? null : _usernameController.text.trim(),
            hospitalId: _selectedHospitalId,
            departmentCode: _selectedDepartmentCode,
            licenseNumber: _licenseNumberController.text.trim(),
          );

      if (!mounted) {
        return;
      }

      // 인증 상태 변경을 감지한 GoRouter가 역할에 맞는 메인 화면으로 이동한다.
      // 여기서 다시 이동하면 특히 환자 로그인 시 화면 전환이 중복될 수 있다.
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
      backgroundColor: const Color(0xFFF7F9FC),

      // ==========================================================
      // 상단 AppBar
      // ==========================================================
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(_isClinician ? '의료진 로그인' : '환자 로그인'),
      ),

      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 32),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // ==================================================
                // BrainOn 로고 영역
                // ==================================================
                _buildLogoSection(),

                const SizedBox(height: 32),

                // ==================================================
                // 화면 제목
                // ==================================================
                Text(
                  _isClinician ? '의료진 계정으로 로그인' : '환자 계정으로 로그인',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 21,
                    fontWeight: FontWeight.w700,
                  ),
                ),

                const SizedBox(height: 8),

                Text(
                  _isClinician
                      ? '의료진 인증을 위해 아래 정보를 입력해주세요.'
                      : '아이디와 비밀번호를 입력해주세요.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    color: Color(0xFF6B7280),
                    fontSize: 14,
                  ),
                ),

                const SizedBox(height: 32),

                // ==================================================
                // 의료진 전용 입력 필드
                // ==================================================
                if (_isClinician) ...[
                  _buildDepartmentField(),
                  const SizedBox(height: 20),

                  _buildHospitalSearchField(),
                  const SizedBox(height: 20),

                  _buildLicenseNumberField(),
                  const SizedBox(height: 20),
                ],

                // ==================================================
                // 환자 전용 아이디 입력 필드
                // ==================================================
                if (!_isClinician) ...[
                  _buildPatientUsernameField(),
                  const SizedBox(height: 16),
                ],

                // ==================================================
                // 환자·의료진 공통 비밀번호
                // ==================================================
                if (_isClinician) const _FieldLabel('비밀번호'),

                _buildPasswordField(),

                const SizedBox(height: 8),

                // 비밀번호 찾기
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: () {
                      context.pushNamed(RouteNames.forgotPassword);
                    },
                    child: const Text('비밀번호를 잊으셨나요?'),
                  ),
                ),

                const SizedBox(height: 16),

                const SizedBox(height: 16),

                // ==================================================
                // 로그인 버튼
                // ==================================================
                _buildLoginButton(),

                // ==================================================
                // 환자 로그인 화면에서만 회원가입 표시
                // ==================================================
                if (!_isClinician) ...[
                  const SizedBox(height: 12),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text(
                        '계정이 없으신가요?',
                        style: TextStyle(color: Color(0xFF6B7280)),
                      ),
                      TextButton(
                        onPressed: () {
                          context.pushNamed(RouteNames.patientSignup);
                        },
                        child: const Text(
                          '회원가입',
                          style: TextStyle(
                            color: Color(0xFF2563EB),
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],

                // ==================================================
                // 의료진 로그인 화면에서만 보안 안내 표시
                // ==================================================
                if (_isClinician) ...[
                  const SizedBox(height: 24),
                  _buildSecurityNotice(),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ==============================================================
  // 로고 영역
  // ==============================================================

  Widget _buildLogoSection() {
    return Column(
      children: [
        // ==========================================================
        // 호닥 로고 이미지
        //
        // 이미지 위치:
        // mobile/assets/images/logo.png
        //
        // 이미지 크기는 width, height 값으로 조절
        // ==========================================================
        Image.asset(
          'assets/images/logo.png',
          width: 40,
          height: 40,
          fit: BoxFit.contain,
        ),

        const SizedBox(height: 12),

        // 로고 이미지에 '호닥' 글자까지 들어 있다면
        // 아래 Text 위젯은 삭제해도 된다.
        const Text(
          '호닥',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Color(0xFF1E3A8A),
            fontSize: 27,
            fontWeight: FontWeight.w800,
          ),
        ),
      ],
    );
  }

  // ==============================================================
  // 환자 아이디 입력
  // ==============================================================

  Widget _buildPatientUsernameField() {
    return TextFormField(
      controller: _usernameController,
      textInputAction: TextInputAction.next,
      decoration: _inputDecoration(
        hintText: '아이디',
        prefixIcon: Icons.person_outline,
      ),
      validator: (value) {
        if (value == null || value.trim().isEmpty) {
          return '아이디를 입력해주세요.';
        }

        return null;
      },
    );
  }

  // ==============================================================
  // 의료진 직군/진료과 선택
  // ==============================================================

  Widget _buildDepartmentField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const _FieldLabel('진료과 선택'),

        DropdownButtonFormField<String>(
          initialValue: _selectedDepartmentCode,
          decoration: _inputDecoration(
            hintText: '선택해주세요',
            prefixIcon: Icons.medical_services_outlined,
          ),

          // Django에서 조회한 활성 진료과를 Dropdown 항목으로 변환한다.
          items: _departments.map((item) {
            final code = item.code;
            final label = item.name;

            return DropdownMenuItem<String>(value: code, child: Text(label));
          }).toList(),

          onChanged: (value) {
            setState(() {
              _selectedDepartmentCode = value;
            });
          },

          validator: (value) {
            if (value == null || value.isEmpty) {
              return '진료과를 선택해주세요.';
            }

            return null;
          },
        ),
      ],
    );
  }

  // ==============================================================
  // 의료진 병원 검색 및 자동추천
  // ==============================================================

  Widget _buildHospitalSearchField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const _FieldLabel('병원 검색'),

        Autocomplete<AuthHospital>(
          // 사용자가 입력한 검색어와 일치하는 병원을 반환한다.
          optionsBuilder: (TextEditingValue textEditingValue) {
            if (textEditingValue.text.trim().isEmpty) {
              return const Iterable<AuthHospital>.empty();
            }

            final keyword = textEditingValue.text.trim().toLowerCase();

            return _hospitals.where((hospital) {
              return hospital.name.toLowerCase().contains(keyword);
            });
          },

          // 입력창에 표시할 값은 hospital_name이다.
          displayStringForOption: (hospital) {
            return hospital.name;
          },

          // 사용자가 추천 목록에서 병원을 선택했을 때 실행된다.
          onSelected: (hospital) {
            setState(() {
              _selectedHospitalId = hospital.id;
              _selectedHospitalName = hospital.name;
            });
          },

          fieldViewBuilder: (context, controller, focusNode, onFieldSubmitted) {
            return TextFormField(
              controller: controller,
              focusNode: focusNode,
              textInputAction: TextInputAction.next,
              decoration: _inputDecoration(
                hintText: '병원명을 입력해주세요',
                prefixIcon: Icons.search,
              ),

              onChanged: (value) {
                // 사용자가 선택한 병원명을 다시 수정하면
                // 이전 병원 ID 선택을 해제한다.
                if (value != _selectedHospitalName) {
                  _selectedHospitalId = null;
                }

                _selectedHospitalName = value;
              },

              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '병원을 입력해주세요.';
                }

                return null;
              },
            );
          },

          optionsViewBuilder: (context, onSelected, options) {
            final optionList = options.toList();

            return Align(
              alignment: Alignment.topLeft,
              child: Material(
                elevation: 8,
                borderRadius: BorderRadius.circular(14),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(
                    maxHeight: 240,
                    maxWidth: 560,
                  ),
                  child: ListView.separated(
                    padding: EdgeInsets.zero,
                    shrinkWrap: true,
                    itemCount: optionList.length,
                    separatorBuilder: (_, _) {
                      return const Divider(height: 1);
                    },
                    itemBuilder: (context, index) {
                      final hospital = optionList[index];

                      final hospitalName = hospital.name;

                      return ListTile(
                        // --------------------------------------------------
                        // 병원 추천 목록의 아이콘을 바꾸려면
                        // 아래 Icon만 변경하면 된다.
                        //
                        // 예:
                        // Icons.apartment_outlined
                        // Icons.local_hospital_outlined
                        // --------------------------------------------------
                        leading: const Icon(
                          Icons.local_hospital_outlined,
                          color: Color(0xFF2563EB),
                        ),
                        title: Text(hospitalName),
                        onTap: () {
                          onSelected(hospital);
                        },
                      );
                    },
                  ),
                ),
              ),
            );
          },
        ),
      ],
    );
  }

  // ==============================================================
  // 의료진 면허번호
  // ==============================================================

  Widget _buildLicenseNumberField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const _FieldLabel('개인 면허번호'),

        TextFormField(
          controller: _licenseNumberController,
          keyboardType: TextInputType.number,
          textInputAction: TextInputAction.next,
          decoration: _inputDecoration(
            hintText: '면허번호를 입력해주세요',
            prefixIcon: Icons.verified_user_outlined,
            helperText: '예) 12345',
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return '면허번호를 입력해주세요.';
            }

            return null;
          },
        ),
      ],
    );
  }

  // ==============================================================
  // 비밀번호 입력
  // ==============================================================

  Widget _buildPasswordField() {
    return TextFormField(
      controller: _passwordController,
      obscureText: _obscurePassword,
      onFieldSubmitted: (_) {
        if (!_isSubmitting) {
          _submit();
        }
      },
      decoration:
          _inputDecoration(
            hintText: _isClinician ? '비밀번호를 입력해주세요' : '비밀번호',
            prefixIcon: Icons.lock_outline,
          ).copyWith(
            suffixIcon: IconButton(
              onPressed: () {
                setState(() {
                  _obscurePassword = !_obscurePassword;
                });
              },
              tooltip: _obscurePassword ? '비밀번호 표시' : '비밀번호 숨기기',
              icon: Icon(
                _obscurePassword
                    ? Icons.visibility_outlined
                    : Icons.visibility_off_outlined,
              ),
            ),
          ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return '비밀번호를 입력해주세요.';
        }

        return null;
      },
    );
  }

  // ==============================================================
  // 로그인 버튼
  // ==============================================================

  Widget _buildLoginButton() {
    return SizedBox(
      height: 56,
      child: FilledButton(
        onPressed: _isSubmitting ? null : _submit,
        style: FilledButton.styleFrom(
          // --------------------------------------------------------
          // 로그인 버튼 색상을 바꾸려면 이 값을 변경한다.
          // --------------------------------------------------------
          backgroundColor: const Color(0xFF2563EB),

          shape: RoundedRectangleBorder(
            // 버튼 둥근 정도를 바꾸려면 아래 숫자를 조정한다.
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
                '로그인',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
              ),
      ),
    );
  }

  // ==============================================================
  // 의료진 보안 안내 카드
  // ==============================================================

  Widget _buildSecurityNotice() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        // 안내 카드 배경색
        color: const Color(0xFFEFF6FF),

        // 안내 카드 둥근 정도
        borderRadius: BorderRadius.circular(16),
      ),
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 안내 카드 아이콘을 바꾸려면 아래 Icon을 변경한다.
          Icon(Icons.security_outlined, color: Color(0xFF2563EB)),

          SizedBox(width: 12),

          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '안전하고 신뢰할 수 있는 의료 서비스',
                  style: TextStyle(
                    color: Color(0xFF1D4ED8),
                    fontWeight: FontWeight.w700,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'HODOC은 개인정보 보호와 보안을 '
                  '최우선으로 생각합니다.',
                  style: TextStyle(
                    color: Color(0xFF64748B),
                    fontSize: 13,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ==============================================================
  // 공통 입력창 디자인
  // ==============================================================

  InputDecoration _inputDecoration({
    required String hintText,
    required IconData prefixIcon,
    String? helperText,
  }) {
    return InputDecoration(
      hintText: hintText,
      helperText: helperText,
      prefixIcon: Icon(prefixIcon),

      // 입력창 배경
      filled: true,
      fillColor: Colors.white,

      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),

      border: OutlineInputBorder(
        // 모든 입력창의 둥근 정도를 변경하는 위치
        borderRadius: BorderRadius.circular(14),
      ),

      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(
          // 입력 전 테두리 색
          color: Color(0xFFCBD5E1),
        ),
      ),

      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(
          // 입력 중 테두리 색
          color: Color(0xFF2563EB),
          width: 2,
        ),
      ),

      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(color: Colors.red),
      ),
    );
  }
}

/// 의료진 로그인 입력 필드 위에 표시되는 제목 위젯
///
/// 예:
/// 직군/진료과 선택
/// 병원 검색
/// 개인 면허번호
class _FieldLabel extends StatelessWidget {
  const _FieldLabel(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        text,
        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
      ),
    );
  }
}
