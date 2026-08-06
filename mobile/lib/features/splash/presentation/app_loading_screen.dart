import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class AppLoadingScreen extends StatefulWidget {
  const AppLoadingScreen({super.key});

  @override
  State<AppLoadingScreen> createState() => _AppLoadingScreenState();
}

class _AppLoadingScreenState extends State<AppLoadingScreen> {
  static const List<String> _frames = [
    'assets/images/splash/hojjang_run/hojjang_run_1.png',
    'assets/images/splash/hojjang_run/hojjang_run_2.png',
    'assets/images/splash/hojjang_run/hojjang_run_3.png',
    'assets/images/splash/hojjang_run/hojjang_run_4.png',
  ];

  Timer? _animationTimer;
  Timer? _navigationTimer;
  int _currentFrame = 0;
  int _activeDot = 0;

  @override
  void initState() {
    super.initState();

    _animationTimer = Timer.periodic(const Duration(milliseconds: 140), (_) {
      if (!mounted) return;

      setState(() {
        _currentFrame = (_currentFrame + 1) % _frames.length;
        _activeDot = (_activeDot + 1) % 3;
      });
    });

    _navigationTimer = Timer(const Duration(milliseconds: 1800), () {
      if (!mounted) return;
      context.go('/');
    });
  }

  @override
  void dispose() {
    _animationTimer?.cancel();
    _navigationTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFF),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.asset(
              _frames[_currentFrame],
              width: 220,
              height: 220,
              fit: BoxFit.contain,
              gaplessPlayback: true,
            ),
            const SizedBox(height: 12),
            const Text(
              '호닥',
              style: TextStyle(
                color: Color(0xFF1F2937),
                fontSize: 28,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              '건강 정보를 준비하고 있어요',
              style: TextStyle(
                color: Color(0xFF6B7280),
                fontSize: 15,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (index) {
                final isActive = index == _activeDot;
                return AnimatedContainer(
                  duration: const Duration(milliseconds: 140),
                  width: isActive ? 10 : 7,
                  height: isActive ? 10 : 7,
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  decoration: BoxDecoration(
                    color: isActive
                        ? const Color(0xFF356A9A)
                        : const Color(0xFFD4DEEA),
                    shape: BoxShape.circle,
                  ),
                );
              }),
            ),
          ],
        ),
      ),
    );
  }
}
