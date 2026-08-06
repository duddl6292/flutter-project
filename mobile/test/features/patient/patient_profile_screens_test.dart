import 'package:brainon_mobile/features/home/home_screen.dart';
import 'package:brainon_mobile/features/medication/providers/medication_provider.dart';
import 'package:brainon_mobile/features/patient/my_page_screen.dart';
import 'package:brainon_mobile/features/patient/providers/patient_profile_provider.dart';
import 'package:brainon_mobile/shared/models/medication.dart';
import 'package:brainon_mobile/shared/models/patient_profile.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const profile = PatientProfile(
    id: 'fd911ac9-3965-4a76-bc72-13d207f0fa41',
    userId: '90a6c756-2168-4492-a4cc-bf92291cafe8',
    username: 'patient01',
    role: 'PATIENT',
    name: '공통프로필',
    email: 'patient01@example.com',
    patientNumber: 'BRN-2026-000006',
  );

  testWidgets('HomeScreen and MyPageScreen show the same profile name', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          patientProfileProvider.overrideWith((ref) async => profile),
          todayMedicationsProvider.overrideWith(
            (ref) async => const <Medication>[],
          ),
        ],
        child: MaterialApp(
          home: HomeScreen(onOpenDrawer: () {}, onOpenAppointment: () {}),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('안녕하세요, 공통프로필님!'), findsOneWidget);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          patientProfileProvider.overrideWith((ref) async => profile),
        ],
        child: MaterialApp(home: MyPageScreen(onOpenDrawer: () {})),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('공통프로필님'), findsOneWidget);
  });
}
