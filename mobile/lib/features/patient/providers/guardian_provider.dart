import 'package:brainon_mobile/features/patient/repositories/guardian_repository.dart';
import 'package:brainon_mobile/shared/mock/mock_guardian_repository.dart';
import 'package:brainon_mobile/shared/models/guardian.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final guardianRepositoryProvider = Provider<GuardianRepository>((ref) {
  return MockGuardianRepository();
});

final guardianProvider =
    NotifierProvider<GuardianNotifier, AsyncValue<List<Guardian>>>(
      GuardianNotifier.new,
    );

class GuardianNotifier extends Notifier<AsyncValue<List<Guardian>>> {
  GuardianRepository get _repository => ref.read(guardianRepositoryProvider);

  bool _isMutating = false;

  @override
  AsyncValue<List<Guardian>> build() {
    Future<void>.microtask(loadGuardians);
    return const AsyncValue.loading();
  }

  Future<void> loadGuardians() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(_repository.getGuardians);
  }

  Future<void> addGuardian(Guardian guardian) async {
    await _runMutation(() => _repository.addGuardian(guardian));
  }

  Future<void> updateGuardian(Guardian guardian) async {
    await _runMutation(() => _repository.updateGuardian(guardian));
  }

  Future<void> deleteGuardian(int guardianId) async {
    await _runMutation(() => _repository.deleteGuardian(guardianId));
  }

  Future<void> _runMutation(Future<Object?> Function() mutation) async {
    if (_isMutating) {
      throw StateError('보호자 정보를 처리하고 있습니다. 잠시 후 다시 시도해 주세요.');
    }

    _isMutating = true;
    state = const AsyncValue.loading();

    try {
      await mutation();
      state = AsyncValue.data(await _repository.getGuardians());
    } on Object catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
      rethrow;
    } finally {
      _isMutating = false;
    }
  }
}
