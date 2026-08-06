import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_profile_screens.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ClinicianMyPageScreen extends ConsumerWidget {
  const ClinicianMyPageScreen({required this.onOpenDrawer, super.key});

  final VoidCallback onOpenDrawer;

  static const _danger = Color(0xFFE34255);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider).user;
    final clinician = user?.role == UserRole.clinician ? user?.clinician : null;
    final name = _valueOrDash(clinician?.name);
    final department = _valueOrDash(clinician?.departmentName);
    final hospital = _valueOrDash(clinician?.hospitalName);
    final approvalStatus = _valueOrDash(clinician?.approvalStatus);

    Future<void> open(Widget screen) {
      return Navigator.of(
        context,
      ).push<void>(MaterialPageRoute<void>(builder: (_) => screen));
    }

    return ClinicianPageScaffold(
      title: '마이 페이지',
      onOpenDrawer: onOpenDrawer,
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 10, 20, 28),
        children: [
          ClinicianSectionCard(
            margin: const EdgeInsets.only(bottom: 16),
            padding: const EdgeInsets.all(20),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 72,
                  height: 72,
                  decoration: const BoxDecoration(
                    color: Color(0xFFE7F0FF),
                    shape: BoxShape.circle,
                  ),
                  alignment: Alignment.center,
                  child: const Icon(
                    Icons.person_rounded,
                    size: 40,
                    color: ClinicianUiColors.primary,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        name,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: ClinicianUiColors.text,
                          fontSize: 21,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        department,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: ClinicianUiColors.primary,
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          const Icon(
                            Icons.local_hospital_outlined,
                            size: 15,
                            color: ClinicianUiColors.mutedText,
                          ),
                          const SizedBox(width: 5),
                          Expanded(
                            child: Text(
                              hospital,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                color: ClinicianUiColors.mutedText,
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      ClinicianStatusBadge(
                        label: approvalStatus,
                        tone: _approvalTone(approvalStatus),
                        icon: Icons.verified_user_outlined,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          ClinicianSectionCard(
            margin: const EdgeInsets.only(bottom: 16),
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                ClinicianSettingsTile(
                  icon: Icons.badge_outlined,
                  title: '내 정보 관리',
                  onTap: () => open(const ClinicianAccountScreen()),
                ),
                ClinicianSettingsTile(
                  icon: Icons.local_hospital_outlined,
                  title: '근무 병원 정보',
                  onTap: () => open(const ClinicianHospitalInfoScreen()),
                ),
                ClinicianSettingsTile(
                  icon: Icons.notifications_outlined,
                  title: '알림 설정',
                  onTap: () =>
                      open(const ClinicianNotificationSettingsScreen()),
                ),
                ClinicianSettingsTile(
                  icon: Icons.lock_outline_rounded,
                  title: '비밀번호 변경',
                  onTap: () => open(const ClinicianPasswordChangeScreen()),
                ),
                ClinicianSettingsTile(
                  icon: Icons.info_outline_rounded,
                  title: '버전 정보',
                  showDivider: false,
                  onTap: () => open(const ClinicianVersionInfoScreen()),
                ),
              ],
            ),
          ),
          ClinicianSectionCard(
            margin: EdgeInsets.zero,
            padding: EdgeInsets.zero,
            child: ClinicianSettingsTile(
              icon: Icons.logout_rounded,
              title: '로그아웃',
              iconColor: _danger,
              iconBackgroundColor: const Color(0xFFFFE7EA),
              titleColor: _danger,
              showDivider: false,
              onTap: () => _confirmLogout(context, ref),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _confirmLogout(BuildContext context, WidgetRef ref) async {
    final shouldLogout =
        await showDialog<bool>(
          context: context,
          builder: (dialogContext) {
            return AlertDialog(
              title: const Text('로그아웃'),
              content: const Text('정말 로그아웃하시겠습니까?'),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(dialogContext).pop(false),
                  child: const Text('취소'),
                ),
                FilledButton(
                  onPressed: () => Navigator.of(dialogContext).pop(true),
                  style: FilledButton.styleFrom(backgroundColor: _danger),
                  child: const Text('로그아웃'),
                ),
              ],
            );
          },
        ) ??
        false;

    if (!shouldLogout || !context.mounted) {
      return;
    }

    await ref.read(authProvider.notifier).logout();

    if (!context.mounted) {
      return;
    }

    context.goNamed(RouteNames.roleSelection);
  }
}

String _valueOrDash(String? value) {
  final trimmed = value?.trim() ?? '';
  return trimmed.isEmpty ? '-' : trimmed;
}

ClinicianStatusTone _approvalTone(String status) =>
    switch (status.toUpperCase()) {
      'APPROVED' => ClinicianStatusTone.success,
      'PENDING' || 'PENDING_APPROVAL' => ClinicianStatusTone.warning,
      'REJECTED' || 'SUSPENDED' => ClinicianStatusTone.danger,
      _ => ClinicianStatusTone.neutral,
    };
