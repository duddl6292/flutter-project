import 'package:brainon_mobile/features/patient/repositories/favorite_hospital_repository.dart';
import 'package:brainon_mobile/shared/mock/mock_favorite_hospital_repository.dart';
import 'package:brainon_mobile/shared/models/hospital.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final favoriteHospitalRepositoryProvider = Provider<FavoriteHospitalRepository>(
  (ref) {
    return MockFavoriteHospitalRepository();
  },
);

final favoriteHospitalsProvider =
    AsyncNotifierProvider<FavoriteHospitalsNotifier, List<Hospital>>(
      FavoriteHospitalsNotifier.new,
    );

class FavoriteHospitalsNotifier extends AsyncNotifier<List<Hospital>> {
  FavoriteHospitalRepository get _repository {
    return ref.read(favoriteHospitalRepositoryProvider);
  }

  @override
  Future<List<Hospital>> build() {
    return _repository.getFavoriteHospitals();
  }

  Future<void> toggleFavorite(Hospital hospital) async {
    final previous = state.valueOrNull ?? const <Hospital>[];
    final isFavorite = previous.any(
      (favorite) => favorite.hospitalId == hospital.hospitalId,
    );

    if (isFavorite) {
      state = AsyncValue.data(
        previous
            .where((favorite) => favorite.hospitalId != hospital.hospitalId)
            .toList(),
      );
    } else {
      state = AsyncValue.data([
        ...previous,
        hospital.copyWith(isFavorite: true),
      ]);
    }

    try {
      if (isFavorite) {
        await _repository.removeFavoriteHospital(hospital.hospitalId);
      } else {
        await _repository.addFavoriteHospital(hospital);
      }
    } on Object catch (error, stackTrace) {
      state = AsyncValue.data(previous);
      Error.throwWithStackTrace(error, stackTrace);
    }
  }
}
