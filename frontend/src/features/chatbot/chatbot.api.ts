import { apiRequest } from '../../core/api/apiClient'

export type ChatRole =
  | 'USER'
  | 'ASSISTANT'
  | 'SYSTEM'
  | 'TOOL'

export interface ChatMessage {
  message_id: string
  role: ChatRole
  sequence: number
  content: string
  created_at: string
}

export interface ChatConversation {
  conversation_id: string
  title: string
  status: 'ACTIVE' | 'ARCHIVED'
  messages: ChatMessage[]
  created_at: string
  updated_at: string
}

interface ApiEnvelope<T> {
  data: T
}

interface ChatReply {
  conversation_id: string
  user_message: ChatMessage
  assistant_message: ChatMessage
}

export async function getLatestChatConversation():
Promise<ChatConversation | null> {
  const response = await apiRequest<
    ApiEnvelope<ChatConversation | null>
  >('/api/v1/chatbot/conversations/latest/')

  return response.data
}

export async function sendChatMessage(input: {
  message: string
  conversationId: string | null
  idempotencyKey: string
}): Promise<ChatReply> {
  const response = await apiRequest<
    ApiEnvelope<ChatReply>
  >(
    '/api/v1/chatbot/messages/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: input.message,
        conversation_id:
          input.conversationId,
        idempotency_key:
          input.idempotencyKey,
      }),
    },
  )

  return response.data
}
