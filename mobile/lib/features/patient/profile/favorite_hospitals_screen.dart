import 'package:brainon_mobile/features/patient/providers/favorite_hospitals_provider.dart';
import 'package:brainon_mobile/shared/models/hospital.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class FavoriteHospitalsScreen extends ConsumerWidget {
  const FavoriteHospitalsScreen({super.key});

  static const Color _backgroundColor = Color(0xFFF7F9FC);
  static const Color _primaryColor = Color(0xFF28669E);
  static const Color _primaryTextColor = Color(0xFF111827);
  static const Color _secondaryTextColor = Color(0xFF6B7280);
  static const Color _borderColor = Color(0xFFE5E7EB);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final favoritesAsync = ref.watch(favoriteHospitalsProvider);

    return Scaffold(
      backgroundColor: _backgroundColor,
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          tooltip: '뒤로가기',
          onPressed: () => Navigator.of(context).pop(),
          icon: const Icon(Icons.arrow_back_rounded),
        ),
        title: const Text(
          '즐겨찾는 병원',
          style: TextStyle(
            color: _primaryTextColor,
            fontSize: 20,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: favoritesAsync.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stackTrace) => _buildErrorView(ref),
          data: (favorites) {
            if (favorites.isEmpty) return _buildEmptyView();
            return ListView.separated(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 36),
              itemCount: favorites.length,
              separatorBuilder: (context, index) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                return _buildHospitalCard(context, ref, favorites[index]);
              },
            );
          },
        ),
      ),
    );
  }

  Widget _buildErrorView(WidgetRef ref) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.error_outline_rounded,
            size: 54,
            color: _secondaryTextColor,
          ),
          const SizedBox(height: 16),
          const Text(
            '즐겨찾는 병원을 불러오지 못했습니다.',
            style: TextStyle(
              color: _primaryTextColor,
              fontSize: 17,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 18),
          OutlinedButton.icon(
            onPressed: () => ref.invalidate(favoriteHospitalsProvider),
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('다시 시도'),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyView() {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.star_border_rounded,
              size: 64,
              color: _secondaryTextColor,
            ),
            SizedBox(height: 16),
            Text(
              '즐겨찾는 병원이 없습니다.',
              style: TextStyle(
                color: _primaryTextColor,
                fontSize: 17,
                fontWeight: FontWeight.w700,
              ),
            ),
            SizedBox(height: 6),
            Text(
              '병원 선택 화면에서 별을 눌러 추가할 수 있어요.',
              textAlign: TextAlign.center,
              style: TextStyle(color: _secondaryTextColor, fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHospitalCard(
    BuildContext context,
    WidgetRef ref,
    Hospital hospital,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _borderColor),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: const Color(0xFFEAF2FA),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Icon(
              Icons.local_hospital_outlined,
              color: _primaryColor,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  hospital.hospitalName,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: _primaryTextColor,
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                if (hospital.address.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Text(
                    hospital.address,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: _secondaryTextColor,
                      fontSize: 12,
                    ),
                  ),
                ],
              ],
            ),
          ),
          IconButton(
            tooltip: '즐겨찾기 해제',
            onPressed: () => _removeFavorite(context, ref, hospital),
            icon: const Icon(
              Icons.star_rounded,
              color: Color(0xFFF59E0B),
              size: 28,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _removeFavorite(
    BuildContext context,
    WidgetRef ref,
    Hospital hospital,
  ) async {
    try {
      await ref
          .read(favoriteHospitalsProvider.notifier)
          .toggleFavorite(hospital);
    } on Object {
      if (!context.mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('즐겨찾기를 변경하지 못했습니다.')));
    }
  }
}
