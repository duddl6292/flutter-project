import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/features/chatbot/chatbot_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ChatbotScreen extends ConsumerStatefulWidget {
  const ChatbotScreen({super.key});

  @override
  ConsumerState<ChatbotScreen> createState() => _ChatbotScreenState();
}

class _ChatbotScreenState extends ConsumerState<ChatbotScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  String? _conversationId;
  bool _loading = true;
  bool _sending = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final conversation = await ref.read(chatbotRepositoryProvider).latest();
      if (conversation != null) {
        _conversationId = conversation.id;
        _messages.addAll(conversation.messages);
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final role = ref.watch(authProvider).user?.role ?? UserRole.patient;
    final isClinician = role == UserRole.clinician;
    return Scaffold(
      appBar: AppBar(title: Text(isClinician ? '의료진 AI 어시스턴트' : '건강 AI 어시스턴트')),
      body: Column(
        children: [
          if (_messages.isEmpty && !_loading)
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  const Icon(
                    Icons.smart_toy_outlined,
                    size: 58,
                    color: Color(0xFF28669E),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    isClinician
                        ? '담당 환자, 일정, 협진과 검사 결과를 물어보세요.'
                        : '내 예약, 복약, 검사 결과와 알림을 물어보세요.',
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children:
                        (isClinician
                                ? [
                                    '오늘 진료 일정을 알려줘',
                                    '확인할 협진 요청이 있어?',
                                    '담당 환자 요약을 보여줘',
                                  ]
                                : [
                                    '다음 예약은 언제야?',
                                    '오늘 먹을 약을 알려줘',
                                    '최근 검사 결과를 요약해줘',
                                  ])
                            .map(
                              (text) => ActionChip(
                                label: Text(text),
                                onPressed: () => _send(text),
                              ),
                            )
                            .toList(),
                  ),
                ],
              ),
            ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final message = _messages[index];
                      final mine = message.role == 'USER';
                      return Align(
                        alignment: mine
                            ? Alignment.centerRight
                            : Alignment.centerLeft,
                        child: Container(
                          constraints: const BoxConstraints(maxWidth: 320),
                          margin: const EdgeInsets.only(bottom: 10),
                          padding: const EdgeInsets.all(13),
                          decoration: BoxDecoration(
                            color: mine
                                ? const Color(0xFF28669E)
                                : const Color(0xFFF0F4F8),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Text(
                            message.content,
                            style: TextStyle(
                              color: mine ? Colors.white : Colors.black87,
                            ),
                          ),
                        ),
                      );
                    },
                  ),
          ),
          SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      minLines: 1,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        hintText: '메시지를 입력하세요',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: _sending ? null : (_) => _send(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    onPressed: _sending ? null : () => _send(),
                    icon: _sending
                        ? const SizedBox.square(
                            dimension: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.send),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _send([String? preset]) async {
    final text = (preset ?? _controller.text).trim();
    if (text.isEmpty || _sending) return;
    _controller.clear();
    setState(() {
      _sending = true;
      _messages.add(
        ChatMessage(role: 'USER', content: text, createdAt: DateTime.now()),
      );
    });
    try {
      final result = await ref
          .read(chatbotRepositoryProvider)
          .send(message: text, conversationId: _conversationId);
      _conversationId = result.conversationId;
      setState(() {
        _messages.removeLast();
        _messages.addAll([result.user, result.assistant]);
      });
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('AI 응답을 받지 못했습니다: $error')));
      }
    } finally {
      if (mounted) setState(() => _sending = false);
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }
}
