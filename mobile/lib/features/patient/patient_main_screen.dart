import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/appointment/appointment_create_screen.dart';
import 'package:brainon_mobile/features/emergency/emergency_guide_screen.dart';
import 'package:brainon_mobile/features/emergency/repository/emergency_repository.dart';
import 'package:brainon_mobile/features/home/home_screen.dart';
import 'package:brainon_mobile/features/medication/medication_list_screen.dart';
import 'package:brainon_mobile/features/patient/my_page_screen.dart';
import 'package:brainon_mobile/features/patient/test_results/patient_test_result_screen.dart';
import 'package:brainon_mobile/shared/mock/patient_home_mock.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class PatientMainScreen extends ConsumerStatefulWidget {
  const PatientMainScreen({super.key});

  @override
  ConsumerState<PatientMainScreen> createState() => _PatientMainScreenState();
}

class _PatientMainScreenState extends ConsumerState<PatientMainScreen> {
  // 모든 탭에서 공통 Drawer를 열기 위한 키
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  // 응급안내 API 호출용 Repository
  late final HttpEmergencyRepository _emergencyRepository;

  // 0: 예약
  // 1: 검사결과
  // 2: 홈
  // 3: 응급안내
  // 4: 마이페이지
  int _selectedIndex = 2;

  // 현재는 Mock 데이터에서 환자 이름을 가져옵니다.
  // 백엔드 로그인 연결 후에는 로그인 사용자 정보로 교체하면 됩니다.
  String get _patientName {
    final patient = patientHomeMock['patient'] as Map<String, dynamic>;

    return patient['name'] as String? ?? '사용자';
  }

  @override
  void initState() {
    super.initState();

    _emergencyRepository = HttpEmergencyRepository(
      // Chrome에서 로컬 백엔드를 실행할 때 사용하는 주소입니다.
      baseUrl: 'http://localhost:8000',
    );
  }

  @override
  void dispose() {
    _emergencyRepository.dispose();
    super.dispose();
  }

  List<Widget> get _screens {
    return [
      AppointmentCreateScreen(onOpenDrawer: _openDrawer),

      PatientTestResultScreen(onOpenDrawer: _openDrawer),

      HomeScreen(
        onOpenDrawer: _openDrawer,
        onOpenAppointment: () {
          _moveToTab(0);
        },
      ),

      EmergencyGuideScreen(
        onOpenDrawer: _openDrawer,
        repository: _emergencyRepository,

        // 로그인 연결 후 실제 환자 ID로 교체합니다.
        patientId: 1,

        // JWT 등의 인증 토큰이 생기면 전달합니다.
        accessToken: null,
      ),

      MyPageScreen(onOpenDrawer: _openDrawer),
    ];
  }

  void _openDrawer() {
    _scaffoldKey.currentState?.openDrawer();
  }

  void _moveToTab(int index) {
    if (index < 0 || index >= _screens.length) {
      return;
    }

    setState(() {
      _selectedIndex = index;
    });
  }

  void _onDestinationSelected(int index) {
    _moveToTab(index);
  }

  void _closeDrawerAndMoveToTab(int index) {
    Navigator.of(context).pop();

    setState(() {
      _selectedIndex = index;
    });
  }

  void _closeDrawer() {
    Navigator.of(context).pop();
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: const Color(0xFFF6F8FC),
      drawer: _buildDrawer(),
      body: IndexedStack(index: _selectedIndex, children: _screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: _onDestinationSelected,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.calendar_month_outlined),
            selectedIcon: Icon(Icons.calendar_month_rounded),
            label: '예약',
          ),
          NavigationDestination(
            icon: Icon(Icons.description_outlined),
            selectedIcon: Icon(Icons.description_rounded),
            label: '검사결과',
          ),
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: '홈',
          ),
          NavigationDestination(
            icon: Icon(Icons.emergency_outlined, color: Color(0xFFDC2626)),
            selectedIcon: Icon(
              Icons.emergency_rounded,
              color: Color(0xFFDC2626),
            ),
            label: '응급',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person_rounded),
            label: '마이',
          ),
        ],
      ),
    );
  }

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
                  Text(
                    '$_patientName님',
                    style: const TextStyle(
                      color: Color(0xFF111827),
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    '오늘도 건강한 하루 되세요.',
                    style: TextStyle(color: Color(0xFF6B7280), fontSize: 13),
                  ),
                ],
              ),
            ),

            _buildDrawerItem(
              icon: Icons.home_outlined,
              title: '홈',
              onTap: () {
                _closeDrawerAndMoveToTab(2);
              },
            ),

            _buildDrawerItem(
              icon: Icons.calendar_month_outlined,
              title: '예약',
              onTap: () {
                _closeDrawerAndMoveToTab(0);
              },
            ),

            _buildDrawerItem(
              icon: Icons.description_outlined,
              title: '검사결과',
              onTap: () {
                _closeDrawerAndMoveToTab(1);
              },
            ),

            _buildDrawerItem(
              icon: Icons.medication_outlined,
              title: '복약관리',
              onTap: () {
                _closeDrawer();

                Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (context) {
                      return const MedicationListScreen();
                    },
                  ),
                );
              },
            ),

            _buildDrawerItem(
              icon: Icons.favorite_border_rounded,
              title: '찜한 병원',
              onTap: () {
                _closeDrawer();
                context.pushNamed(RouteNames.favoriteHospitals);
              },
            ),

            _buildDrawerItem(
              icon: Icons.notifications_outlined,
              title: '알림설정',
              onTap: () {
                _closeDrawer();
                _showMessage('알림 설정 화면은 다음 단계에서 연결합니다.');
              },
            ),

            _buildDrawerItem(
              icon: Icons.emergency_outlined,
              title: '응급안내',
              iconColor: const Color(0xFFDC2626),
              onTap: () {
                _closeDrawerAndMoveToTab(3);
              },
            ),

            _buildDrawerItem(
              icon: Icons.person_outline_rounded,
              title: '마이페이지',
              onTap: () {
                _closeDrawerAndMoveToTab(4);
              },
            ),

            const Spacer(),
            const Divider(height: 1),

            _buildDrawerItem(
              icon: Icons.logout_rounded,
              title: '로그아웃',
              onTap: () async {
                _closeDrawer();
                await ref.read(authProvider.notifier).logout();
              },
            ),

            const SizedBox(height: 10),
          ],
        ),
      ),
    );
  }

  Widget _buildDrawerItem({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
    Color iconColor = const Color(0xFF4B5563),
  }) {
    return ListTile(
      leading: Icon(icon, color: iconColor),
      title: Text(
        title,
        style: const TextStyle(
          color: Color(0xFF111827),
          fontSize: 15,
          fontWeight: FontWeight.w600,
        ),
      ),
      trailing: const Icon(
        Icons.chevron_right_rounded,
        color: Color(0xFF9CA3AF),
      ),
      onTap: onTap,
    );
  }
}
