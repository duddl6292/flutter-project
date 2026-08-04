import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/shared/mock/patient_home_mock.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({required this.onOpenDrawer, super.key});

  /// PatientMainScreen이 관리하는 공통 Drawer를 엽니다.
  final VoidCallback onOpenDrawer;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const Color primaryColor = Color(0xFF2563EB);
  static const Color textColor = Color(0xFF111827);
  static const Color subTextColor = Color(0xFF6B7280);

  @override
  Widget build(BuildContext context) {
    final patient = patientHomeMock['patient'] as Map<String, dynamic>;

    final nextAppointment =
        patientHomeMock['next_appointment'] as Map<String, dynamic>;

    final upcomingDates = patientHomeMock['upcoming_dates'] as List<dynamic>;

    final medication = patientHomeMock['medication'] as Map<String, dynamic>;

    final medicationItems = medication['items'] as List<dynamic>;

    return Scaffold(
      // 챗봇 버튼
      floatingActionButton: _buildChatbotButton(),

      // HomeScreen 자체의 BottomNavigationBar는 제거합니다.
      // 하단 네비게이션은 PatientMainScreen에서만 관리합니다.
      body: SafeArea(
        child: Column(
          children: [
            _buildTopBar(
              notificationCount: patient['notification_count'] as int,
            ),

            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 26, 20, 100),
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 520),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildGreetingSection(
                          patientName: patient['name'] as String,
                        ),

                        const SizedBox(height: 24),

                        _buildScheduleCard(
                          appointment: nextAppointment,
                          upcomingDates: upcomingDates,
                        ),

                        const SizedBox(height: 18),

                        _buildMedicationCard(
                          medication: medication,
                          items: medicationItems,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ============================================================
  // 상단 바
  // ============================================================
  Widget _buildTopBar({required int notificationCount}) {
    return Container(
      height: 76,
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(bottom: BorderSide(color: Color(0xFFE5E7EB))),
      ),
      child: Stack(
        children: [
          Positioned.fill(
            child: Align(
              alignment: Alignment.center,
              child: Image.asset(
                'assets/images/logo.png',
                width: 112,
                height: 44,
                fit: BoxFit.contain,
              ),
            ),
          ),

          // 햄버거 메뉴
          Positioned(
            left: 12,
            top: 10,
            bottom: 10,
            child: IconButton(
              tooltip: '메뉴',
              onPressed: widget.onOpenDrawer,
              icon: const Icon(Icons.menu_rounded, size: 32, color: textColor),
            ),
          ),

          // 알림
          Positioned(
            right: 12,
            top: 10,
            bottom: 10,
            child: Stack(
              clipBehavior: Clip.none,
              children: [
                IconButton(
                  tooltip: '알림',
                  onPressed: () {
                    _showMessage('알림 목록 화면은 추후 연결할 예정입니다.');
                  },
                  icon: const Icon(
                    Icons.notifications_none_rounded,
                    size: 32,
                    color: textColor,
                  ),
                ),

                if (notificationCount > 0)
                  Positioned(
                    right: 3,
                    top: 2,
                    child: Container(
                      constraints: const BoxConstraints(
                        minWidth: 20,
                        minHeight: 20,
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 5),
                      decoration: const BoxDecoration(
                        color: Color(0xFFEF4444),
                        shape: BoxShape.circle,
                      ),
                      alignment: Alignment.center,
                      child: Text(
                        '$notificationCount',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ============================================================
  // 인사말
  // ============================================================
  Widget _buildGreetingSection({required String patientName}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '안녕하세요, $patientName님!',
          style: const TextStyle(
            color: textColor,
            fontSize: 25,
            fontWeight: FontWeight.w800,
            height: 1.3,
          ),
        ),
        const SizedBox(height: 6),
        const Text(
          '오늘도 건강한 하루 되세요.',
          style: TextStyle(color: subTextColor, fontSize: 16),
        ),
      ],
    );
  }

  // ============================================================
  // 진료 일정 카드
  // ============================================================
  Widget _buildScheduleCard({
    required Map<String, dynamic> appointment,
    required List<dynamic> upcomingDates,
  }) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: _cardDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Text(
                  '진료 일정',
                  style: TextStyle(
                    color: textColor,
                    fontSize: 21,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              TextButton(
                onPressed: () {
                  context.pushNamed(RouteNames.appointments);
                },
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '전체보기',
                      style: TextStyle(
                        color: primaryColor,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    SizedBox(width: 2),
                    Icon(Icons.chevron_right_rounded, color: primaryColor),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 14),

          SizedBox(
            width: double.infinity,
            height: 48,
            child: OutlinedButton.icon(
              onPressed: () {
                context.pushNamed(RouteNames.appointmentCreate);
              },
              icon: const Icon(Icons.add_circle_outline, size: 20),
              label: const Text(
                '진료 예약하기',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
              style: OutlinedButton.styleFrom(
                foregroundColor: primaryColor,
                backgroundColor: const Color(0xFFEFF6FF),
                side: const BorderSide(color: Color(0xFFBFDBFE)),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),

          const SizedBox(height: 18),

          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: const Color(0xFFE5E7EB)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                SizedBox(
                  width: 66,
                  child: Column(
                    children: [
                      Text(
                        appointment['date'] as String,
                        style: const TextStyle(
                          color: primaryColor,
                          fontSize: 23,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        appointment['day'] as String,
                        style: const TextStyle(
                          color: subTextColor,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 5,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEAF2FF),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          appointment['d_day'] as String,
                          style: const TextStyle(
                            color: primaryColor,
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(width: 12),

                Container(
                  width: 1,
                  height: 112,
                  color: const Color(0xFFE5E7EB),
                ),

                const SizedBox(width: 16),

                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Wrap(
                        spacing: 10,
                        runSpacing: 6,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          Text(
                            appointment['time'] as String,
                            style: const TextStyle(
                              color: textColor,
                              fontSize: 22,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          _buildTypeChip(appointment['type'] as String),
                        ],
                      ),

                      const SizedBox(height: 10),

                      Text(
                        '${appointment['hospital_name']} '
                        '${appointment['department']}',
                        style: const TextStyle(
                          color: textColor,
                          fontSize: 17,
                          fontWeight: FontWeight.w800,
                        ),
                      ),

                      const SizedBox(height: 6),

                      Text(
                        appointment['doctor_name'] as String,
                        style: const TextStyle(
                          color: subTextColor,
                          fontSize: 15,
                        ),
                      ),

                      const SizedBox(height: 8),

                      Row(
                        children: [
                          const Icon(
                            Icons.location_on_outlined,
                            size: 18,
                            color: Color(0xFF9CA3AF),
                          ),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              appointment['location'] as String,
                              style: const TextStyle(
                                color: subTextColor,
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(width: 8),

                const Icon(
                  Icons.calendar_month_outlined,
                  color: primaryColor,
                  size: 28,
                ),
              ],
            ),
          ),

          const SizedBox(height: 18),

          const Text(
            '다가오는 예약',
            style: TextStyle(
              color: textColor,
              fontSize: 16,
              fontWeight: FontWeight.w800,
            ),
          ),

          const SizedBox(height: 10),

          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 12),
            decoration: BoxDecoration(
              color: const Color(0xFFFAFBFD),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE5E7EB)),
            ),
            child: Row(
              children: upcomingDates.map((dateData) {
                final date = dateData as Map<String, dynamic>;

                return Expanded(child: _buildUpcomingDate(date));
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypeChip(String type) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: const Color(0xFFEAF2FF),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        type,
        style: const TextStyle(
          color: primaryColor,
          fontSize: 13,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _buildUpcomingDate(Map<String, dynamic> date) {
    final day = date['day'] as String;
    final isSelected = date['is_selected'] as bool;
    final hasSchedule = date['has_schedule'] as bool;

    Color dayColor = subTextColor;

    if (day == '일') {
      dayColor = const Color(0xFFEF4444);
    } else if (day == '토') {
      dayColor = primaryColor;
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 2),
      padding: const EdgeInsets.symmetric(vertical: 7),
      decoration: BoxDecoration(
        color: isSelected ? primaryColor : Colors.transparent,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          Text(
            day,
            style: TextStyle(
              color: isSelected ? Colors.white : dayColor,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 7),
          Text(
            date['date'] as String,
            style: TextStyle(
              color: isSelected ? Colors.white : textColor,
              fontSize: 16,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 7),
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: hasSchedule
                  ? isSelected
                        ? Colors.white
                        : primaryColor
                  : const Color(0xFFD1D5DB),
              shape: BoxShape.circle,
            ),
          ),
        ],
      ),
    );
  }

  // ============================================================
  // 복약 카드
  // ============================================================
  Widget _buildMedicationCard({
    required Map<String, dynamic> medication,
    required List<dynamic> items,
  }) {
    return Container(
      decoration: _cardDecoration(),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 12),
            child: Column(
              children: [
                Row(
                  children: [
                    const Icon(
                      Icons.calendar_today_outlined,
                      color: Color(0xFF1E3A5F),
                      size: 25,
                    ),
                    const SizedBox(width: 10),
                    const Expanded(
                      child: Text(
                        '오늘의 복약',
                        style: TextStyle(
                          color: textColor,
                          fontSize: 20,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                    const Icon(
                      Icons.check_circle_outline_rounded,
                      color: primaryColor,
                      size: 25,
                    ),
                    const SizedBox(width: 5),
                    Text(
                      '${medication['completed_count']}/'
                      '${medication['total_count']} 완료',
                      style: const TextStyle(
                        color: subTextColor,
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 12),

                Align(
                  alignment: Alignment.centerLeft,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 11,
                      vertical: 5,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF3F7FF),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFF93B4FF)),
                    ),
                    child: Text(
                      medication['date'] as String,
                      style: const TextStyle(
                        color: primaryColor,
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),

          const Divider(height: 1, color: Color(0xFFE5E7EB)),

          ...items.map((itemData) {
            final item = itemData as Map<String, dynamic>;

            return _buildMedicationItem(item);
          }),
        ],
      ),
    );
  }

  Widget _buildMedicationItem(Map<String, dynamic> item) {
    final isPurple = item['icon_type'] == 'purple';

    final iconColor = isPurple ? const Color(0xFF8B5CF6) : primaryColor;

    final iconBackground = isPurple
        ? const Color(0xFFF3EEFF)
        : const Color(0xFFEAF2FF);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Color(0xFFE5E7EB))),
      ),
      child: Row(
        children: [
          Container(
            width: 54,
            height: 54,
            decoration: BoxDecoration(
              color: iconBackground,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Icon(Icons.medication_outlined, color: iconColor, size: 31),
          ),

          const SizedBox(width: 14),

          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item['name'] as String,
                  style: const TextStyle(
                    color: textColor,
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    const Icon(
                      Icons.access_time_rounded,
                      size: 17,
                      color: subTextColor,
                    ),
                    const SizedBox(width: 5),
                    Text(
                      '${item['time']} 알림',
                      style: const TextStyle(color: subTextColor, fontSize: 13),
                    ),
                  ],
                ),
              ],
            ),
          ),

          Container(
            padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 9),
            decoration: BoxDecoration(
              color: const Color(0xFFF8F5FF),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: const Color(0xFFD9CCFF)),
            ),
            child: Text(
              item['status'] as String,
              style: const TextStyle(
                color: Color(0xFF8B5CF6),
                fontSize: 13,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ============================================================
  // 챗봇 버튼
  // ============================================================
  Widget _buildChatbotButton() {
    return FloatingActionButton(
      onPressed: () {
        _showMessage('AI 건강 챗봇은 추후 Gemini와 연결할 예정입니다.');
      },
      backgroundColor: primaryColor,
      foregroundColor: Colors.white,
      elevation: 5,
      tooltip: 'AI 건강 챗봇',
      child: const Icon(Icons.smart_toy_outlined, size: 29),
    );
  }

  // ============================================================
  // 공통 카드 디자인
  // ============================================================
  BoxDecoration _cardDecoration() {
    return BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(22),
      border: Border.all(color: const Color(0xFFE8ECF2)),
      boxShadow: const [
        BoxShadow(
          color: Color(0x120F172A),
          blurRadius: 18,
          offset: Offset(0, 6),
        ),
      ],
    );
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 2),
        ),
      );
  }
}
