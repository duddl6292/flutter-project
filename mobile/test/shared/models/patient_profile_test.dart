import 'package:brainon_mobile/shared/models/patient_profile.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('PatientProfile.fromJson', () {
    test('parses the actual patients/me response fields', () {
      final profile = PatientProfile.fromJson({
        'patient_id': 'fd911ac9-3965-4a76-bc72-13d207f0fa41',
        'user_id': '90a6c756-2168-4492-a4cc-bf92291cafe8',
        'username': 'patient01',
        'email': 'patient01@example.com',
        'medical_record_number': 'BRN-2026-000006',
        'name': '강승현',
        'birth_date': '1987-07-13',
        'sex': 'F',
        'phone': '010-0000-0006',
        'emergency_contact': '010-9000-0006',
        'address': '서울특별시 종로구',
        'status': 'ACTIVE',
      });

      expect(profile.id, 'fd911ac9-3965-4a76-bc72-13d207f0fa41');
      expect(profile.userId, '90a6c756-2168-4492-a4cc-bf92291cafe8');
      expect(profile.username, 'patient01');
      expect(profile.email, 'patient01@example.com');
      expect(profile.patientNumber, 'BRN-2026-000006');
      expect(profile.name, '강승현');
      expect(profile.birthDate, DateTime(1987, 7, 13));
      expect(profile.sex, 'F');
      expect(profile.emergencyContact, '010-9000-0006');
      expect(profile.address, '서울특별시 종로구');
      expect(profile.status, 'ACTIVE');
    });

    test('keeps nullable values null and ignores an invalid birth date', () {
      final profile = PatientProfile.fromJson({
        'patient_id': 'fd911ac9-3965-4a76-bc72-13d207f0fa41',
        'user_id': null,
        'username': null,
        'email': '',
        'medical_record_number': null,
        'name': '  ',
        'birth_date': 'not-a-date',
        'sex': null,
        'phone': '',
        'emergency_contact': null,
        'address': '',
        'status': null,
      });

      expect(profile.id, 'fd911ac9-3965-4a76-bc72-13d207f0fa41');
      expect(profile.userId, isNull);
      expect(profile.username, isEmpty);
      expect(profile.email, isNull);
      expect(profile.patientNumber, isNull);
      expect(profile.name, isNull);
      expect(profile.birthDate, isNull);
      expect(profile.sex, isNull);
      expect(profile.phone, isNull);
      expect(profile.emergencyContact, isNull);
      expect(profile.address, isNull);
      expect(profile.status, isNull);
    });
  });
}
