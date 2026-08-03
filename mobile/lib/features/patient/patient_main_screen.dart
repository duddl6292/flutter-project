import 'package:brainon_mobile/features/appointment/appointment_create_screen.dart';
import 'package:brainon_mobile/features/home/home_screen.dart';
import 'package:brainon_mobile/features/patient/emergency_guide_screen.dart';
import 'package:brainon_mobile/features/patient/my_page_screen.dart';
import 'package:brainon_mobile/features/patient/test_result_screen.dart';
import 'package:flutter/material.dart';

class PatientMainScreen extends StatefulWidget {
  const PatientMainScreen({super.key});

  @override
  State<PatientMainScreen> createState() =>
      _PatientMainScreenState();
}

class _PatientMainScreenState
    extends State<PatientMainScreen> {
  int _selectedIndex = 0;

  static const List<Widget> _screens = [
    HomeScreen(),
    AppointmentCreateScreen(),
    EmergencyGuideScreen(),
    TestResultScreen(),
    MyPageScreen(),
  ];

  void _onDestinationSelected(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: _onDestinationSelected,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: '홈',
          ),
          NavigationDestination(
            icon: Icon(Icons.calendar_month_outlined),
            selectedIcon: Icon(Icons.calendar_month_rounded),
            label: '예약',
          ),
          NavigationDestination(
            icon: Icon(
              Icons.emergency_outlined,
              color: Color(0xFFDC2626),
            ),
            selectedIcon: Icon(
              Icons.emergency_rounded,
              color: Color(0xFFDC2626),
            ),
            label: '응급',
          ),
          NavigationDestination(
            icon: Icon(Icons.description_outlined),
            selectedIcon: Icon(Icons.description_rounded),
            label: '검사결과',
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
}