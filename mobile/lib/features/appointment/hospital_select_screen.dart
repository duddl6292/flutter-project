import 'package:brainon_mobile/features/appointment/repositories/hospital_repository.dart';
import 'package:brainon_mobile/features/patient/providers/favorite_hospitals_provider.dart';
import 'package:brainon_mobile/shared/mock/recent_hospital_mock.dart';
import 'package:brainon_mobile/shared/models/hospital.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class HospitalSelectScreen extends ConsumerStatefulWidget {
  const HospitalSelectScreen({super.key});

  @override
  ConsumerState<HospitalSelectScreen> createState() =>
      _HospitalSelectScreenState();
}

class _HospitalSelectScreenState extends ConsumerState<HospitalSelectScreen> {
  final HospitalRepository _repository = HospitalRepository();
  final TextEditingController _searchController = TextEditingController();

  List<Hospital> _hospitals = [];

  bool _isLoading = true;
  String _keyword = '';
  String? _selectedHospitalId;

  @override
  void initState() {
    super.initState();
    _loadHospitals();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadHospitals() async {
    try {
      final hospitals = await _repository.getHospitals();

      if (!mounted) {
        return;
      }

      setState(() {
        _hospitals = hospitals;
        _isLoading = false;
      });
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
      });

      _showMessage('병원 정보를 불러오지 못했습니다.');
    }
  }

  List<Hospital> get _recentHospitals {
    return recentHospitalIdMock
        .map((hospitalId) {
          for (final hospital in _hospitals) {
            if (hospital.hospitalId == hospitalId) {
              return hospital;
            }
          }

          return null;
        })
        .whereType<Hospital>()
        .toList();
  }

  void _selectHospital(Hospital hospital) {
    setState(() {
      _selectedHospitalId = hospital.hospitalId;
    });
  }

  Future<void> _toggleFavorite(Hospital selectedHospital) async {
    try {
      await ref
          .read(favoriteHospitalsProvider.notifier)
          .toggleFavorite(selectedHospital);
    } on Object {
      if (mounted) _showMessage('즐겨찾기를 변경하지 못했습니다.');
    }
  }

  void _completeSelection() {
    if (_selectedHospitalId == null) {
      _showMessage('병원을 선택해 주세요.');
      return;
    }

    final selectedHospital = _hospitals.firstWhere((hospital) {
      return hospital.hospitalId == _selectedHospitalId;
    });

    Navigator.of(context).pop(selectedHospital);
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
      );
  }

  @override
  Widget build(BuildContext context) {
    final favoriteIds = ref
        .watch(favoriteHospitalsProvider)
        .valueOrNull
        ?.map((hospital) => hospital.hospitalId)
        .toSet();
    final displayHospitals = _hospitals.map((hospital) {
      return hospital.copyWith(
        isFavorite:
            favoriteIds?.contains(hospital.hospitalId) ?? hospital.isFavorite,
      );
    }).toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        elevation: 0,
        title: const Text(
          '병원 선택',
          style: TextStyle(
            color: Color(0xFF111827),
            fontSize: 20,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : Column(
                children: [
                  Expanded(
                    child: ListView(
                      padding: const EdgeInsets.fromLTRB(20, 22, 20, 30),
                      children: [
                        const Text(
                          '어느 병원에서 진료를 받으시겠어요?',
                          style: TextStyle(
                            color: Color(0xFF111827),
                            fontSize: 22,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 7),
                        const Text(
                          '병원명을 검색하거나 최근·찜한 병원에서 선택해 주세요.',
                          style: TextStyle(
                            color: Color(0xFF6B7280),
                            fontSize: 14,
                            height: 1.4,
                          ),
                        ),
                        const SizedBox(height: 22),

                        // 병원 검색창
                        TextField(
                          controller: _searchController,
                          onChanged: (value) {
                            setState(() {
                              _keyword = value.trim();
                            });
                          },
                          decoration: InputDecoration(
                            hintText: '병원명을 검색해 주세요.',
                            prefixIcon: const Icon(Icons.search_rounded),
                            suffixIcon: _keyword.isEmpty
                                ? null
                                : IconButton(
                                    onPressed: () {
                                      _searchController.clear();

                                      setState(() {
                                        _keyword = '';
                                      });
                                    },
                                    icon: const Icon(Icons.close_rounded),
                                  ),
                            filled: true,
                            fillColor: Colors.white,
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 17,
                            ),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(16),
                              borderSide: const BorderSide(
                                color: Color(0xFFD8DEE9),
                              ),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(16),
                              borderSide: const BorderSide(
                                color: Color(0xFF2563EB),
                                width: 1.5,
                              ),
                            ),
                          ),
                        ),

                        const SizedBox(height: 26),

                        if (_keyword.isEmpty) ...[
                          // ============================================================
                          // 찜한 병원
                          // ============================================================
                          const _SectionTitle(title: '찜한 병원'),

                          const SizedBox(height: 12),

                          if (displayHospitals
                              .where((hospital) => hospital.isFavorite)
                              .isEmpty)
                            const _EmptySection(
                              message: '찜한 병원이 없습니다.\n검색 결과의 별을 눌러 추가해 보세요.',
                            )
                          else
                            ...displayHospitals
                                .where((hospital) => hospital.isFavorite)
                                .map((hospital) {
                                  return Padding(
                                    padding: const EdgeInsets.only(bottom: 12),
                                    child: _HospitalCard(
                                      hospital: hospital,
                                      isSelected:
                                          _selectedHospitalId ==
                                          hospital.hospitalId,
                                      onSelect: () {
                                        _selectHospital(hospital);
                                      },
                                      onFavorite: () {
                                        _toggleFavorite(hospital);
                                      },
                                    ),
                                  );
                                }),

                          const SizedBox(height: 18),

                          // ============================================================
                          // 최근 방문 병원
                          // ============================================================
                          const _SectionTitle(
                            title: '최근 방문 병원',
                            trailingText: '최근 이용 기준',
                          ),

                          const SizedBox(height: 12),

                          if (_recentHospitals.isEmpty)
                            const _EmptySection(message: '최근 방문한 병원이 없습니다.')
                          else
                            ...recentHospitalIdMock
                                .map(
                                  (hospitalId) => displayHospitals
                                      .where(
                                        (hospital) =>
                                            hospital.hospitalId == hospitalId,
                                      )
                                      .firstOrNull,
                                )
                                .whereType<Hospital>()
                                .take(3)
                                .map((hospital) {
                                  return Padding(
                                    padding: const EdgeInsets.only(bottom: 12),
                                    child: _HospitalCard(
                                      hospital: hospital,
                                      isSelected:
                                          _selectedHospitalId ==
                                          hospital.hospitalId,
                                      onSelect: () {
                                        _selectHospital(hospital);
                                      },
                                      onFavorite: () {
                                        _toggleFavorite(hospital);
                                      },
                                      badgeText: '최근 방문',
                                    ),
                                  );
                                }),
                        ] else ...[
                          // 검색 결과
                          _SectionTitle(
                            title: '검색 결과',
                            trailingText:
                                '${displayHospitals.where((hospital) => hospital.hospitalName.toLowerCase().contains(_keyword.trim().toLowerCase())).length}개',
                          ),
                          const SizedBox(height: 12),

                          if (displayHospitals
                              .where(
                                (hospital) => hospital.hospitalName
                                    .toLowerCase()
                                    .contains(_keyword.trim().toLowerCase()),
                              )
                              .isEmpty)
                            const _EmptySection(message: '검색 결과가 없습니다.')
                          else
                            ...displayHospitals
                                .where(
                                  (hospital) => hospital.hospitalName
                                      .toLowerCase()
                                      .contains(_keyword.trim().toLowerCase()),
                                )
                                .map((hospital) {
                                  return Padding(
                                    padding: const EdgeInsets.only(bottom: 12),
                                    child: _HospitalCard(
                                      hospital: hospital,
                                      isSelected:
                                          _selectedHospitalId ==
                                          hospital.hospitalId,
                                      onSelect: () {
                                        _selectHospital(hospital);
                                      },
                                      onFavorite: () {
                                        _toggleFavorite(hospital);
                                      },
                                    ),
                                  );
                                }),
                        ],
                      ],
                    ),
                  ),

                  // 다음 버튼
                  Container(
                    padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
                    decoration: const BoxDecoration(color: Color(0xFFF5F7FB)),
                    child: SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: FilledButton(
                        onPressed: _selectedHospitalId == null
                            ? null
                            : _completeSelection,
                        style: FilledButton.styleFrom(
                          backgroundColor: const Color(0xFF2563EB),
                          disabledBackgroundColor: const Color(0xFFD1D5DB),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                        ),
                        child: const Text(
                          '다음',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.title, this.trailingText});

  final String title;
  final String? trailingText;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(
            title,
            style: const TextStyle(
              color: Color(0xFF111827),
              fontSize: 17,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        if (trailingText != null)
          Text(
            trailingText!,
            style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
          ),
      ],
    );
  }
}

class _HospitalCard extends StatelessWidget {
  const _HospitalCard({
    required this.hospital,
    required this.isSelected,
    required this.onSelect,
    required this.onFavorite,
    this.badgeText,
  });

  final Hospital hospital;
  final bool isSelected;
  final VoidCallback onSelect;
  final VoidCallback onFavorite;
  final String? badgeText;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onSelect,
      borderRadius: BorderRadius.circular(18),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(
            color: isSelected
                ? const Color(0xFF2563EB)
                : const Color(0xFFE5E7EB),
            width: isSelected ? 1.5 : 1,
          ),
        ),
        child: Row(
          children: [
            // 병원 아이콘
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: const Color(0xFFEFF6FF),
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Icon(
                Icons.local_hospital_outlined,
                color: Color(0xFF2563EB),
              ),
            ),

            const SizedBox(width: 14),

            // 병원 정보
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          hospital.hospitalName,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            color: Color(0xFF111827),
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),

                      if (badgeText != null) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: const Color(0xFFEFF6FF),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            badgeText!,
                            style: const TextStyle(
                              color: Color(0xFF2563EB),
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),

                  if (hospital.address.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      hospital.address,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Color(0xFF6B7280),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ],
              ),
            ),

            // 찜 버튼
            IconButton(
              onPressed: onFavorite,
              tooltip: hospital.isFavorite ? '찜 해제' : '찜 추가',
              icon: Icon(
                hospital.isFavorite
                    ? Icons.star_rounded
                    : Icons.star_border_rounded,
                color: hospital.isFavorite
                    ? const Color(0xFFF59E0B)
                    : const Color(0xFFCBD5E1),
                size: 28,
              ),
            ),

            const SizedBox(width: 4),

            // 선택 표시
            Icon(
              isSelected
                  ? Icons.check_circle_rounded
                  : Icons.radio_button_unchecked,
              color: isSelected
                  ? const Color(0xFF2563EB)
                  : const Color(0xFFCBD5E1),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptySection extends StatelessWidget {
  const _EmptySection({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE5E7EB)),
      ),
      child: Text(
        message,
        textAlign: TextAlign.center,
        style: const TextStyle(
          color: Color(0xFF6B7280),
          fontSize: 13,
          height: 1.5,
        ),
      ),
    );
  }
}
