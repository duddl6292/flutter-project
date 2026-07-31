import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('BrainOn')),
      body: const Center(child: Text('환자용 뇌졸중 관리 서비스 입니다')),
    );
  }
}
