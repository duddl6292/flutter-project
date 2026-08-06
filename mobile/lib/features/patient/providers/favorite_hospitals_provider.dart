import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/patient/repositories/api_favorite_hospital_repository.dart';
import 'package:brainon_mobile/features/patient/repositories/favorite_hospital_repository.dart';
import 'package:brainon_mobile/shared/models/hospital.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final favoriteHospitalRepositoryProvider = Provider<FavoriteHospitalRepository>(
  (ref) => ApiFavoriteHospitalRepository(ref.watch(apiClientProvider)),
);

final favoriteHospitalsProvider = FutureProvider<List<Hospital>>(
  (ref) => ref.watch(favoriteHospitalRepositoryProvider).getFavoriteHospitals(),
);

final hospitalSearchProvider = FutureProvider.autoDispose.family<List<Hospital>, String>((ref, query) async {
  final repository = ref.watch(favoriteHospitalRepositoryProvider);
  final results = await repository.searchHospitals(query);
  final favorites = await ref.watch(favoriteHospitalsProvider.future);
  final ids = favorites.map((item) => item.hospitalId).toSet();
  return results.map((item) => item.copyWith(isFavorite: ids.contains(item.hospitalId))).toList();
});

final favoriteMutationProvider = StateProvider.autoDispose<bool>((ref) => false);

Future<void> toggleFavorite(WidgetRef ref, Hospital hospital) async {
  if (ref.read(favoriteMutationProvider)) return;
  ref.read(favoriteMutationProvider.notifier).state = true;
  try {
    final repository = ref.read(favoriteHospitalRepositoryProvider);
    if (hospital.isFavorite) {
      await repository.removeFavoriteHospital(hospital.hospitalId);
    } else {
      await repository.addFavoriteHospital(hospital);
    }
    ref.invalidate(favoriteHospitalsProvider);
    ref.invalidate(hospitalSearchProvider);
  } finally {
    ref.read(favoriteMutationProvider.notifier).state = false;
  }
}
