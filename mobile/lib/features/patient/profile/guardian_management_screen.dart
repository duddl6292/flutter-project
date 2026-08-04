import 'package:brainon_mobile/features/patient/providers/guardian_provider.dart';
import 'package:brainon_mobile/shared/models/guardian.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class GuardianManagementScreen extends ConsumerWidget {
  const GuardianManagementScreen({super.key});

  static const Color _backgroundColor = Color(0xFFF7F9FC);
  static const Color _primaryColor = Color(0xFF28669E);
  static const Color _primaryTextColor = Color(0xFF111827);
  static const Color _secondaryTextColor = Color(0xFF6B7280);
  static const Color _borderColor = Color(0xFFE5E7EB);
  static const Color _iconBackgroundColor = Color(0xFFEAF2FA);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final guardiansAsync = ref.watch(guardianProvider);

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
          '보호자 관리',
          style: TextStyle(
            color: _primaryTextColor,
            fontSize: 20,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: guardiansAsync.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stackTrace) => _buildErrorView(context, ref),
          data: (guardians) => _buildGuardianList(context, ref, guardians),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openGuardianForm(context, ref),
        backgroundColor: _primaryColor,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.person_add_alt_1_rounded),
        label: const Text(
          '보호자 추가',
          style: TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
    );
  }

  Widget _buildErrorView(BuildContext context, WidgetRef ref) {
    return Center(
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
            '보호자 정보를 불러오지 못했습니다.',
            style: TextStyle(
              color: _primaryTextColor,
              fontSize: 17,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 20),
          OutlinedButton.icon(
            onPressed: ref.read(guardianProvider.notifier).loadGuardians,
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('다시 시도'),
          ),
        ],
      ),
    );
  }

  Widget _buildGuardianList(
    BuildContext context,
    WidgetRef ref,
    List<Guardian> guardians,
  ) {
    return RefreshIndicator(
      onRefresh: ref.read(guardianProvider.notifier).loadGuardians,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 110),
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: _iconBackgroundColor,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.info_outline_rounded, color: _primaryColor),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    '응급 상황에서는 우선순위가 높은 보호자부터 연락합니다. '
                    '현재 정보는 화면 검증용 Mock 데이터입니다.',
                    style: TextStyle(
                      color: _primaryColor,
                      fontSize: 13,
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          if (guardians.isEmpty)
            _buildEmptyView()
          else
            ...guardians.map(
              (guardian) => Padding(
                padding: const EdgeInsets.only(bottom: 14),
                child: _buildGuardianCard(context, ref, guardian),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildEmptyView() {
    return const Padding(
      padding: EdgeInsets.only(top: 90),
      child: Column(
        children: [
          Icon(
            Icons.family_restroom_rounded,
            size: 60,
            color: _secondaryTextColor,
          ),
          SizedBox(height: 16),
          Text(
            '등록된 보호자가 없습니다.',
            style: TextStyle(
              color: _primaryTextColor,
              fontSize: 17,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGuardianCard(
    BuildContext context,
    WidgetRef ref,
    Guardian guardian,
  ) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _borderColor),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: _iconBackgroundColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Icon(
                  Icons.person_outline_rounded,
                  color: _primaryColor,
                  size: 28,
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            guardian.name,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: _primaryTextColor,
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        _buildPriorityBadge(guardian.emergencyPriority),
                      ],
                    ),
                    const SizedBox(height: 5),
                    Text(
                      '${guardian.relationship} · ${guardian.phone}',
                      style: const TextStyle(
                        color: _secondaryTextColor,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Divider(height: 1, color: _borderColor),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton.icon(
                onPressed: () => _openGuardianForm(context, ref, guardian),
                icon: const Icon(Icons.edit_outlined, size: 19),
                label: const Text('수정'),
              ),
              const SizedBox(width: 4),
              TextButton.icon(
                onPressed: () => _confirmDelete(context, ref, guardian),
                style: TextButton.styleFrom(foregroundColor: Colors.redAccent),
                icon: const Icon(Icons.delete_outline_rounded, size: 19),
                label: const Text('삭제'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPriorityBadge(int priority) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        color: priority == 1 ? const Color(0xFFFFECEC) : _iconBackgroundColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        '$priority순위',
        style: TextStyle(
          color: priority == 1 ? const Color(0xFFD14343) : _primaryColor,
          fontSize: 12,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Future<void> _openGuardianForm(
    BuildContext context,
    WidgetRef ref, [
    Guardian? guardian,
  ]) async {
    final usedPriorities = ref
        .read(guardianProvider)
        .valueOrNull
        ?.where((item) => item.id != guardian?.id)
        .map((item) => item.emergencyPriority)
        .toSet();
    final result = await showDialog<Guardian>(
      context: context,
      builder: (dialogContext) => _GuardianFormDialog(
        guardian: guardian,
        usedPriorities: usedPriorities ?? const <int>{},
      ),
    );
    if (result == null || !context.mounted) return;

    try {
      final notifier = ref.read(guardianProvider.notifier);
      if (guardian == null) {
        await notifier.addGuardian(result);
      } else {
        await notifier.updateGuardian(result);
      }
      if (!context.mounted) return;
      _showMessage(
        context,
        guardian == null ? '보호자를 추가했습니다.' : '보호자 정보를 수정했습니다.',
      );
    } on Object {
      if (context.mounted) _showMessage(context, '보호자 정보를 저장하지 못했습니다.');
    }
  }

  Future<void> _confirmDelete(
    BuildContext context,
    WidgetRef ref,
    Guardian guardian,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('보호자 삭제'),
        content: Text('${guardian.name} 보호자를 삭제하시겠습니까?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(false),
            child: const Text('취소'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogContext).pop(true),
            style: FilledButton.styleFrom(backgroundColor: Colors.redAccent),
            child: const Text('삭제'),
          ),
        ],
      ),
    );
    if (confirmed != true || !context.mounted) return;

    try {
      await ref.read(guardianProvider.notifier).deleteGuardian(guardian.id);
      if (context.mounted) _showMessage(context, '보호자를 삭제했습니다.');
    } on Object {
      if (context.mounted) _showMessage(context, '보호자를 삭제하지 못했습니다.');
    }
  }

  void _showMessage(BuildContext context, String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
      );
  }
}

class _GuardianFormDialog extends StatefulWidget {
  const _GuardianFormDialog({required this.usedPriorities, this.guardian});

  final Guardian? guardian;
  final Set<int> usedPriorities;

  @override
  State<_GuardianFormDialog> createState() => _GuardianFormDialogState();
}

class _GuardianFormDialogState extends State<_GuardianFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  late final TextEditingController _relationshipController;
  late final TextEditingController _phoneController;
  late int _priority;

  @override
  void initState() {
    super.initState();
    final guardian = widget.guardian;
    _nameController = TextEditingController(text: guardian?.name);
    _relationshipController = TextEditingController(
      text: guardian?.relationship,
    );
    _phoneController = TextEditingController(text: guardian?.phone);
    _priority = guardian?.emergencyPriority ?? 1;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _relationshipController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.guardian == null ? '보호자 추가' : '보호자 수정'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildTextField(_nameController, '보호자 이름'),
              const SizedBox(height: 14),
              _buildTextField(_relationshipController, '환자와의 관계'),
              const SizedBox(height: 14),
              _buildTextField(
                _phoneController,
                '전화번호',
                keyboardType: TextInputType.phone,
              ),
              const SizedBox(height: 14),
              DropdownButtonFormField<int>(
                initialValue: _priority,
                decoration: const InputDecoration(
                  labelText: '응급 연락 우선순위',
                  border: OutlineInputBorder(),
                ),
                items: List.generate(
                  5,
                  (index) => DropdownMenuItem(
                    value: index + 1,
                    enabled: !widget.usedPriorities.contains(index + 1),
                    child: Text('${index + 1}순위'),
                  ),
                ),
                onChanged: (value) {
                  if (value != null) _priority = value;
                },
                validator: (value) {
                  if (value == null) return '응급 연락 우선순위를 선택해 주세요.';
                  if (widget.usedPriorities.contains(value)) {
                    return '$value순위는 이미 사용 중입니다.';
                  }
                  return null;
                },
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('취소'),
        ),
        FilledButton(
          onPressed: _submit,
          child: Text(widget.guardian == null ? '추가' : '저장'),
        ),
      ],
    );
  }

  TextFormField _buildTextField(
    TextEditingController controller,
    String label, {
    TextInputType? keyboardType,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
      ),
      validator: (value) {
        if (value == null || value.trim().isEmpty) return '$label을 입력해 주세요.';
        return null;
      },
    );
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    Navigator.of(context).pop(
      Guardian(
        id: widget.guardian?.id ?? 0,
        name: _nameController.text.trim(),
        relationship: _relationshipController.text.trim(),
        phone: _phoneController.text.trim(),
        emergencyPriority: _priority,
      ),
    );
  }
}
