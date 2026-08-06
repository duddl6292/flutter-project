import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_profile_screens.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_tab_header.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianMyPageScreen extends ConsumerWidget {
  const ClinicianMyPageScreen({required this.onOpenDrawer, super.key});
  final VoidCallback onOpenDrawer;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider).user;
    final clinician = user?.role == UserRole.clinician ? user?.clinician : null;
    final name = clinician?.name ?? '이현우';
    final department = clinician?.departmentName ?? '신경과';
    final hospital = clinician?.hospitalName.isNotEmpty == true
        ? clinician!.hospitalName
        : '등록된 병원 없음';

    Future<void> open(Widget screen) {
      return Navigator.of(
        context,
      ).push<void>(MaterialPageRoute<void>(builder: (_) => screen));
    }

    return ColoredBox(
      color: const Color(0xFFF6F8FC),
      child: SafeArea(
        bottom: false,
        child: Column(
          children: [
            ClinicianTabHeader(title: '마이 페이지', onOpenDrawer: onOpenDrawer),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(20, 10, 20, 28),
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(color: const Color(0xFFE5EAF2)),
                    ),
                    child: Row(
                      children: [
                        const CircleAvatar(
                          radius: 32,
                          backgroundColor: Color(0xFFEAF2FA),
                          child: Icon(
                            Icons.person_rounded,
                            size: 38,
                            color: Color(0xFF28669E),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                name,
                                style: const TextStyle(
                                  fontSize: 19,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                department,
                                style: const TextStyle(
                                  color: Color(0xFF28669E),
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              const SizedBox(height: 3),
                              Text(
                                hospital,
                                style: const TextStyle(
                                  color: Color(0xFF6B7280),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 18),
                  Material(
                    color: Colors.white,
                    clipBehavior: Clip.antiAlias,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(18),
                      side: const BorderSide(color: Color(0xFFE5EAF2)),
                    ),
                    child: Column(
                      children: [
                        _SettingTile(
                          icon: Icons.badge_outlined,
                          title: '내 정보 관리',
                          onTap: () => open(const ClinicianAccountScreen()),
                        ),
                        _SettingTile(
                          icon: Icons.local_hospital_outlined,
                          title: '근무 병원 정보',
                          onTap: () =>
                              open(const ClinicianHospitalInfoScreen()),
                        ),
                        _SettingTile(
                          icon: Icons.notifications_outlined,
                          title: '알림 설정',
                          onTap: () => open(
                            const ClinicianNotificationSettingsScreen(),
                          ),
                        ),
                        _SettingTile(
                          icon: Icons.lock_outline_rounded,
                          title: '비밀번호 변경',
                          onTap: () =>
                              open(const ClinicianPasswordChangeScreen()),
                        ),
                        _SettingTile(
                          icon: Icons.info_outline_rounded,
                          title: '버전 정보',
                          trailing: '1.0.0',
                          onTap: () =>
                              open(const ClinicianVersionInfoScreen()),
                          showDivider: false,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SettingTile extends StatelessWidget {
  const _SettingTile({
    required this.icon,
    required this.title,
    required this.onTap,
    this.trailing,
    this.showDivider = true,
  });
  final IconData icon;
  final String title;
  final VoidCallback onTap;
  final String? trailing;
  final bool showDivider;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Material(
          color: Colors.transparent,
          child: ListTile(
            onTap: onTap,
            leading: Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                color: const Color(0xFFEAF2FA),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: const Color(0xFF28669E), size: 21),
            ),
            title: Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            trailing: trailing == null
                ? const Icon(Icons.chevron_right_rounded)
                : Text(
                    trailing!,
                    style: const TextStyle(color: Color(0xFF6B7280)),
                  ),
          ),
        ),
        if (showDivider)
          const Divider(height: 1, indent: 68, color: Color(0xFFE5EAF2)),
      ],
    );
  }
}
