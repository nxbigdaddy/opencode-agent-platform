export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  isStreaming?: boolean
  isError?: boolean
}

export interface Session {
  id: string
  title: string
  agent: string
  messageCount: number
  createdAt: Date
  updatedAt: Date
}

export interface ChatRequest {
  message: string
  session_id?: string
  agent?: string
}

export interface ChatResponse {
  session_id: string
  message_id: string
  role: string
  content: string
  status: string
  created_at: string
}

export interface SSEEvent {
  type: 'session' | 'text' | 'tool_result' | 'done' | 'error'
  data: Record<string, unknown>
  timestamp?: string
}
