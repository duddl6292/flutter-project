import 'package:brainon_mobile/features/patient/repositories/favorite_hospital_repository.dart';
import 'package:brainon_mobile/shared/mock/hospital_mock.dart';
import 'package:brainon_mobile/shared/models/hospital.dart';

class MockFavoriteHospitalRepository implements FavoriteHospitalRepository {
  MockFavoriteHospitalRepository()
    : _favorites = hospitalMockList
          .map(Hospital.fromJson)
          .where((hospital) => hospital.isFavorite)
          .toList();

  final List<Hospital> _favorites;

  @override
  Future<List<Hospital>> getFavoriteHospitals() async {
    await _simulateDelay();
    return List<Hospital>.unmodifiable(_favorites);
  }

  @override
  Future<void> addFavoriteHospital(Hospital hospital) async {
    await _simulateDelay();
    final exists = _favorites.any(
      (favorite) => favorite.hospitalId == hospital.hospitalId,
    );
    if (!exists) {
      _favorites.add(hospital.copyWith(isFavorite: true));
    }
  }

  @override
  Future<void> removeFavoriteHospital(String hospitalId) async {
    await _simulateDelay();
    _favorites.removeWhere((hospital) => hospital.hospitalId == hospitalId);
  }

  Future<void> _simulateDelay() {
    return Future<void>.delayed(const Duration(milliseconds: 150));
  }
}
