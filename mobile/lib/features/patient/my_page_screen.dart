import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/patient/providers/patient_profile_provider.dart';
import 'package:brainon_mobile/features/medication/medication_list_screen.dart';
import 'package:brainon_mobile/shared/models/patient_profile.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class MyPageScreen extends ConsumerWidget {
  const MyPageScreen({required this.onOpenDrawer, super.key});

  final VoidCallback onOpenDrawer;

  static const Color _backgroundColor = Color(0xFFF7F9FC);
  static const Color _primaryTextColor = Color(0xFF111827);
  static const Color _secondaryTextColor = Color(0xFF6B7280);
  static const Color _borderColor = Color(0xFFE5E7EB);
  static const Color _iconBackgroundColor = Color(0xFFEAF2FA);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(patientProfileProvider);

    return Scaffold(
      backgroundColor: _backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(context),
            Expanded(
              child: RefreshIndicator(
                onRefresh: () async {
                  ref.invalidate(patientProfileProvider);

                  await ref.read(patientProfileProvider.future);
                },
                child: profileAsync.when(
                  loading: _buildLoadingView,
                  error: (error, stackTrace) {
                    return _buildErrorView(context, ref, error);
                  },
                  data: (profile) {
                    return _buildProfileView(context, ref, profile);
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ============================================================
  // 상단바
  // ============================================================
  Widget _buildHeader(BuildContext context) {
    return Container(
      height: 76,
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(bottom: BorderSide(color: _borderColor)),
      ),
      child: Stack(
        children: [
          const Positioned.fill(
            child: Align(
              alignment: Alignment.center,
              child: Text(
                '마이페이지',
                style: TextStyle(
                  color: _primaryTextColor,
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
          Positioned(
            left: 12,
            top: 10,
            bottom: 10,
            child: IconButton(
              tooltip: '메뉴',
              onPressed: onOpenDrawer,
              icon: const Icon(
                Icons.menu_rounded,
                size: 32,
                color: _primaryTextColor,
              ),
            ),
          ),
          Positioned(
            right: 12,
            top: 10,
            bottom: 10,
            child: IconButton(
              tooltip: '알림',
              onPressed: () {
                _showPreparingMessage(context, '알림함');
              },
              icon: const Icon(
                Icons.notifications_none_rounded,
                size: 32,
                color: _primaryTextColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ============================================================
  // 로딩 화면
  // ============================================================
  Widget _buildLoadingView() {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.only(top: 180),
      children: const [
        Center(child: CircularProgressIndicator()),
        SizedBox(height: 16),
        Center(
          child: Text(
            '사용자 정보를 불러오고 있습니다.',
            style: TextStyle(color: _secondaryTextColor, fontSize: 14),
          ),
        ),
      ],
    );
  }

  // ============================================================
  // 오류 화면
  // ============================================================
  Widget _buildErrorView(BuildContext context, WidgetRef ref, Object error) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(24, 150, 24, 40),
      children: [
        const Icon(
          Icons.error_outline_rounded,
          size: 56,
          color: _secondaryTextColor,
        ),
        const SizedBox(height: 16),
        const Text(
          '사용자 정보를 불러오지 못했습니다.',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: _primaryTextColor,
            fontSize: 17,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          error.toString(),
          textAlign: TextAlign.center,
          style: const TextStyle(color: _secondaryTextColor, fontSize: 13),
        ),
        const SizedBox(height: 24),
        Center(
          child: OutlinedButton.icon(
            onPressed: () {
              ref.invalidate(patientProfileProvider);
            },
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('다시 시도'),
          ),
        ),
      ],
    );
  }

  // ============================================================
  // 마이페이지 본문
  // ============================================================
  Widget _buildProfileView(
    BuildContext context,
    WidgetRef ref,
    PatientProfile profile,
  ) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 36),
      children: [
        _buildProfileCard(context, profile),
        const SizedBox(height: 24),

        _buildSectionTitle('건강·진료 관리'),
        const SizedBox(height: 10),
        _buildMenuCard(
          children: [
            _buildMenuItem(
              context: context,
              icon: Icons.history_rounded,
              title: '진료 내역',
              subtitle: '이전에 받은 진료 기록을 확인해요.',
              onTap: () {
                context.pushNamed(RouteNames.patientMedicalHistory);
              },
            ),
            _buildDivider(),
            _buildMenuItem(
              context: context,
              icon: Icons.medication_outlined,
              title: '복약 관리',
              subtitle: '처방약과 복약 일정을 관리해요.',
              onTap: () {
                Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (_) => const MedicationListScreen(),
                  ),
                );
              },
            ),
            _buildDivider(),
            _buildMenuItem(
              context: context,
              icon: Icons.favorite_border_rounded,
              title: '즐겨찾는 병원',
              subtitle: '저장한 병원 정보를 확인해요.',
              onTap: () {
                context.pushNamed(RouteNames.favoriteHospitals);
              },
            ),
          ],
        ),
        const SizedBox(height: 24),

        _buildSectionTitle('설정'),
        const SizedBox(height: 10),
        _buildMenuCard(
          children: [
            _buildMenuItem(
              context: context,
              icon: Icons.notifications_outlined,
              title: '알림 설정',
              subtitle: '예약, 복약, 검사결과 알림을 설정해요.',
              onTap: () {
                context.pushNamed(RouteNames.notificationSettings);
              },
            ),

            _buildDivider(),
            _buildMenuItem(
              context: context,
              icon: Icons.person_outline_rounded,
              title: '개인정보 관리',
              subtitle: '연락처와 개인정보를 확인하고 수정해요.',
              onTap: () {
                context.pushNamed(RouteNames.personalInfo);
              },
            ),
          ],
        ),
        const SizedBox(height: 24),

        _buildSectionTitle('서비스 안내'),
        const SizedBox(height: 10),
        _buildMenuCard(
          children: [
            _buildMenuItem(
              context: context,
              icon: Icons.campaign_outlined,
              title: '공지사항',
              onTap: () {
                _showPreparingMessage(context, '공지사항');
              },
            ),
            _buildDivider(),
            _buildMenuItem(
              context: context,
              icon: Icons.help_outline_rounded,
              title: '고객센터',
              onTap: () {
                _showPreparingMessage(context, '고객센터');
              },
            ),
            _buildDivider(),
            _buildMenuItem(
              context: context,
              icon: Icons.info_outline_rounded,
              title: '앱 정보',
              trailingText: '버전 1.0.0',
              onTap: () {
                context.pushNamed(RouteNames.appInfo);
              },
            ),
          ],
        ),
        const SizedBox(height: 24),

        _buildLogoutButton(context, ref),
      ],
    );
  }

  // ============================================================
  // 프로필 카드
  // ============================================================
  Widget _buildProfileCard(BuildContext context, PatientProfile profile) {
    final detailText = _buildProfileDetailText(profile);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _borderColor),
      ),
      child: Row(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: const BoxDecoration(
              color: _iconBackgroundColor,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.person_rounded,
              size: 36,
              color: Color(0xFF28669E),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Flexible(
                      child: Text(
                        '${profile.displayName}님',
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: _primaryTextColor,
                          fontSize: 21,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 9,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: _iconBackgroundColor,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        profile.displayRole,
                        style: const TextStyle(
                          color: Color(0xFF28669E),
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 7),
                Text(
                  detailText,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: _secondaryTextColor,
                    fontSize: 14,
                    height: 1.4,
                  ),
                ),
                if (profile.patientNumber != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    '환자번호 ${profile.patientNumber}',
                    style: const TextStyle(
                      color: _secondaryTextColor,
                      fontSize: 13,
                    ),
                  ),
                ],
              ],
            ),
          ),
          IconButton(
            tooltip: '내 정보 수정',
            onPressed: () {
              _showPreparingMessage(context, '내 정보 수정');
            },
            icon: const Icon(
              Icons.chevron_right_rounded,
              color: _secondaryTextColor,
            ),
          ),
        ],
      ),
    );
  }

  String _buildProfileDetailText(PatientProfile profile) {
    if (profile.email != null) {
      return profile.email!;
    }

    if (profile.phone != null) {
      return profile.phone!;
    }

    return profile.username;
  }

  // ============================================================
  // 섹션 제목
  // ============================================================
  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        title,
        style: const TextStyle(
          color: _primaryTextColor,
          fontSize: 16,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }

  // ============================================================
  // 메뉴 카드
  // ============================================================
  Widget _buildMenuCard({required List<Widget> children}) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _borderColor),
      ),
      child: Column(children: children),
    );
  }

  Widget _buildMenuItem({
    required BuildContext context,
    required IconData icon,
    required String title,
    required VoidCallback onTap,
    String? subtitle,
    String? trailingText,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
          child: Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: _iconBackgroundColor,
                  borderRadius: BorderRadius.circular(13),
                ),
                child: Icon(icon, size: 22, color: const Color(0xFF28669E)),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        color: _primaryTextColor,
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    if (subtitle != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: const TextStyle(
                          color: _secondaryTextColor,
                          fontSize: 12,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              if (trailingText != null)
                Text(
                  trailingText,
                  style: const TextStyle(
                    color: _secondaryTextColor,
                    fontSize: 12,
                  ),
                )
              else
                const Icon(
                  Icons.chevron_right_rounded,
                  color: _secondaryTextColor,
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDivider() {
    return const Divider(
      height: 1,
      thickness: 1,
      indent: 72,
      endIndent: 16,
      color: _borderColor,
    );
  }

  // ============================================================
  // 로그아웃
  // ============================================================
  Widget _buildLogoutButton(BuildContext context, WidgetRef ref) {
    return SizedBox(
      width: double.infinity,
      height: 54,
      child: OutlinedButton.icon(
        onPressed: () {
          _showLogoutDialog(context, ref);
        },
        icon: const Icon(Icons.logout_rounded, size: 21),
        label: const Text(
          '로그아웃',
          style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
        ),
        style: OutlinedButton.styleFrom(
          foregroundColor: _secondaryTextColor,
          side: const BorderSide(color: _borderColor),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }

  Future<void> _showLogoutDialog(BuildContext context, WidgetRef ref) async {
    final shouldLogout = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('로그아웃'),
          content: const Text('현재 계정에서 로그아웃하시겠습니까?'),
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
              child: const Text('로그아웃'),
            ),
          ],
        );
      },
    );

    if (shouldLogout != true || !context.mounted) {
      return;
    }

    try {
      await ref.read(authProvider.notifier).logout();

      if (!context.mounted) {
        return;
      }

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('로그아웃되었습니다.')));
    } on Object {
      if (!context.mounted) {
        return;
      }

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('로그아웃 처리 중 오류가 발생했습니다.')));
    }
  }

  // ============================================================
  // 준비 중 안내
  // ============================================================
  void _showPreparingMessage(BuildContext context, String featureName) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text('$featureName 기능은 준비 중입니다.')));
  }
}
