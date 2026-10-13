import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import ChatWindow from './components/ChatWindow'
import './App.css'

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const { user, clearAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-left">
          <h1>🤖 AI Agent 对话平台</h1>
          {sessionId && (
            <span className="session-id">
              会话: {sessionId.slice(0, 12)}...
            </span>
          )}
        </div>
        <div className="header-right">
          {user && (
            <div className="user-badge">
              <span className="user-avatar-small">👤</span>
              <span className="user-name-header">{user.username}</span>
            </div>
          )}
          <button className="logout-btn-header" onClick={handleLogout}>
            退出
          </button>
        </div>
      </header>
      
      <main className="app-main">
        <ChatWindow 
          sessionId={sessionId}
          onSessionCreated={setSessionId}
        />
      </main>
    </div>
  )
}

export default App
