import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/home/clinician_dashboard_model.dart';
import 'package:brainon_mobile/features/clinician/home/clinician_home_provider.dart';
import 'package:brainon_mobile/features/clinician/clinician_feature_navigation.dart';
import 'package:brainon_mobile/features/notifications/notification_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

/// 의료진 홈 진입 화면
///
/// Provider에서 대시보드 데이터를 받아 로딩, 오류, 성공 상태를 처리한다.
/// 기존 [ClinicianHomeScreen] 호출부를 수정하지 않아도 되도록
/// 생성자 형태는 그대로 유지한다.
class ClinicianHomeScreen extends ConsumerWidget {
  const ClinicianHomeScreen({
    required this.clinicianName,
    required this.departmentName,
    required this.onOpenDrawer,
    required this.onSelectTab,
    super.key,
  });

  final String clinicianName;
  final String departmentName;
  final VoidCallback onOpenDrawer;
  final ValueChanged<int> onSelectTab;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardAsync = ref.watch(clinicianDashboardProvider);
    final notificationCount =
        ref.watch(unreadNotificationCountProvider).valueOrNull ?? 0;

    return dashboardAsync.when(
      loading: () => const _DashboardLoadingView(),
      error: (error, stackTrace) => _DashboardErrorView(
        error: error,
        onRetry: () {
          ref.invalidate(clinicianDashboardProvider);
        },
      ),
      data: (dashboard) => _ClinicianHomeContent(
        clinicianName: clinicianName,
        departmentName: departmentName,
        dashboard: dashboard,
        onOpenDrawer: onOpenDrawer,
        onSelectTab: onSelectTab,
        notificationCount: notificationCount,
        onRefresh: () async {
          final refresh = ref.refresh(clinicianDashboardProvider.future);
          await refresh;
        },
      ),
    );
  }
}

/// 의료진 홈의 실제 UI
///
/// 이 위젯은 전달받은 모델만 사용하며 Mock, Repository, Provider를 직접 참조하지 않는다.
class _ClinicianHomeContent extends StatelessWidget {
  const _ClinicianHomeContent({
    required this.clinicianName,
    required this.departmentName,
    required this.dashboard,
    required this.onOpenDrawer,
    required this.onSelectTab,
    required this.onRefresh,
    required this.notificationCount,
  });

  static const _background = Color(0xFFF6F8FC);
  static const _primary = Color(0xFF28669E);
  static const _text = Color(0xFF111827);
  static const _secondaryText = Color(0xFF6B7280);
  static const _border = Color(0xFFE5EAF2);
  static const _lavender = Color(0xFFF1EDFF);

  final String clinicianName;
  final String departmentName;
  final ClinicianDashboard dashboard;
  final VoidCallback onOpenDrawer;
  final ValueChanged<int> onSelectTab;
  final Future<void> Function() onRefresh;
  final int notificationCount;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: _background,
      child: SafeArea(
        bottom: false,
        child: RefreshIndicator(
          onRefresh: onRefresh,
          child: CustomScrollView(
            physics: const AlwaysScrollableScrollPhysics(
              parent: BouncingScrollPhysics(),
            ),
            slivers: [
              SliverToBoxAdapter(child: _buildHeader(context)),
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(20, 10, 20, 28),
                sliver: SliverList.list(
                  children: [
                    _buildProfile(),
                    const SizedBox(height: 18),
                    _buildSummary(),
                    const SizedBox(height: 14),
                    _buildConsultationBanner(),
                    const SizedBox(height: 24),
                    Row(
                      children: [
                        _sectionTitle('빠른 메뉴'),
                        const Spacer(),
                        TextButton(
                          onPressed: () {
                            _showReady(context, '빠른 메뉴 편집');
                          },
                          child: const Text(
                            '편집',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    _buildQuickMenu(context),
                    const SizedBox(height: 24),
                    _buildScheduleHeader(),
                    const SizedBox(height: 12),
                    _buildScheduleCard(context),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(10, 6, 12, 0),
      child: Row(
        children: [
          IconButton(
            tooltip: '메뉴',
            onPressed: onOpenDrawer,
            icon: const Icon(Icons.menu_rounded, size: 29, color: _text),
          ),
          const Spacer(),
          IconButton(
            tooltip: '알림',
            onPressed: () => ClinicianFeatureNavigation.notifications(context),
            icon: Badge(
              isLabelVisible: notificationCount > 0,
              label: Text('$notificationCount'),
              child: const Icon(
                Icons.notifications_none_rounded,
                size: 27,
                color: _text,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Container(
            width: 43,
            height: 43,
            decoration: BoxDecoration(
              color: const Color(0xFFEAF2FA),
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 2),
            ),
            child: const Icon(
              Icons.medical_services_outlined,
              color: _primary,
              size: 23,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProfile() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '안녕하세요,',
          style: TextStyle(color: _secondaryText, fontSize: 14),
        ),
        const SizedBox(height: 2),
        Text(
          '$clinicianName 의료진님 👋',
          style: const TextStyle(
            color: _text,
            fontSize: 25,
            height: 1.2,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: const Color(0xFFEAF2FA),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                departmentName,
                style: const TextStyle(
                  color: _primary,
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
            const Spacer(),
            Text(
              _formatToday(),
              style: const TextStyle(
                color: _secondaryText,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSummary() {
    final summary = dashboard.summary;

    final items = [
      ('예약 환자', summary.appointmentTotal, '명', _text),
      ('대기 환자', summary.appointmentWaiting, '명', _primary),
      ('협진 요청', summary.consultationWaiting, '건', const Color(0xFFE34255)),
      ('검사 결과', summary.testResultWaiting, '건', const Color(0xFF7957D5)),
    ];

    return Container(
      decoration: _cardDecoration(),
      child: Row(
        children: [
          for (var index = 0; index < items.length; index++) ...[
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 17),
                child: Column(
                  children: [
                    Text(
                      items[index].$1,
                      style: TextStyle(
                        color: items[index].$4,
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 7),
                    Text.rich(
                      TextSpan(
                        text: '${items[index].$2}',
                        children: [
                          TextSpan(
                            text: items[index].$3,
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                      style: TextStyle(
                        color: items[index].$4,
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (index != items.length - 1)
              const SizedBox(
                height: 40,
                child: VerticalDivider(width: 1, color: _border),
              ),
          ],
        ],
      ),
    );
  }

  Widget _buildConsultationBanner() {
    final waiting = dashboard.consultations
        .where((item) => item.status == 'requested' || item.status == 'waiting')
        .toList();

    if (waiting.isEmpty) {
      return const SizedBox.shrink();
    }

    final departments = waiting
        .map((item) => item.department)
        .where((department) => department.isNotEmpty)
        .join(' · ');

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => onSelectTab(3),
        borderRadius: BorderRadius.circular(16),
        child: Ink(
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF102A50), Color(0xFF1C3764)],
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: const [
              BoxShadow(
                color: Color(0x22102A50),
                blurRadius: 14,
                offset: Offset(0, 6),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: const BoxDecoration(
                  color: Color(0xFFE34255),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.groups_2_outlined,
                  color: Colors.white,
                  size: 19,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '협진 요청 ${waiting.length}건 도착',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      departments.isEmpty ? '새 협진 요청을 확인해 주세요.' : departments,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Color(0xFFCAD7EA),
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 11,
                  vertical: 7,
                ),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Row(
                  children: [
                    Text(
                      '바로 확인',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    SizedBox(width: 3),
                    Icon(
                      Icons.chevron_right_rounded,
                      color: Colors.white,
                      size: 17,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickMenu(BuildContext context) {
    final items = [
      (
        title: '환자 조회',
        icon: Icons.person_search_outlined,
        backgroundColor: const Color(0xFFEAF2FF),
        iconColor: _primary,
      ),
      (
        title: '예약 관리',
        icon: Icons.calendar_month_outlined,
        backgroundColor: const Color(0xFFEAF2FF),
        iconColor: const Color(0xFF4A7FE5),
      ),
      (
        title: '검사 결과',
        icon: Icons.assignment_outlined,
        backgroundColor: _lavender,
        iconColor: const Color(0xFF7957D5),
      ),
      (
        title: '처방 관리',
        icon: Icons.medication_outlined,
        backgroundColor: const Color(0xFFEAF7F1),
        iconColor: const Color(0xFF2E9C75),
      ),
      (
        title: 'AI 분석',
        icon: Icons.psychology_alt_outlined,
        backgroundColor: const Color(0xFFF1EDFF),
        iconColor: const Color(0xFF7957D5),
      ),
    ];

    return SizedBox(
      height: 104,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        itemCount: items.length,
        separatorBuilder: (context, index) {
          return const SizedBox(width: 10);
        },
        itemBuilder: (context, index) {
          final item = items[index];

          return SizedBox(
            width: 82,
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () {
                  _onQuickMenuTap(context, item.title);
                },
                child: Ink(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: _border),
                    boxShadow: const [
                      BoxShadow(
                        color: Color(0x08000000),
                        blurRadius: 8,
                        offset: Offset(0, 3),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 12,
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 42,
                          height: 42,
                          decoration: BoxDecoration(
                            color: item.backgroundColor,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            item.icon,
                            color: item.iconColor,
                            size: 24,
                          ),
                        ),
                        const SizedBox(height: 9),
                        Text(
                          item.title,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: _text,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildScheduleHeader() {
    return Row(
      children: [
        _sectionTitle('오늘 일정'),
        const Spacer(),
        TextButton(
          onPressed: () => onSelectTab(1),
          child: const Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('전체보기'),
              SizedBox(width: 2),
              Icon(Icons.chevron_right_rounded, size: 17),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildScheduleCard(BuildContext context) {
    final schedules = dashboard.schedules;

    if (schedules.isEmpty) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 32),
        decoration: _cardDecoration(),
        child: const Column(
          children: [
            Icon(
              Icons.event_available_outlined,
              color: _secondaryText,
              size: 30,
            ),
            SizedBox(height: 8),
            Text(
              '오늘 등록된 일정이 없습니다.',
              style: TextStyle(
                color: _secondaryText,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      decoration: _cardDecoration(),
      child: Column(
        children: [
          for (var index = 0; index < schedules.length; index++) ...[
            _ScheduleRow(
              schedule: schedules[index],
              onTap: schedules[index].patientId.isEmpty
                  ? null
                  : () => context.pushNamed(
                      RouteNames.clinicianPatientDetail,
                      pathParameters: {
                        'patientId': schedules[index].patientId,
                      },
                    ),
            ),
            if (index != schedules.length - 1)
              const Divider(
                height: 1,
                indent: 70,
                endIndent: 14,
                color: _border,
              ),
          ],
        ],
      ),
    );
  }

  Widget _sectionTitle(String value) {
    return Text(
      value,
      style: const TextStyle(
        color: _text,
        fontSize: 17,
        fontWeight: FontWeight.w800,
      ),
    );
  }

  BoxDecoration _cardDecoration() {
    return BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      border: Border.all(color: _border),
      boxShadow: const [
        BoxShadow(
          color: Color(0x08000000),
          blurRadius: 10,
          offset: Offset(0, 3),
        ),
      ],
    );
  }

  String _formatToday() {
    final now = DateTime.now();
    const weekdays = ['월', '화', '수', '목', '금', '토', '일'];

    return '${now.year}.'
        '${now.month.toString().padLeft(2, '0')}.'
        '${now.day.toString().padLeft(2, '0')} '
        '(${weekdays[now.weekday - 1]})';
  }

  void _onQuickMenuTap(BuildContext context, String menuTitle) {
    switch (menuTitle) {
      case '환자 조회':
        onSelectTab(0);
        break;
      case '예약 관리':
        onSelectTab(1);
        break;
      case '검사 결과':
        ClinicianFeatureNavigation.testResults(context);
        break;
      case '처방 관리':
        ClinicianFeatureNavigation.prescriptions(context);
        break;
      case 'AI 분석':
        ClinicianFeatureNavigation.aiAnalysis(context);
        break;
      default:
        _showReady(context, menuTitle);
    }
  }

  void _showReady(BuildContext context, String feature) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text('$feature 기능은 준비 중입니다.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
  }
}

class _ScheduleRow extends StatelessWidget {
  const _ScheduleRow({required this.schedule, required this.onTap});

  final ClinicianSchedule schedule;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final status = schedule.status;

    final (label, foreground, background) = switch (status) {
      'in_progress' => ('진료', const Color(0xFF28669E), const Color(0xFFEAF2FA)),
      'waiting' => ('대기', const Color(0xFFD47A12), const Color(0xFFFFF3DF)),
      'scheduled' => ('예약', const Color(0xFF7957D5), const Color(0xFFF1EDFF)),
      'confirmed' => ('예약', const Color(0xFF7957D5), const Color(0xFFF1EDFF)),
      'checked_in' => ('접수', const Color(0xFFD47A12), const Color(0xFFFFF3DF)),
      'completed' => ('완료', const Color(0xFF2E9C75), const Color(0xFFEAF7F1)),
      'cancelled' => ('취소', const Color(0xFF6B7280), const Color(0xFFF3F4F6)),
      'no_show' => ('미방문', const Color(0xFFE34255), const Color(0xFFFDECEF)),
      _ => (
        status.isEmpty ? '확인' : status,
        const Color(0xFF6B7280),
        const Color(0xFFF3F4F6),
      ),
    };

    final startAt = schedule.startAt.toLocal();
    final time =
        '${startAt.hour.toString().padLeft(2, '0')}:'
        '${startAt.minute.toString().padLeft(2, '0')}';

    final patientName = schedule.patientName.isEmpty
        ? '-'
        : schedule.patientName;
    final room = schedule.room.isEmpty ? '-' : schedule.room;

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
        child: Row(
        children: [
          SizedBox(
            width: 47,
            child: Text(
              time,
              style: const TextStyle(
                color: Color(0xFF111827),
                fontSize: 13,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Row(
              children: [
                Flexible(
                  child: Text(
                    patientName,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: Color(0xFF111827),
                      fontSize: 13,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    room,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: Color(0xFF6B7280),
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
            decoration: BoxDecoration(
              color: background,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              label,
              style: TextStyle(
                color: foreground,
                fontSize: 10,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
        ],
        ),
      ),
    );
  }
}

class _DashboardLoadingView extends StatelessWidget {
  const _DashboardLoadingView();

  @override
  Widget build(BuildContext context) {
    return const ColoredBox(
      color: Color(0xFFF6F8FC),
      child: SafeArea(child: Center(child: CircularProgressIndicator())),
    );
  }
}

class _DashboardErrorView extends StatelessWidget {
  const _DashboardErrorView({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final unauthorized =
        error is ApiException && (error as ApiException).statusCode == 401;
    return ColoredBox(
      color: const Color(0xFFF6F8FC),
      child: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.cloud_off_outlined,
                  size: 44,
                  color: Color(0xFF6B7280),
                ),
                const SizedBox(height: 14),
                Text(
                  unauthorized
                      ? '로그인이 만료되었습니다. 다시 로그인해주세요.'
                      : '의료진 홈 정보를 불러오지 못했습니다.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    color: Color(0xFF111827),
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  '잠시 후 다시 시도해 주세요.',
                  style: TextStyle(color: Color(0xFF6B7280), fontSize: 13),
                ),
                const SizedBox(height: 18),
                FilledButton.icon(
                  onPressed: onRetry,
                  icon: const Icon(Icons.refresh_rounded),
                  label: const Text('다시 시도'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
