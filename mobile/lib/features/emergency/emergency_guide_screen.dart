import 'package:brainon_mobile/features/emergency/repository/emergency_repository.dart';
import 'package:brainon_mobile/shared/models/emergency_ai_request.dart';
import 'package:brainon_mobile/shared/models/emergency_ai_response.dart';
import 'package:flutter/material.dart';

class EmergencyGuideScreen extends StatefulWidget {
  const EmergencyGuideScreen({
    required this.onOpenDrawer,
    required this.repository,
    this.patientId,
    this.accessToken,
    super.key,
  });

  final VoidCallback onOpenDrawer;
  final EmergencyRepository repository;
  final int? patientId;
  final String? accessToken;

  @override
  State<EmergencyGuideScreen> createState() => _EmergencyGuideScreenState();
}

class _EmergencyGuideScreenState extends State<EmergencyGuideScreen> {
  final TextEditingController _symptomController = TextEditingController();

  bool _isAiLoading = false;
  EmergencyAiResponse? _aiResult;
  String? _aiErrorMessage;

  static const Color emergencyColor = Color(0xFFDC2626);
  static const Color backgroundColor = Color(0xFFF7F9FC);
  static const Color textColor = Color(0xFF111827);

  @override
  void dispose() {
    _symptomController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(18, 18, 18, 36),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildEmergencyBanner(),
                    const SizedBox(height: 16),
                    _buildAiSymptomCard(),
                    const SizedBox(height: 16),
                    _buildSymptomCheckCard(),
                    const SizedBox(height: 24),
                    _buildFastSection(),
                    const SizedBox(height: 20),
                    _buildCall119Button(),
                    const SizedBox(height: 24),
                    _buildEmergencyTips(),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      width: double.infinity,
      height: 76,
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(bottom: BorderSide(color: Color(0xFFE5E7EB))),
      ),
      child: Stack(
        children: [
          const Positioned.fill(
            child: Align(
              alignment: Alignment.center,
              child: Text(
                '응급안내',
                style: TextStyle(
                  color: textColor,
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
          Positioned(
            left: 12,
            top: 10,
            bottom: 10,
            child: IconButton(
              tooltip: '메뉴',
              onPressed: widget.onOpenDrawer,
              icon: const Icon(Icons.menu_rounded, size: 32, color: textColor),
            ),
          ),
          Positioned(
            right: 12,
            top: 10,
            bottom: 10,
            child: IconButton(
              tooltip: '알림',
              onPressed: () {
                _showMessage('알림 목록 화면은 추후 연결할 예정입니다.');
              },
              icon: const Icon(
                Icons.notifications_none_rounded,
                size: 32,
                color: textColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmergencyBanner() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF1F2),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFFECACA)),
      ),
      child: const Row(
        children: [
          Icon(Icons.emergency_rounded, color: emergencyColor, size: 42),
          SizedBox(width: 14),
          Expanded(
            child: Text(
              '뇌졸중이 의심되시나요?\n하나라도 해당되면 즉시 119에 신고하세요.',
              style: TextStyle(
                color: textColor,
                fontSize: 15,
                fontWeight: FontWeight.w700,
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAiSymptomCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFF2F4FF),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFD8DEFF)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '증상을 입력해 주세요. AI가 안내를 도와드려요!',
            style: TextStyle(
              color: textColor,
              fontSize: 16,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: _symptomController,
            minLines: 1,
            maxLines: 3,
            decoration: InputDecoration(
              hintText: '예: 한쪽 팔에 힘이 없고 말이 어눌해요.',
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(15),
              ),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            height: 50,
            child: FilledButton.icon(
              onPressed: _isAiLoading ? null : _handleAiQuestion,
              icon: _isAiLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.send_rounded),
              label: Text(_isAiLoading ? 'AI 분석 중...' : 'AI에게 물어보기'),
            ),
          ),
          if (_aiResult != null) ...[
            const SizedBox(height: 12),
            _buildAiResultCard(_aiResult!),
          ],
          if (_aiErrorMessage != null) ...[
            const SizedBox(height: 12),
            _buildAiErrorCard(_aiErrorMessage!),
          ],
        ],
      ),
    );
  }

  Widget _buildAiResultCard(EmergencyAiResponse result) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Text(
        result.message,
        style: const TextStyle(
          color: textColor,
          height: 1.5,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _buildAiErrorCard(String message) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF7ED),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Text(
        message,
        style: const TextStyle(color: Color(0xFF9A3412), height: 1.5),
      ),
    );
  }

  Widget _buildSymptomCheckCard() {
    return ListTile(
      tileColor: const Color(0xFFF4F1FF),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      leading: const Icon(Icons.fact_check_outlined),
      title: const Text(
        '증상 체크하기',
        style: TextStyle(fontWeight: FontWeight.w800),
      ),
      subtitle: const Text('간단한 질문으로 응급 가능성을 확인해 보세요.'),
      trailing: const Icon(Icons.chevron_right_rounded),
      onTap: () {
        _showMessage('증상 체크 화면은 다음 단계에서 연결할 예정입니다.');
      },
    );
  }

  Widget _buildFastSection() {
    return const Text(
      'F.A.S.T. 뇌졸중 대표 증상\n'
      'F: 얼굴 처짐 · A: 한쪽 팔 힘 빠짐 · '
      'S: 말 어눌함 · T: 즉시 119',
      style: TextStyle(
        color: textColor,
        fontSize: 16,
        fontWeight: FontWeight.w800,
        height: 1.6,
      ),
    );
  }

  Widget _buildCall119Button() {
    return SizedBox(
      width: double.infinity,
      height: 64,
      child: FilledButton.icon(
        onPressed: () {
          _showMessage('119 전화 연결 기능은 추후 추가할 예정입니다.');
        },
        icon: const Icon(Icons.phone_in_talk_rounded),
        label: const Text(
          '119 전화하기',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
        ),
        style: FilledButton.styleFrom(
          backgroundColor: const Color(0xFFEF233C),
          foregroundColor: Colors.white,
        ),
      ),
    );
  }

  Widget _buildEmergencyTips() {
    return const Text(
      '응급 행동요령\n'
      '• 증상 발생 시간을 기억하세요.\n'
      '• 음식이나 물을 먹이지 마세요.\n'
      '• 직접 운전하지 마세요.\n'
      '• 복용 중인 약을 의료진에게 알리세요.',
      style: TextStyle(color: textColor, fontSize: 14, height: 1.8),
    );
  }

  Future<void> _handleAiQuestion() async {
    final symptom = _symptomController.text.trim();

    if (symptom.isEmpty) {
      _showMessage('증상을 먼저 입력해 주세요.');
      return;
    }

    if (_isAiLoading) return;

    setState(() {
      _isAiLoading = true;
      _aiResult = null;
      _aiErrorMessage = null;
    });

    try {
      final result = await widget.repository.askAiSymptom(
        request: EmergencyAiRequest(
          symptomText: symptom,
          patientId: widget.patientId,
        ),
        accessToken: widget.accessToken,
      );

      if (!mounted) return;

      setState(() {
        _aiResult = result;
      });
    } on EmergencyApiException catch (error) {
      if (!mounted) return;

      setState(() {
        _aiErrorMessage = error.message;
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _aiErrorMessage = '응급 안내를 불러오는 중 오류가 발생했습니다.';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isAiLoading = false;
        });
      }
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
      );
  }
}
