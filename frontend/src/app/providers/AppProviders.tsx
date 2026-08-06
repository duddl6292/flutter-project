import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { type ReactNode, useState } from 'react'
import { BrowserRouter } from 'react-router-dom'

import {
  WebPushManager,
} from '../../firebase/WebPushManager'
import {
  ChatbotWidget,
} from '../../features/chatbot/ChatbotWidget'

export function AppProviders({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  )

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
        <ChatbotWidget />
        <WebPushManager />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
