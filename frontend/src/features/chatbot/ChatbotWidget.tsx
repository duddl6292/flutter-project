import {
  FormEvent,
  KeyboardEvent,
  useEffect,
  useRef,
  useState,
} from 'react'

import {
  Bot,
  ChevronDown,
  LoaderCircle,
  MessageCircle,
  Send,
  Sparkles,
} from 'lucide-react'

import { useAuthStore } from '../../core/auth/authStore'
import {
  getLatestChatConversation,
  sendChatMessage,
} from './chatbot.api'
import type { ChatMessage } from './chatbot.api'

import './chatbot.css'

const QUICK_PROMPTS = [
  'BrainOn 백엔드 상태를 확인해줘.',
  '서울 지역 병원을 최대 5개 알려줘.',
]

function formatMessageTime(value: string): string {
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(new Date(value))
}

export function ChatbotWidget() {
  const user = useAuthStore((state) => state.user)
  const [open, setOpen] = useState(false)
  const [conversationId, setConversationId] =
    useState<string | null>(null)
  const [messages, setMessages] =
    useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loadingHistory, setLoadingHistory] =
    useState(false)
  const [sending, setSending] = useState(false)
  const [historyLoaded, setHistoryLoaded] =
    useState(false)
  const [error, setError] = useState('')
  const messageEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const available =
    user?.role === 'CLINICIAN'
    || user?.role === 'ADMIN'

  useEffect(() => {
    setOpen(false)
    setConversationId(null)
    setMessages([])
    setHistoryLoaded(false)
    setError('')
  }, [user?.id])

  useEffect(() => {
    if (!open || historyLoaded || !available) {
      return
    }

    let active = true
    setLoadingHistory(true)
    setError('')

    void getLatestChatConversation()
      .then((conversation) => {
        if (!active) {
          return
        }
        setConversationId(
          conversation?.conversation_id ?? null,
        )
        setMessages(
          conversation?.messages.filter(
            (message) =>
              message.role === 'USER'
              || message.role === 'ASSISTANT',
          ) ?? [],
        )
        setHistoryLoaded(true)
      })
      .catch((requestError: unknown) => {
        if (!active) {
          return
        }
        setError(
          requestError instanceof Error
            ? requestError.message
            : '이전 대화를 불러오지 못했습니다.',
        )
      })
      .finally(() => {
        if (active) {
          setLoadingHistory(false)
        }
      })

    return () => {
      active = false
    }
  }, [available, historyLoaded, open])

  useEffect(() => {
    if (!open) {
      return
    }
    messageEndRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
    })
  }, [messages, open, sending])

  useEffect(() => {
    if (open && historyLoaded) {
      textareaRef.current?.focus()
    }
  }, [historyLoaded, open])

  if (!available) {
    return null
  }

  const submitMessage = async () => {
    const message = input.trim()
    if (!message || sending) {
      return
    }

    const temporaryId = `pending-${crypto.randomUUID()}`
    const optimisticMessage: ChatMessage = {
      message_id: temporaryId,
      role: 'USER',
      sequence: messages.length + 1,
      content: message,
      created_at: new Date().toISOString(),
    }

    setInput('')
    setError('')
    setSending(true)
    setMessages((current) => [
      ...current,
      optimisticMessage,
    ])

    try {
      const reply = await sendChatMessage({
        message,
        conversationId,
        idempotencyKey: crypto.randomUUID(),
      })
      setConversationId(reply.conversation_id)
      setMessages((current) => [
        ...current.filter(
          (item) => item.message_id !== temporaryId,
        ),
        reply.user_message,
        reply.assistant_message,
      ])
    } catch (requestError) {
      setMessages((current) =>
        current.filter(
          (item) => item.message_id !== temporaryId,
        ),
      )
      setInput(message)
      setError(
        requestError instanceof Error
          ? requestError.message
          : '답변을 생성하지 못했습니다.',
      )
    } finally {
      setSending(false)
    }
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    void submitMessage()
  }

  const handleKeyDown = (
    event: KeyboardEvent<HTMLTextAreaElement>,
  ) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void submitMessage()
    }
  }

  return (
    <aside className="brainon-chatbot" aria-label="BrainOn AI 챗봇">
      {open && (
        <section className="brainon-chatbot-panel">
          <header className="brainon-chatbot-header">
            <div className="brainon-chatbot-brand">
              <span className="brainon-chatbot-logo">
                <Bot size={21} />
              </span>
              <div>
                <strong>BrainOn AI</strong>
                <span>의료진 업무 도우미</span>
              </div>
            </div>
            <button
              type="button"
              className="brainon-chatbot-minimize"
              aria-label="챗봇 접기"
              onClick={() => setOpen(false)}
            >
              <ChevronDown size={21} />
            </button>
          </header>

          <div className="brainon-chatbot-messages" aria-live="polite">
            {loadingHistory && (
              <div className="brainon-chatbot-loading">
                <LoaderCircle className="brainon-chatbot-spinner" size={19} />
                이전 대화를 불러오는 중입니다.
              </div>
            )}

            {!loadingHistory && messages.length === 0 && (
              <div className="brainon-chatbot-welcome">
                <span><Sparkles size={20} /></span>
                <strong>무엇을 도와드릴까요?</strong>
                <p>
                  BrainOn 시스템 상태와 등록 병원 정보를
                  도구로 확인할 수 있습니다.
                </p>
                <div className="brainon-chatbot-prompts">
                  {QUICK_PROMPTS.map((prompt) => (
                    <button
                      type="button"
                      key={prompt}
                      onClick={() => {
                        setInput(prompt)
                        textareaRef.current?.focus()
                      }}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((message) => (
              <article
                key={message.message_id}
                className={`brainon-chatbot-message brainon-chatbot-message-${message.role.toLowerCase()}`}
              >
                {message.role === 'ASSISTANT' && (
                  <span className="brainon-chatbot-message-avatar">
                    <Bot size={16} />
                  </span>
                )}
                <div>
                  <p>{message.content}</p>
                  <time>{formatMessageTime(message.created_at)}</time>
                </div>
              </article>
            ))}

            {sending && (
              <article className="brainon-chatbot-message brainon-chatbot-message-assistant">
                <span className="brainon-chatbot-message-avatar">
                  <Bot size={16} />
                </span>
                <div className="brainon-chatbot-thinking">
                  <span />
                  <span />
                  <span />
                </div>
              </article>
            )}

            <div ref={messageEndRef} />
          </div>

          {error && (
            <p className="brainon-chatbot-error">{error}</p>
          )}

          <form className="brainon-chatbot-form" onSubmit={handleSubmit}>
            <div className="brainon-chatbot-input-row">
              <textarea
                ref={textareaRef}
                rows={1}
                maxLength={2000}
                value={input}
                aria-label="챗봇 메시지"
                placeholder="BrainOn AI에게 질문하세요"
                disabled={sending}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleKeyDown}
              />
              <button
                type="submit"
                aria-label="메시지 전송"
                disabled={!input.trim() || sending}
              >
                {sending
                  ? <LoaderCircle className="brainon-chatbot-spinner" size={19} />
                  : <Send size={18} />}
              </button>
            </div>
            <small>AI 답변은 의료진의 최종 판단을 대체하지 않습니다.</small>
          </form>
        </section>
      )}

      {!open && (
        <button
          type="button"
          className="brainon-chatbot-launcher"
          aria-label="BrainOn AI 챗봇 열기"
          onClick={() => setOpen(true)}
        >
          <MessageCircle size={23} />
          <span>AI 도우미</span>
        </button>
      )}
    </aside>
  )
}
