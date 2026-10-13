import ReactMarkdown from 'react-markdown'
import type { Message } from '../types/chat'
import './MessageList.css'

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
}

function MessageList({ messages, isLoading }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="message-list-empty">
        <div className="empty-state">
          <h2>👋 欢迎使用 AI Agent 对话平台</h2>
          <p>输入消息开始与 AI 助手对话</p>
        </div>
      </div>
    )
  }

  return (
    <div className="message-list">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`message message-${message.role} message-enter ${
            message.isError ? 'message-error' : ''
          }`}
        >
          <div className="message-header">
            <span className="message-role">
              {message.role === 'user' ? '👤 你' : '🤖 AI 助手'}
            </span>
            <span className="message-time">
              {message.timestamp.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          </div>
          <div className="message-content markdown-content">
            <ReactMarkdown>{message.content}</ReactMarkdown>
            {message.isStreaming && <span className="typing-cursor" />}
          </div>
        </div>
      ))}
      {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
        <div className="message message-assistant message-enter">
          <div className="message-header">
            <span className="message-role">🤖 AI 助手</span>
          </div>
          <div className="message-content">
            <div className="loading-dots">
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MessageList
