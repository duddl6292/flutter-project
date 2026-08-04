import 'package:brainon_mobile/shared/models/hospital.dart';

abstract interface class FavoriteHospitalRepository {
  Future<List<Hospital>> getFavoriteHospitals();

  Future<void> addFavoriteHospital(Hospital hospital);

  Future<void> removeFavoriteHospital(String hospitalId);
}
