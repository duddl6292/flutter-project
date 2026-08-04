import 'package:flutter/material.dart';

class MyPageScreen extends StatefulWidget {
  const MyPageScreen({required this.onOpenDrawer, super.key});

  final VoidCallback onOpenDrawer;

  @override
  State<MyPageScreen> createState() => _MyPageScreenState();
}

class _MyPageScreenState extends State<MyPageScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),

            const Expanded(
              child: Center(
                child: Text(
                  '마이페이지 화면 준비 중',
                  style: TextStyle(
                    color: Color(0xFF111827),
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
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
  // 마이페이지 상단바
  // ------------------------------------------------------------
  // 왼쪽 햄버거 버튼은 PatientMainScreen의 Drawer를 엽니다.
  // ============================================================
  Widget _buildHeader() {
    return Container(
      height: 76,
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(bottom: BorderSide(color: Color(0xFFE5E7EB))),
      ),
      child: Stack(
        children: [
          const Positioned.fill(
            child: Align(
              alignment: Alignment.center,
              child: Text(
                '마이페이지',
                style: TextStyle(
                  color: Color(0xFF111827),
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
              onPressed: widget.onOpenDrawer,
              icon: const Icon(
                Icons.menu_rounded,
                size: 32,
                color: Color(0xFF111827),
              ),
            ),
          ),

          Positioned(
            right: 12,
            top: 10,
            bottom: 10,
            child: IconButton(
              tooltip: '알림',
              onPressed: () {},
              icon: const Icon(
                Icons.notifications_none_rounded,
                size: 32,
                color: Color(0xFF111827),
              ),
            ),
          ),
        ],
      ),
    );
  } // _buildHeader 끝
} // _MyPageScreenState 끝
