import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { chatApi } from '../api/client'
import ChatWindow from '../components/ChatWindow'
import SessionSidebar from '../components/SessionSidebar'
import QuotaDisplay from '../components/QuotaDisplay'
import './Chat.css'

interface Session {
  id: string
  title: string
  agent: string
  message_count: number
  created_at: string
  updated_at: string
}

function Chat() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [loading, setLoading] = useState(true)
  
  const navigate = useNavigate()
  const { user, clearAuth } = useAuthStore()

  // 加载会话列表
  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      setLoading(true)
      const response = await chatApi.getSessions()
      setSessions(response.data)
      
      // 如果有会话，选择第一个
      if (response.data.length > 0 && !currentSessionId) {
        setCurrentSessionId(response.data[0].id)
      }
    } catch (error) {
      console.error('加载会话失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSession = () => {
    setCurrentSessionId(null)
  }

  const handleSelectSession = (sessionId: string) => {
    setCurrentSessionId(sessionId)
  }

  const handleSessionCreated = (sessionId: string) => {
    setCurrentSessionId(sessionId)
    loadSessions()
  }

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  if (loading && sessions.length === 0) {
    return (
      <div className="chat-loading">
        <div className="loading-spinner" />
        <p>加载中...</p>
      </div>
    )
  }

  return (
    <div className="chat-page">
      {/* 侧边栏 */}
      <SessionSidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        isOpen={sidebarOpen}
        user={user}
        onSelectSession={handleSelectSession}
        onCreateSession={handleCreateSession}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onLogout={handleLogout}
      />

      {/* 主内容区 */}
      <main className="chat-main">
        {/* 顶部配额显示 */}
        <QuotaDisplay />
        
        <ChatWindow
          sessionId={currentSessionId}
          onSessionCreated={handleSessionCreated}
        />
      </main>
    </div>
  )
}

export default Chat
