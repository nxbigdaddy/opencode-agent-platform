import { useState, useRef, useEffect } from 'react'
import { useAuthStore } from '../stores/authStore'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import type { Message } from '../types/chat'

interface ChatWindowProps {
  sessionId: string | null
  onSessionCreated: (sessionId: string) => void
}

function ChatWindow({ sessionId, onSessionCreated }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const accessToken = YOUR_SECRET) => state.accessToken)

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 加载历史消息
  useEffect(() => {
    if (sessionId) {
      loadMessages(sessionId)
    } else {
      setMessages([])
    }
  }, [sessionId])

  const loadMessages = async (sid: string) => {
    try {
      setIsLoadingHistory(true)
      const response = await fetch(`/api/v1/sessions/${sid}/messages`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })
      
      if (!response.ok) throw new Error('加载失败')
      
      const data = await response.json()
      const historyMessages: Message[] = data.map((msg: any) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.created_at),
      }))
      setMessages(historyMessages)
    } catch (error) {
      console.error('加载消息历史失败:', error)
    } finally {
      setIsLoadingHistory(false)
    }
  }

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return

    // 添加用户消息
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // 创建 AI 消息占位符
      const aiMessageId = `ai_${Date.now()}`
      setMessages((prev) => [
        ...prev,
        {
          id: aiMessageId,
          role: 'assistant',
          content: '',
          timestamp: new Date(),
          isStreaming: true,
        },
      ])

      // 发送请求到 Gateway
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          message: content,
          session_id: sessionId,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      // 处理 SSE 流
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let aiContent = ''
      let newSessionId = sessionId

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value, { stream: true })
        const lines = text.split('\n')

        for (const line of lines) {
          if (line.startsWith('event: session')) {
            continue
          } else if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.session_id && !newSessionId) {
                newSessionId = data.session_id
                onSessionCreated(newSessionId)
              }
              if (data.text) {
                aiContent += data.text
                // 更新 AI 消息内容
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === aiMessageId ? { ...msg, content: aiContent } : msg
                  )
                )
              }
            } catch {
              // 忽略解析错误
            }
          } else if (line.startsWith('event: done')) {
            // 流式传输完成
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === aiMessageId ? { ...msg, isStreaming: false } : msg
              )
            )
            break
          }
        }
      }
    } catch (error: any) {
      console.error('发送消息失败:', error)
      // 添加错误消息
      setMessages((prev) => [
        ...prev,
        {
          id: `error_${Date.now()}`,
          role: 'assistant',
          content: `❌ 发送失败：${error.message || '请稍后重试'}`,
          timestamp: new Date(),
          isError: true,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoadingHistory) {
    return (
      <div className="chat-window loading">
        <div className="loading-spinner" />
        <p>加载消息历史...</p>
      </div>
    )
  }

  return (
    <div className="chat-window">
      <MessageList messages={messages} isLoading={isLoading} />
      <MessageInput onSend={handleSendMessage} disabled={isLoading} />
      <div ref={messagesEndRef} />
    </div>
  )
}

export default ChatWindow
