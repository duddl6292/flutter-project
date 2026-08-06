import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ChatMessage {
  const ChatMessage({
    required this.role,
    required this.content,
    required this.createdAt,
  });
  final String role;
  final String content;
  final DateTime createdAt;

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
    role: json['role'] as String,
    content: json['content'] as String,
    createdAt:
        DateTime.tryParse(json['created_at'] as String? ?? '') ??
        DateTime.now(),
  );
}

class ChatConversation {
  const ChatConversation({required this.id, required this.messages});
  final String id;
  final List<ChatMessage> messages;
}

final chatbotRepositoryProvider = Provider<ChatbotRepository>((ref) {
  return ChatbotRepository(ref.watch(apiClientProvider));
});

class ChatbotRepository {
  const ChatbotRepository(this._dio);
  final Dio _dio;

  Future<ChatConversation?> latest() => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/chatbot/conversations/latest/',
    );
    final raw = response.data?['data'];
    if (raw == null) return null;
    final data = Map<String, dynamic>.from(raw as Map);
    return ChatConversation(
      id: data['conversation_id'] as String,
      messages: (data['messages'] as List? ?? const [])
          .map(
            (item) =>
                ChatMessage.fromJson(Map<String, dynamic>.from(item as Map)),
          )
          .toList(),
    );
  });

  Future<({String conversationId, ChatMessage user, ChatMessage assistant})>
  send({required String message, String? conversationId}) =>
      runApiRequest(() async {
        final response = await _dio.post<Map<String, dynamic>>(
          '/api/v1/chatbot/messages/',
          data: {
            'message': message,
            'conversation_id': ?conversationId,
            'idempotency_key': '${DateTime.now().microsecondsSinceEpoch}',
          },
        );
        final data = Map<String, dynamic>.from(response.data?['data'] as Map);
        return (
          conversationId: data['conversation_id'] as String,
          user: ChatMessage.fromJson(
            Map<String, dynamic>.from(data['user_message'] as Map),
          ),
          assistant: ChatMessage.fromJson(
            Map<String, dynamic>.from(data['assistant_message'] as Map),
          ),
        );
      });
}
