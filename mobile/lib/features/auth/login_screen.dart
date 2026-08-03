import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:go_router/go_router.dart';

import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/shared/mock/clinician_mock.dart';
import 'package:brainon_mobile/shared/mock/hospital_mock.dart';
import 'package:flutter/material.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({required this.role, super.key});

  /// 역할 선택 화면에서 전달받은 사용자 역할
  ///
  /// patient   → 환자 로그인 폼
  /// clinician → 의료진 로그인 폼
  final UserRole role;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
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

  /// 현재 화면이 의료진 로그인 화면인지 확인
  bool get _isClinician => widget.role == UserRole.clinician;

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

    // 실제 Django 로그인 API가 아직 연결되지 않았으므로
    // 서버 요청처럼 보이도록 임시 지연 시간을 준다.
    await Future<void>.delayed(const Duration(milliseconds: 700));

    if (!mounted) {
      return;
    }

    setState(() {
      _isSubmitting = false;
    });

    if (_isClinician) {
      context.goNamed(RouteNames.home); //로그인되는지 임시 확인
      // ----------------------------------------------------------
      // 의료진 로그인 임시 확인
      //
      // 실제 API 연결 후에는 이 SnackBar 대신
      // authProvider 또는 AuthRepository의 login을 호출한다.
      // ----------------------------------------------------------
      // ScaffoldMessenger.of(context).showSnackBar(
      //   SnackBar(
      //     content: Text(
      //       '의료진 로그인 입력 확인 완료\n'
      //       '직군 코드: $_selectedDepartmentCode\n'
      //       '병원: $_selectedHospitalName\n'
      //       '병원 ID: $_selectedHospitalId\n'
      //       '면허번호: ${_licenseNumberController.text.trim()}',
      //     ),
      //   ),
      // );
      // return;
    }

    // 환자 로그인 임시 확인
    context.goNamed(RouteNames.home); //로그인되는지 확인하기 위한 임시!
    // ScaffoldMessenger.of(
    //   context,
    // ).showSnackBar(const SnackBar(content: Text('환자 로그인 입력 확인이 완료되었습니다.')));
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
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('비밀번호 찾기 화면은 다음 단계에서 구현합니다.'),
                        ),
                      );
                    },
                    child: const Text('비밀번호를 잊으셨나요?'),
                  ),
                ),

                const SizedBox(height: 16),

                // ==================================================
                // 로그인 버튼
                // ==================================================
                _buildLoginButton(),

                // 의료진 화면에서만 보안 안내 표시
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

  Widget _buildDepartmentField(){
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

          // clinician_mock.dart의 데이터를 Dropdown 항목으로 변환한다.
          items: clinicianTypeMockList.map((item) {
            final code = item['code']!;
            final label = item['label']!;

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

        Autocomplete<Map<String, String>>(
          // 사용자가 입력한 검색어와 일치하는 병원을 반환한다.
          optionsBuilder: (textEditingValue) {
            final keyword = textEditingValue.text.trim().toLowerCase();

            if (keyword.isEmpty) {
              return const Iterable<Map<String, String>>.empty();
            }

            return hospitalMockList.where((hospital) {
              final hospitalName =
                  hospital['hospital_name']?.toLowerCase() ?? '';

              return hospitalName.contains(keyword);
            });
          },

          // 입력창에 표시할 값은 hospital_name이다.
          displayStringForOption: (hospital) {
            return hospital['hospital_name'] ?? '';
          },

          // 사용자가 추천 목록에서 병원을 선택했을 때 실행된다.
          onSelected: (hospital) {
            setState(() {
              _selectedHospitalId = hospital['hospital_id'];
              _selectedHospitalName = hospital['hospital_name'] ?? '';
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
                      final hospitalName = hospital['hospital_name'] ?? '';

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
