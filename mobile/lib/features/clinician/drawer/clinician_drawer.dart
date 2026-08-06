import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/clinician_feature_navigation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

/// 의료진 앱의 햄버거 메뉴.
///
/// [onSelectTab]에는 `clinician_main_screen.dart`의 하단 탭 변경 함수를 전달한다.
///
/// 현재 탭 인덱스 기준:
/// 0: 환자
/// 1: 일정
/// 2: 홈
/// 3: 협진
/// 4: 마이
class ClinicianDrawer extends ConsumerWidget {
  const ClinicianDrawer({required this.onSelectTab, super.key});

  final ValueChanged<int> onSelectTab;

  static const _primary = Color(0xFF28669E);
  static const _text = Color(0xFF111827);
  static const _secondaryText = Color(0xFF6B7280);
  static const _border = Color(0xFFE5EAF2);
  static const _danger = Color(0xFFE34255);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final clinician = authState.user?.clinician;

    final clinicianName = clinician?.name.trim().isNotEmpty == true
        ? clinician!.name
        : '이현우';

    final departmentName = clinician?.departmentName.trim().isNotEmpty == true
        ? clinician!.departmentName
        : '신경과';

    return Drawer(
      width: MediaQuery.sizeOf(context).width * 0.82,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.horizontal(right: Radius.circular(22)),
      ),
      child: SafeArea(
        child: Column(
          children: [
            _buildHeader(
              context,
              clinicianName: clinicianName,
              departmentName: departmentName,
            ),
            const Divider(height: 1, color: _border),

            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(12, 10, 12, 16),
                children: [
                  _DrawerMenuItem(
                    icon: Icons.notifications_none_rounded,
                    title: '알림센터',
                    badgeCount: 3,
                    onTap: () {
                      _openFeature(
                        context,
                        ClinicianFeatureNavigation.notifications,
                      );
                    },
                  ),
                  const Divider(height: 24, color: _border),

                  const _DrawerSectionTitle('업무'),

                  _DrawerMenuItem(
                    icon: Icons.search_rounded,
                    title: '환자 검색',
                    onTap: () {
                      _moveToTab(context, 0);
                    },
                  ),
                  _DrawerMenuItem(
                    icon: Icons.science_outlined,
                    title: '검사 결과 관리',
                    onTap: () {
                      _openFeature(
                        context,
                        ClinicianFeatureNavigation.testResults,
                      );
                    },
                  ),
                  _DrawerMenuItem(
                    icon: Icons.medication_outlined,
                    title: '처방 관리',
                    onTap: () {
                      _openFeature(
                        context,
                        ClinicianFeatureNavigation.prescriptions,
                      );
                    },
                  ),
                  _DrawerMenuItem(
                    icon: Icons.description_outlined,
                    title: '진료 기록',
                    onTap: () {
                      _openFeature(context, ClinicianFeatureNavigation.records);
                    },
                  ),
                  _DrawerMenuItem(
                    icon: Icons.psychology_alt_outlined,
                    title: 'AI 분석',
                    onTap: () {
                      _openFeature(
                        context,
                        ClinicianFeatureNavigation.aiAnalysis,
                      );
                    },
                  ),
                  const Divider(height: 24, color: _border),

                  const _DrawerSectionTitle('서비스'),

                  _DrawerMenuItem(
                    icon: Icons.campaign_outlined,
                    title: '공지사항',
                    onTap: () {
                      _openFeature(context, ClinicianFeatureNavigation.notices);
                    },
                  ),
                  _DrawerMenuItem(
                    icon: Icons.chat_bubble_outline_rounded,
                    title: '고객센터',
                    onTap: () {
                      _openFeature(context, ClinicianFeatureNavigation.support);
                    },
                  ),
                  _DrawerMenuItem(
                    icon: Icons.settings_outlined,
                    title: '설정',
                    onTap: () {
                      _moveToTab(context, 4);
                    },
                  ),
                ],
              ),
            ),

            const Divider(height: 1, color: _border),

            Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
              child: _DrawerMenuItem(
                icon: Icons.logout_rounded,
                title: '로그아웃',
                iconColor: _danger,
                textColor: _danger,
                onTap: () {
                  _confirmLogout(context, ref);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(
    BuildContext context, {
    required String clinicianName,
    required String departmentName,
  }) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 12, 18),
      child: Row(
        children: [
          Container(
            width: 58,
            height: 58,
            decoration: BoxDecoration(
              color: const Color(0xFFEAF2FA),
              shape: BoxShape.circle,
              border: Border.all(color: const Color(0xFFD7E5F5)),
            ),
            child: const Icon(Icons.person_rounded, size: 32, color: _primary),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$clinicianName 의료진',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: _text,
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '$departmentName 전문의',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: _secondaryText,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            tooltip: '메뉴 닫기',
            onPressed: () {
              Navigator.of(context).pop();
            },
            icon: const Icon(Icons.close_rounded, color: _text, size: 25),
          ),
        ],
      ),
    );
  }

  void _moveToTab(BuildContext context, int index) {
    Navigator.of(context).pop();
    onSelectTab(index);
  }

  void _openFeature(
    BuildContext context,
    Future<void> Function(BuildContext) open,
  ) {
    Navigator.of(context).pop();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (context.mounted) {
        open(context);
      }
    });
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
                  onPressed: () {
                    Navigator.of(dialogContext).pop(false);
                  },
                  child: const Text('취소'),
                ),
                FilledButton(
                  onPressed: () {
                    Navigator.of(dialogContext).pop(true);
                  },
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

class _DrawerSectionTitle extends StatelessWidget {
  const _DrawerSectionTitle(this.title);

  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 4, 14, 6),
      child: Text(
        title,
        style: const TextStyle(
          color: Color(0xFF2563EB),
          fontSize: 12,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

class _DrawerMenuItem extends StatelessWidget {
  const _DrawerMenuItem({
    required this.icon,
    required this.title,
    required this.onTap,
    this.badgeCount,
    this.iconColor = const Color(0xFF334155),
    this.textColor = const Color(0xFF111827),
  });

  final IconData icon;
  final String title;
  final VoidCallback onTap;
  final int? badgeCount;
  final Color iconColor;
  final Color textColor;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
          child: Row(
            children: [
              Icon(icon, size: 21, color: iconColor),
              const SizedBox(width: 14),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    color: textColor,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              if (badgeCount != null && badgeCount! > 0)
                Container(
                  constraints: const BoxConstraints(
                    minWidth: 20,
                    minHeight: 20,
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 6),
                  alignment: Alignment.center,
                  decoration: const BoxDecoration(
                    color: Color(0xFFE34255),
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    '$badgeCount',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
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
}
