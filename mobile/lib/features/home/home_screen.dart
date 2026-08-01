import 'package:flutter/material.dart';
import 'package:brainon_mobile/shared/mock/patient_home_mock.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  // 하단 네비게이션에서 현재 선택된 메뉴 번호
  int _selectedBottomIndex = 0;

  // 햄버거 메뉴를 열기 위해 사용하는 Key
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  // 앱의 대표 색상
  static const Color primaryColor = Color(0xFF2563EB);
  static const Color backgroundColor = Color(0xFFF6F8FC);
  static const Color textColor = Color(0xFF111827);
  static const Color subTextColor = Color(0xFF6B7280);

  @override
  Widget build(BuildContext context) {
    // Mock 데이터에서 각 영역의 데이터를 꺼냅니다.
    final patient = patientHomeMock['patient'] as Map<String, dynamic>;

    final nextAppointment =
        patientHomeMock['next_appointment'] as Map<String, dynamic>;

    final upcomingDates = patientHomeMock['upcoming_dates'] as List<dynamic>;

    final medication = patientHomeMock['medication'] as Map<String, dynamic>;

    final medicationItems = medication['items'] as List<dynamic>;

    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: backgroundColor,

      // 왼쪽 햄버거 메뉴를 눌렀을 때 열리는 메뉴
      drawer: _buildDrawer(),

      // 오른쪽 아래 챗봇 버튼
      floatingActionButton: _buildChatbotButton(),

      // 하단 네비게이션 바
      bottomNavigationBar: _buildBottomNavigationBar(),

      body: SafeArea(
        child: Column(
          children: [
            // 상단 햄버거 메뉴 / 로고 / 알림
            _buildTopBar(
              notificationCount: patient['notification_count'] as int,
            ),

            // 스크롤 가능한 본문
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 26, 20, 100),
                child: Center(
                  // Chrome에서 실행해도 모바일 화면처럼 보이게 최대 폭을 제한
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 520),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // 인사말
                        _buildGreetingSection(
                          patientName: patient['name'] as String,
                        ),

                        const SizedBox(height: 24),

                        // 진료 일정 + 다가오는 예약
                        _buildScheduleCard(
                          appointment: nextAppointment,
                          upcomingDates: upcomingDates,
                        ),

                        const SizedBox(height: 18),

                        // 오늘의 복약
                        _buildMedicationCard(
                          medication: medication,
                          items: medicationItems,
                        ),

                        const SizedBox(height: 18),

                        // 진료 일정 등록
                        _buildRegisterScheduleCard(),
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
  // 상단 영역
  // 왼쪽: 햄버거 메뉴
  // 가운데: 호닥 로고
  // 오른쪽: 알림 아이콘
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
          // 가운데 로고
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

          // 왼쪽 햄버거 메뉴
          Positioned(
            left: 12,
            top: 10,
            bottom: 10,
            child: IconButton(
              tooltip: '메뉴',
              onPressed: () {
                _scaffoldKey.currentState?.openDrawer();
              },
              icon: const Icon(Icons.menu_rounded, size: 32, color: textColor),
            ),
          ),

          // 오른쪽 알림 아이콘
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
                    _showMessage('알림 화면은 추후 연결할 예정입니다.');
                  },
                  icon: const Icon(
                    Icons.notifications_none_rounded,
                    size: 32,
                    color: textColor,
                  ),
                ),

                // 알림 개수가 1개 이상일 때만 숫자 배지 표시
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
  // 인사말 영역
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
          style: TextStyle(
            color: subTextColor,
            fontSize: 16,
            fontWeight: FontWeight.w400,
          ),
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
          // 카드 제목
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
                  _showMessage('전체 진료 일정 화면은 추후 연결합니다.');
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

          const SizedBox(height: 12),

          // 가장 가까운 진료 일정
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
                // 왼쪽 날짜 영역
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

                // 진료 상세 정보
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

          // 다가오는 예약
          Row(
            children: [
              const Expanded(
                child: Text(
                  '다가오는 예약',
                  style: TextStyle(
                    color: textColor,
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              TextButton(
                onPressed: () {
                  _showMessage('예약 목록 화면은 추후 연결합니다.');
                },
                child: const Text(
                  '더보기',
                  style: TextStyle(color: subTextColor, fontSize: 13),
                ),
              ),
            ],
          ),

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

  // 진료/검사 등의 상태 표시 Chip
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

  // 다가오는 예약의 날짜 한 칸
  Widget _buildUpcomingDate(Map<String, dynamic> date) {
    final String day = date['day'] as String;
    final bool isSelected = date['is_selected'] as bool;
    final bool hasSchedule = date['has_schedule'] as bool;

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
  // 오늘의 복약 카드
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

          // 약 목록
          ...items.map((itemData) {
            final item = itemData as Map<String, dynamic>;

            return _buildMedicationItem(item);
          }),
        ],
      ),
    );
  }

  // 약 한 개의 정보
  Widget _buildMedicationItem(Map<String, dynamic> item) {
    final bool isPurple = item['icon_type'] == 'purple';

    final Color iconColor = isPurple ? const Color(0xFF8B5CF6) : primaryColor;

    final Color iconBackground = isPurple
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
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 16,
                  height: 16,
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: const Color(0xFFA78BFA),
                      width: 2,
                    ),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 7),
                Text(
                  item['status'] as String,
                  style: const TextStyle(
                    color: Color(0xFF8B5CF6),
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
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
  // 진료 일정 등록 카드
  // ============================================================
  Widget _buildRegisterScheduleCard() {
    return InkWell(
      borderRadius: BorderRadius.circular(20),
      onTap: () {
        _showMessage('진료 일정 등록 화면은 추후 연결합니다.');
      },
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: const Color(0xFFF3F7FF),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: const Color(0xFFCFE0FF)),
        ),
        child: Row(
          children: [
            Container(
              width: 58,
              height: 58,
              decoration: BoxDecoration(
                color: const Color(0xFFDDEAFF),
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Icon(
                Icons.event_available_outlined,
                color: primaryColor,
                size: 31,
              ),
            ),

            const SizedBox(width: 15),

            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '진료 일정 등록하기',
                    style: TextStyle(
                      color: primaryColor,
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  SizedBox(height: 6),
                  Text(
                    '병원에서 받은 일정을 등록하고\n알림을 받아보세요.',
                    style: TextStyle(
                      color: subTextColor,
                      fontSize: 13,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),

            const Icon(
              Icons.chevron_right_rounded,
              color: primaryColor,
              size: 32,
            ),
          ],
        ),
      ),
    );
  }

  // ============================================================
  // 챗봇 플로팅 버튼
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
  // 하단 네비게이션
  // ============================================================
  Widget _buildBottomNavigationBar() {
    return BottomNavigationBar(
      currentIndex: _selectedBottomIndex,
      onTap: (index) {
        setState(() {
          _selectedBottomIndex = index;
        });

        const menuNames = ['홈', '진료 일정', '상담', '내 기록', '마이페이지'];

        if (index != 0) {
          _showMessage('${menuNames[index]} 화면은 추후 연결합니다.');
        }
      },
      type: BottomNavigationBarType.fixed,
      backgroundColor: Colors.white,
      selectedItemColor: primaryColor,
      unselectedItemColor: const Color(0xFF8B8F98),
      selectedFontSize: 12,
      unselectedFontSize: 12,
      selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w700),
      elevation: 12,
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.home_outlined),
          activeIcon: Icon(Icons.home_rounded),
          label: '홈',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.calendar_month_outlined),
          activeIcon: Icon(Icons.calendar_month_rounded),
          label: '진료 일정',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.chat_bubble_outline_rounded),
          activeIcon: Icon(Icons.chat_bubble_rounded),
          label: '상담',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.folder_outlined),
          activeIcon: Icon(Icons.folder_rounded),
          label: '내 기록',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person_outline_rounded),
          activeIcon: Icon(Icons.person_rounded),
          label: '마이페이지',
        ),
      ],
    );
  }

  // ============================================================
  // 햄버거 메뉴 Drawer
  // ============================================================
  Widget _buildDrawer() {
    return Drawer(
      backgroundColor: Colors.white,
      child: SafeArea(
        child: Column(
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(22, 24, 22, 20),
              color: const Color(0xFFF3F7FF),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Image.asset(
                    'assets/images/logo.png',
                    width: 105,
                    fit: BoxFit.contain,
                  ),
                  const SizedBox(height: 18),
                  const Text(
                    '김지환님',
                    style: TextStyle(
                      color: textColor,
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    '오늘도 건강한 하루 되세요.',
                    style: TextStyle(color: subTextColor, fontSize: 13),
                  ),
                ],
              ),
            ),
            _buildDrawerItem(icon: Icons.home_outlined, title: '홈'),
            _buildDrawerItem(
              icon: Icons.calendar_month_outlined,
              title: '진료 일정',
            ),
            _buildDrawerItem(icon: Icons.medication_outlined, title: '복약 관리'),
            _buildDrawerItem(icon: Icons.description_outlined, title: '검사 결과'),
            _buildDrawerItem(icon: Icons.emergency_outlined, title: '응급 증상 안내'),
            const Spacer(),
            const Divider(height: 1),
            _buildDrawerItem(icon: Icons.logout_rounded, title: '로그아웃'),
            const SizedBox(height: 10),
          ],
        ),
      ),
    );
  }

  Widget _buildDrawerItem({required IconData icon, required String title}) {
    return ListTile(
      leading: Icon(icon, color: const Color(0xFF4B5563)),
      title: Text(
        title,
        style: const TextStyle(
          color: textColor,
          fontSize: 15,
          fontWeight: FontWeight.w600,
        ),
      ),
      trailing: const Icon(
        Icons.chevron_right_rounded,
        color: Color(0xFF9CA3AF),
      ),
      onTap: () {
        Navigator.pop(context);
        _showMessage('$title 화면은 추후 연결합니다.');
      },
    );
  }

  // 카드 공통 디자인
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

  // 아직 구현되지 않은 기능을 임시로 알려주는 메시지
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
