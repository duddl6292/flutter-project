import 'package:brainon_mobile/features/clinician/widgets/clinician_tab_header.dart';
import 'package:flutter/material.dart';

class ClinicianDetailScaffold extends StatelessWidget {
  const ClinicianDetailScaffold({
    required this.title,
    required this.body,
    super.key,
  });
  final String title;
  final Widget body;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8FC),
      body: SafeArea(
        child: Column(
          children: [
            ClinicianTabHeader(title: title, showBackButton: true),
            Expanded(child: body),
          ],
        ),
      ),
    );
  }
}
