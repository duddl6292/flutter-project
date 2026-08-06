import 'dart:async';

import 'package:brainon_mobile/features/patient/providers/favorite_hospitals_provider.dart';
import 'package:brainon_mobile/shared/models/hospital.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class FavoriteHospitalsScreen extends ConsumerStatefulWidget {
  const FavoriteHospitalsScreen({super.key});
  @override
  ConsumerState<FavoriteHospitalsScreen> createState() => _FavoriteHospitalsScreenState();
}

class _FavoriteHospitalsScreenState extends ConsumerState<FavoriteHospitalsScreen> {
  String _query = '';
  Timer? _debounce;

  @override
  void dispose() {
    _debounce?.cancel();
    super.dispose();
  }

  void _search(String value) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 300), () {
      if (mounted) setState(() => _query = value.trim());
    });
  }

  @override
  Widget build(BuildContext context) {
    final data = _query.isEmpty
        ? ref.watch(favoriteHospitalsProvider)
        : ref.watch(hospitalSearchProvider(_query));
    final mutating = ref.watch(favoriteMutationProvider);
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      appBar: AppBar(title: const Text('즐겨찾는 병원')),
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.all(20),
          child: TextField(
            onChanged: _search,
            decoration: const InputDecoration(
              hintText: '병원명, 주소 또는 병원 코드 검색',
              prefixIcon: Icon(Icons.search),
              filled: true,
              fillColor: Colors.white,
            ),
          ),
        ),
        Expanded(
          child: data.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (_, _) => _ErrorView(onRetry: () {
              if (_query.isEmpty) {
                ref.invalidate(favoriteHospitalsProvider);
              } else {
                ref.invalidate(hospitalSearchProvider(_query));
              }
            }),
            data: (hospitals) {
              if (hospitals.isEmpty) {
                return Center(child: Text(_query.isEmpty ? '즐겨찾는 병원이 없습니다.' : '검색 결과가 없습니다.'));
              }
              return RefreshIndicator(
                onRefresh: () async {
                  ref.invalidate(favoriteHospitalsProvider);
                  if (_query.isNotEmpty) ref.invalidate(hospitalSearchProvider(_query));
                  await ref.read(favoriteHospitalsProvider.future);
                },
                child: ListView.separated(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
                  itemCount: hospitals.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 10),
                  itemBuilder: (context, index) => _HospitalCard(
                    hospital: hospitals[index],
                    enabled: !mutating,
                    onToggle: () async {
                      try {
                        await toggleFavorite(ref, hospitals[index]);
                      } catch (_) {
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('즐겨찾기를 변경하지 못했습니다.')));
                        }
                      }
                    },
                  ),
                ),
              );
            },
          ),
        ),
      ]),
    );
  }
}

class _HospitalCard extends StatelessWidget {
  const _HospitalCard({required this.hospital, required this.enabled, required this.onToggle});
  final Hospital hospital;
  final bool enabled;
  final VoidCallback onToggle;
  @override
  Widget build(BuildContext context) => Card(
    child: ListTile(
      contentPadding: const EdgeInsets.all(14),
      leading: const Icon(Icons.local_hospital_outlined),
      title: Text(hospital.hospitalName, style: const TextStyle(fontWeight: FontWeight.w800)),
      subtitle: Text([hospital.address, hospital.phone].where((value) => value.isNotEmpty).join('\n')),
      trailing: IconButton(
        tooltip: hospital.isFavorite ? '즐겨찾기 해제' : '즐겨찾기 등록',
        onPressed: enabled ? onToggle : null,
        icon: Icon(hospital.isFavorite ? Icons.star : Icons.star_border, color: hospital.isFavorite ? Colors.amber : null),
      ),
    ),
  );
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.onRetry});
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
    const Text('병원 정보를 불러오지 못했습니다.'),
    const SizedBox(height: 12),
    OutlinedButton.icon(onPressed: onRetry, icon: const Icon(Icons.refresh), label: const Text('다시 시도')),
  ]));
}
