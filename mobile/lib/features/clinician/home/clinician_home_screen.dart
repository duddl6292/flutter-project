import 'package:flutter/material.dart';

class ClinicianHomeScreen extends StatelessWidget {
  const ClinicianHomeScreen({super.key});

  static const Color _backgroundColor = Color(0xFFF7F9FC);
  static const Color _primaryColor = Color(0xFF28669E);
  static const Color _primaryTextColor = Color(0xFF111827);
  static const Color _secondaryTextColor = Color(0xFF6B7280);
  static const Color _borderColor = Color(0xFFE5E7EB);
  static const Color _iconBackgroundColor = Color(0xFFEAF2FA);

  static const String _clinicianName = '이현우';
  static const String _department = '신경과';

  static const List<_ScheduleItem> _todaySchedules = [
    _ScheduleItem(
      time: '09:00',
      patientName: '김민준',
      visitType: '초진',
      status: '진료 완료',
      isCompleted: true,
    ),
    _ScheduleItem(
      time: '10:30',
      patientName: '박서연',
      visitType: '재진',
      status: '대기 중',
    ),
    _ScheduleItem(
      time: '11:20',
      patientName: '최영수',
      visitType: '검사 상담',
      status: '예약',
    ),
    _ScheduleItem(
      time: '14:00',
      patientName: '정미영',
      visitType: '재진',
      status: '예약',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _backgroundColor,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 24, 20, 36),
          children: [
            _buildGreeting(),
            const SizedBox(height: 24),
            _buildSummaryGrid(),
            const SizedBox(height: 28),
            _buildSectionTitle('빠른 메뉴'),
            const SizedBox(height: 12),
            _buildQuickMenu(context),
            const SizedBox(height: 28),
            _buildScheduleHeader(),
            const SizedBox(height: 12),
            _buildScheduleCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildGreeting() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '안녕하세요, $_clinicianName 의료진님',
                style: TextStyle(
                  color: _primaryTextColor,
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 5,
                    ),
                    decoration: BoxDecoration(
                      color: _iconBackgroundColor,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Text(
                      _department,
                      style: TextStyle(
                        color: _primaryColor,
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    _formattedToday(),
                    style: const TextStyle(
                      color: _secondaryTextColor,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        Container(
          width: 52,
          height: 52,
          decoration: const BoxDecoration(
            color: _iconBackgroundColor,
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.medical_services_outlined,
            color: _primaryColor,
            size: 28,
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryGrid() {
    return LayoutBuilder(
      builder: (context, constraints) {
        const spacing = 12.0;
        final cardWidth = (constraints.maxWidth - spacing) / 2;

        return Wrap(
          spacing: spacing,
          runSpacing: spacing,
          children: [
            SizedBox(
              width: cardWidth,
              child: const _SummaryCard(
                icon: Icons.calendar_today_outlined,
                label: '오늘 예약 환자',
                value: '12명',
                color: _primaryColor,
              ),
            ),
            SizedBox(
              width: cardWidth,
              child: const _SummaryCard(
                icon: Icons.hourglass_top_rounded,
                label: '진료 대기 환자',
                value: '4명',
                color: Color(0xFFF59E0B),
              ),
            ),
            SizedBox(
              width: constraints.maxWidth,
              child: const _SummaryCard(
                icon: Icons.assignment_late_outlined,
                label: '확인이 필요한 검사결과',
                value: '3건',
                color: Color(0xFFD14343),
                horizontal: true,
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildQuickMenu(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _QuickMenuItem(
            icon: Icons.person_search_outlined,
            label: '환자 조회',
            onTap: () => _showPreparingMessage(context, '환자 조회'),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _QuickMenuItem(
            icon: Icons.event_note_outlined,
            label: '예약 관리',
            onTap: () => _showPreparingMessage(context, '예약 관리'),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _QuickMenuItem(
            icon: Icons.description_outlined,
            label: '진료 기록',
            onTap: () => _showPreparingMessage(context, '진료 기록'),
          ),
        ),
      ],
    );
  }

  Widget _buildScheduleHeader() {
    return Row(
      children: [
        _buildSectionTitle('오늘 진료 일정'),
        const Spacer(),
        Text(
          '총 ${_todaySchedules.length}건',
          style: const TextStyle(
            color: _secondaryTextColor,
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildScheduleCard() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _borderColor),
      ),
      child: Column(
        children: [
          for (var index = 0; index < _todaySchedules.length; index++) ...[
            _ScheduleTile(schedule: _todaySchedules[index]),
            if (index != _todaySchedules.length - 1)
              const Divider(
                height: 1,
                indent: 82,
                endIndent: 16,
                color: _borderColor,
              ),
          ],
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        color: _primaryTextColor,
        fontSize: 17,
        fontWeight: FontWeight.w800,
      ),
    );
  }

  static String _formattedToday() {
    final today = DateTime.now();
    const weekdays = ['월', '화', '수', '목', '금', '토', '일'];
    return '${today.year}년 ${today.month}월 ${today.day}일 '
        '${weekdays[today.weekday - 1]}요일';
  }

  void _showPreparingMessage(BuildContext context, String featureName) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text('$featureName 기능은 준비 중입니다.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
  }
}

class _SummaryCard extends StatelessWidget {
  const _SummaryCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
    this.horizontal = false,
  });

  final IconData icon;
  final String label;
  final String value;
  final Color color;
  final bool horizontal;

  @override
  Widget build(BuildContext context) {
    final iconWidget = Container(
      width: 42,
      height: 42,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(13),
      ),
      child: Icon(icon, color: color, size: 22),
    );

    return Container(
      padding: const EdgeInsets.all(17),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: ClinicianHomeScreen._borderColor),
      ),
      child: horizontal
          ? Row(
              children: [
                iconWidget,
                const SizedBox(width: 14),
                Expanded(child: _buildLabel()),
                _buildValue(),
              ],
            )
          : Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                iconWidget,
                const SizedBox(height: 16),
                _buildValue(),
                const SizedBox(height: 5),
                _buildLabel(),
              ],
            ),
    );
  }

  Widget _buildLabel() {
    return Text(
      label,
      style: const TextStyle(
        color: ClinicianHomeScreen._secondaryTextColor,
        fontSize: 13,
        height: 1.35,
      ),
    );
  }

  Widget _buildValue() {
    return Text(
      value,
      style: const TextStyle(
        color: ClinicianHomeScreen._primaryTextColor,
        fontSize: 23,
        fontWeight: FontWeight.w800,
      ),
    );
  }
}

class _QuickMenuItem extends StatelessWidget {
  const _QuickMenuItem({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 17),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: ClinicianHomeScreen._borderColor),
          ),
          child: Column(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: ClinicianHomeScreen._iconBackgroundColor,
                  borderRadius: BorderRadius.circular(13),
                ),
                child: Icon(
                  icon,
                  color: ClinicianHomeScreen._primaryColor,
                  size: 22,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                label,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: ClinicianHomeScreen._primaryTextColor,
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ScheduleTile extends StatelessWidget {
  const _ScheduleTile({required this.schedule});

  final _ScheduleItem schedule;

  @override
  Widget build(BuildContext context) {
    final statusColor = schedule.isCompleted
        ? const Color(0xFF2F855A)
        : schedule.status == '대기 중'
        ? const Color(0xFFF59E0B)
        : ClinicianHomeScreen._primaryColor;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
      child: Row(
        children: [
          SizedBox(
            width: 50,
            child: Text(
              schedule.time,
              style: const TextStyle(
                color: ClinicianHomeScreen._primaryTextColor,
                fontSize: 15,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  schedule.patientName,
                  style: const TextStyle(
                    color: ClinicianHomeScreen._primaryTextColor,
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  schedule.visitType,
                  style: const TextStyle(
                    color: ClinicianHomeScreen._secondaryTextColor,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
            decoration: BoxDecoration(
              color: statusColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              schedule.status,
              style: TextStyle(
                color: statusColor,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ScheduleItem {
  const _ScheduleItem({
    required this.time,
    required this.patientName,
    required this.visitType,
    required this.status,
    this.isCompleted = false,
  });

  final String time;
  final String patientName;
  final String visitType;
  final String status;
  final bool isCompleted;
}
