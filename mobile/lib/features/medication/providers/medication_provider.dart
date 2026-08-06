import 'package:brainon_mobile/features/medication/repositories/medication_repository.dart';
import 'package:brainon_mobile/shared/models/medication.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final todayMedicationsProvider = FutureProvider<List<Medication>>(
  (ref) => ref.watch(medicationRepositoryProvider).getTodayMedications(),
);
