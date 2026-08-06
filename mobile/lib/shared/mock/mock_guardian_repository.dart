import 'package:brainon_mobile/features/patient/repositories/guardian_repository.dart';
import 'package:brainon_mobile/shared/models/guardian.dart';

class MockGuardianRepository implements GuardianRepository {
  final List<Guardian> _guardians = [
    const Guardian(
      id: 1,
      name: '김민수',
      relationship: '배우자',
      phone: '010-9876-5432',
      emergencyPriority: 1,
    ),
    const Guardian(
      id: 2,
      name: '김영희',
      relationship: '자녀',
      phone: '010-2468-1357',
      emergencyPriority: 2,
    ),
  ];

  int _nextId = 3;

  @override
  Future<List<Guardian>> getGuardians() async {
    await _simulateDelay();
    return _sortedGuardians();
  }

  @override
  Future<Guardian> addGuardian(Guardian guardian) async {
    await _simulateDelay();
    _validatePriority(guardian.emergencyPriority);
    final createdGuardian = guardian.copyWith(id: _nextId++);
    _guardians.add(createdGuardian);
    return createdGuardian;
  }

  @override
  Future<Guardian> updateGuardian(Guardian guardian) async {
    await _simulateDelay();
    final index = _guardians.indexWhere((item) => item.id == guardian.id);
    if (index == -1) {
      throw StateError('수정할 보호자 정보를 찾을 수 없습니다.');
    }
    _validatePriority(guardian.emergencyPriority, excludingId: guardian.id);
    _guardians[index] = guardian;
    return guardian;
  }

  @override
  Future<void> deleteGuardian(int guardianId) async {
    await _simulateDelay();
    final exists = _guardians.any((guardian) => guardian.id == guardianId);
    if (!exists) {
      throw StateError('삭제할 보호자 정보를 찾을 수 없습니다.');
    }
    _guardians.removeWhere((guardian) => guardian.id == guardianId);
  }

  void _validatePriority(int priority, {int? excludingId}) {
    final duplicated = _guardians.any(
      (guardian) =>
          guardian.id != excludingId && guardian.emergencyPriority == priority,
    );
    if (duplicated) {
      throw StateError('$priority순위는 이미 다른 보호자가 사용하고 있습니다.');
    }
  }

  Future<void> _simulateDelay() {
    return Future<void>.delayed(const Duration(milliseconds: 250));
  }

  List<Guardian> _sortedGuardians() {
    final guardians = List<Guardian>.of(_guardians)
      ..sort((a, b) => a.emergencyPriority.compareTo(b.emergencyPriority));
    return guardians;
  }
}
