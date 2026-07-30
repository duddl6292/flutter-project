import 'package:brainon_mobile/app/app_theme.dart';
import 'package:brainon_mobile/features/home/home_screen.dart';
import 'package:flutter/material.dart';

class BrainOnApp extends StatelessWidget {
  const BrainOnApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BrainOn',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: const HomeScreen(),
    );
  }
}
