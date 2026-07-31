import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class RoleSelectionScreen extends StatefulWidget {
  const RoleSelectionScreen({super.key});

  @override
  State<RoleSelectionScreen> createState() => _RoleSelectionScreenState();
}

class _RoleSelectionScreenState extends State<RoleSelectionScreen> {
  UserRole _selectedRole = UserRole.patient;

  @override
  Widget build(BuildContext context) {
    final isPatient = _selectedRole == UserRole.patient;
    //메인 화면 수정
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 20),
          child: Column(
            children: [
              const SizedBox(height: 12),
              Image.asset(
                'assets/images/logo.png',
                width: 90,
                height: 90,
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 8),
              const Text(
                '호닥',
                style: TextStyle(
                  color: Color(0xFF1E3A8A),
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 36),
              const Text(
                '로그인 유형을 선택해주세요',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 8),
              const Text(
                '서비스에 맞는 모드를 선택한 뒤 로그인하세요.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Color(0xFF6B7280), fontSize: 14),
              ),
              const SizedBox(height: 28),
              _RoleCard(
                title: '환자 모드',
                description: '진료 일정과 복약, 검사 결과를 확인합니다.',
                icon: Icons.medication_outlined,
                selected: isPatient,
                onTap: () {
                  setState(() {
                    _selectedRole = UserRole.patient;
                  });
                },
              ),
              const SizedBox(height: 16),
              _RoleCard(
                title: '의료진 모드',
                description: '예약, 환자 정보와 협진 업무를 확인합니다.',
                icon: Icons.medical_services_outlined,
                selected: !isPatient,
                onTap: () {
                  setState(() {
                    _selectedRole = UserRole.clinician;
                  });
                },
              ),
              const Spacer(),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: FilledButton(
                  onPressed: () {
                    context.pushNamed(RouteNames.login, extra: _selectedRole);
                  },
                  style: FilledButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Text(
                    '${_selectedRole.displayName} 모드로 계속하기',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                '호닥은 개인정보 보호와 보안을 중요하게 생각합니다.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Color(0xFF6B7280), fontSize: 12),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RoleCard extends StatelessWidget {
  const _RoleCard({
    required this.title,
    required this.description,
    required this.icon,
    required this.selected,
    required this.onTap,
  });

  final String title;
  final String description;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      selected: selected,
      label: '$title, ${selected ? '선택됨' : '선택되지 않음'}',
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: selected
                  ? const Color(0xFF2563EB)
                  : const Color(0xFFE5E7EB),
              width: selected ? 2 : 1,
            ),
            boxShadow: const [
              BoxShadow(
                color: Color(0x12000000),
                blurRadius: 16,
                offset: Offset(0, 6),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 62,
                height: 62,
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Icon(icon, size: 33, color: const Color(0xFF2563EB)),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 19,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      description,
                      style: const TextStyle(
                        color: Color(0xFF6B7280),
                        fontSize: 14,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              Icon(
                selected ? Icons.check_circle : Icons.radio_button_unchecked,
                color: selected
                    ? const Color(0xFF2563EB)
                    : const Color(0xFFCBD5E1),
                size: 28,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
