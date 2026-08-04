import 'package:brainon_mobile/shared/models/guardian.dart';

abstract interface class GuardianRepository {
  Future<List<Guardian>> getGuardians();

  Future<Guardian> addGuardian(Guardian guardian);

  Future<Guardian> updateGuardian(Guardian guardian);

  Future<void> deleteGuardian(int guardianId);
}
