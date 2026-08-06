import 'package:brainon_mobile/features/patient/providers/patient_profile_provider.dart';
import 'package:brainon_mobile/shared/models/patient_profile.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class PersonalInfoScreen extends ConsumerWidget {
  const PersonalInfoScreen({super.key});

  static const Color _backgroundColor = Color(0xFFF7F9FC);
  static const Color _primaryColor = Color(0xFF28669E);
  static const Color _primaryTextColor = Color(0xFF111827);
  static const Color _secondaryTextColor = Color(0xFF6B7280);
  static const Color _borderColor = Color(0xFFE5E7EB);
  static const Color _iconBackgroundColor = Color(0xFFEAF2FA);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(patientProfileProvider);

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
          icon: const Icon(Icons.arrow_back_rounded, color: _primaryTextColor),
        ),
        title: const Text(
          '개인정보 관리',
          style: TextStyle(
            color: _primaryTextColor,
            fontSize: 20,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: profileAsync.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stackTrace) => _buildErrorView(context, ref),
          data: (profile) => _buildProfileView(context, profile),
        ),
      ),
    );
  }

  Widget _buildErrorView(BuildContext context, WidgetRef ref) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.error_outline_rounded,
              size: 56,
              color: _secondaryTextColor,
            ),
            const SizedBox(height: 16),
            const Text(
              '개인정보를 불러오지 못했습니다.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: _primaryTextColor,
                fontSize: 17,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 20),
            OutlinedButton.icon(
              onPressed: () => ref.invalidate(patientProfileProvider),
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('다시 시도'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileView(BuildContext context, PatientProfile profile) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 36),
      children: [
        const Padding(
          padding: EdgeInsets.only(left: 4),
          child: Text(
            '기본 정보',
            style: TextStyle(
              color: _primaryTextColor,
              fontSize: 16,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        const SizedBox(height: 10),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: _borderColor),
          ),
          child: Column(
            children: [
              _buildInfoItem(
                icon: Icons.badge_outlined,
                label: '이름',
                value: profile.displayName,
              ),
              _buildDivider(),
              _buildInfoItem(
                icon: Icons.account_circle_outlined,
                label: '아이디',
                value: profile.username,
              ),
              _buildDivider(),
              _buildInfoItem(
                icon: Icons.email_outlined,
                label: '이메일',
                value: _displayValue(profile.email),
              ),
              _buildDivider(),
              _buildInfoItem(
                icon: Icons.phone_outlined,
                label: '휴대전화',
                value: _displayValue(profile.phone),
              ),
              _buildDivider(),
              _buildInfoItem(
                icon: Icons.local_hospital_outlined,
                label: '환자번호',
                value: _displayValue(profile.patientNumber),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        _buildActionButton(
          icon: Icons.lock_outline_rounded,
          label: '비밀번호 변경',
          onPressed: () => _showPreparingMessage(context, '비밀번호 변경'),
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 54,
          child: FilledButton.icon(
            onPressed: () => _showPreparingMessage(context, '개인정보 수정'),
            style: FilledButton.styleFrom(
              backgroundColor: _primaryColor,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
            icon: const Icon(Icons.edit_outlined, size: 21),
            label: const Text(
              '개인정보 수정',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
            ),
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          '개인정보 수정 및 비밀번호 변경 기능은 추후 서버 연동 후 제공됩니다.',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: _secondaryTextColor,
            fontSize: 12,
            height: 1.5,
          ),
        ),
      ],
    );
  }

  Widget _buildInfoItem({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: _iconBackgroundColor,
              borderRadius: BorderRadius.circular(13),
            ),
            child: Icon(icon, color: _primaryColor, size: 22),
          ),
          const SizedBox(width: 14),
          SizedBox(
            width: 72,
            child: Text(
              label,
              style: const TextStyle(
                color: _secondaryTextColor,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.right,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: _primaryTextColor,
                fontSize: 15,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
  }) {
    return SizedBox(
      height: 54,
      child: OutlinedButton.icon(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          foregroundColor: _primaryColor,
          side: const BorderSide(color: _borderColor),
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
        icon: Icon(icon, size: 21),
        label: Text(
          label,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
        ),
      ),
    );
  }

  Widget _buildDivider() {
    return const Divider(
      height: 1,
      thickness: 1,
      indent: 72,
      endIndent: 16,
      color: _borderColor,
    );
  }

  String _displayValue(String? value) {
    final trimmedValue = value?.trim();
    return trimmedValue == null || trimmedValue.isEmpty ? '미등록' : trimmedValue;
  }

  void _showPreparingMessage(BuildContext context, String featureName) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text('$featureName 기능은 서버 연동 후 제공됩니다.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
  }
}
