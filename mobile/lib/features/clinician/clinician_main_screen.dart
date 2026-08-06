import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/features/clinician/appointments/clinician_schedule_screen.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_screen.dart';
import 'package:brainon_mobile/features/clinician/drawer/clinician_drawer.dart';
import 'package:brainon_mobile/features/clinician/home/clinician_home_screen.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_screen.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_my_page_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianMainScreen extends ConsumerStatefulWidget {
  const ClinicianMainScreen({super.key});

  @override
  ConsumerState<ClinicianMainScreen> createState() =>
      _ClinicianMainScreenState();
}

class _ClinicianMainScreenState extends ConsumerState<ClinicianMainScreen> {
  static const _background = Color(0xFFF6F8FC);

  final _scaffoldKey = GlobalKey<ScaffoldState>();

  // 하단 네비게이션 기본 선택: 홈
  int _selectedIndex = 2;

  // ==========================================================
  // 하단 탭 변경
  // 0 환자 / 1 일정 / 2 홈 / 3 협진 / 4 마이
  // ==========================================================
  void _selectTab(int index) {
    if (index < 0 || index > 4) {
      return;
    }

    setState(() {
      _selectedIndex = index;
    });
  }

  // 의료진 홈의 햄버거 버튼에서 Drawer 열기
  void _openDrawer() {
    _scaffoldKey.currentState?.openDrawer();
  }

  @override
  Widget build(BuildContext context) {
    final authUser = ref.watch(authProvider).user;

    final clinician = authUser?.role == UserRole.clinician
        ? authUser?.clinician
        : null;

    final name = clinician?.name ?? '이현우';

    // clinician_home_screen.dart에서 진료과 이름만 표시하므로
    // '전문의' 문구는 여기서 붙이지 않는다.
    final department = clinician?.departmentName ?? '신경과';

    final screens = <Widget>[
      // 0. 환자
      ClinicianPatientScreen(onOpenDrawer: _openDrawer),

      // 1. 일정
      ClinicianScheduleScreen(onOpenDrawer: _openDrawer),

      // 2. 홈
      ClinicianHomeScreen(
        clinicianName: name,
        departmentName: department,
        onOpenDrawer: _openDrawer,
        onSelectTab: _selectTab,
      ),

      // 3. 협진
      ClinicianConsultationScreen(onOpenDrawer: _openDrawer),

      // 4. 마이
      ClinicianMyPageScreen(onOpenDrawer: _openDrawer),
    ];

    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: _background,

      // 새로 만든 의료진 햄버거 메뉴
      drawer: ClinicianDrawer(onSelectTab: _selectTab),

      // 하단 탭 화면의 상태를 유지하기 위해 IndexedStack 사용
      body: IndexedStack(index: _selectedIndex, children: screens),

      bottomNavigationBar: NavigationBar(
        height: 72,
        backgroundColor: Colors.white,
        indicatorColor: const Color(0xFFDCEBFF),
        selectedIndex: _selectedIndex,
        onDestinationSelected: _selectTab,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.people_alt_outlined),
            selectedIcon: Icon(Icons.people_alt_rounded),
            label: '환자',
          ),
          NavigationDestination(
            icon: Icon(Icons.calendar_month_outlined),
            selectedIcon: Icon(Icons.calendar_month_rounded),
            label: '일정',
          ),
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: '홈',
          ),
          NavigationDestination(
            icon: Badge(label: Text('2'), child: Icon(Icons.groups_2_outlined)),
            selectedIcon: Badge(
              label: Text('2'),
              child: Icon(Icons.groups_2_rounded),
            ),
            label: '협진',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline_rounded),
            selectedIcon: Icon(Icons.person_rounded),
            label: '마이',
          ),
        ],
      ),
    );
  }
}
