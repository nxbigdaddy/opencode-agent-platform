import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import './SessionSidebar.css'

interface Session {
  id: string
  title: string
  agent: string
  message_count: number
  created_at: string
  updated_at: string
}

interface User {
  username: string
  role: string
}

interface SessionSidebarProps {
  sessions: Session[]
  currentSessionId: string | null
  isOpen: boolean
  user: User | null
  onSelectSession: (sessionId: string) => void
  onCreateSession: () => void
  onToggleSidebar: () => void
  onLogout: () => void
}

function SessionSidebar({
  sessions,
  currentSessionId,
  isOpen,
  user,
  onSelectSession,
  onCreateSession,
  onToggleSidebar,
  onLogout,
}: SessionSidebarProps) {
  return (
    <aside className={`session-sidebar ${isOpen ? 'open' : 'closed'}`}>
      {/* 侧边栏头部 */}
      <div className="sidebar-header">
        <button className="toggle-button" onClick={onToggleSidebar}>
          {isOpen ? '◀' : '▶'}
        </button>
        <h2>AI Agent</h2>
      </div>

      {/* 新建会话按钮 */}
      <button className="new-session-button" onClick={onCreateSession}>
        <span className="icon">+</span>
        {isOpen && <span>新建会话</span>}
      </button>

      {/* 会话列表 */}
      <div className="session-list">
        {sessions.length === 0 ? (
          <div className="empty-sessions">
            <p>暂无会话</p>
            <p className="hint">点击"新建会话"开始对话</p>
          </div>
        ) : (
          sessions.map((session) => (
            <button
              key={session.id}
              className={`session-item ${currentSessionId === session.id ? 'active' : ''}`}
              onClick={() => onSelectSession(session.id)}
            >
              <div className="session-info">
                <span className="session-title">{session.title}</span>
                <span className="session-meta">
                  {session.message_count} 条消息 ·{' '}
                  {formatDistanceToNow(new Date(session.updated_at), {
                    addSuffix: true,
                    locale: zhCN,
                  })}
                </span>
              </div>
            </button>
          ))
        )}
      </div>

      {/* 用户信息和退出 */}
      <div className="sidebar-footer">
        {isOpen && user && (
          <div className="user-info">
            <span className="user-avatar">👤</span>
            <div className="user-details">
              <span className="user-name">{user.username}</span>
              <span className="user-role">{user.role}</span>
            </div>
          </div>
        )}
        <button className="logout-button" onClick={onLogout}>
          <span className="icon">🚪</span>
          {isOpen && <span>退出登录</span>}
        </button>
      </div>
    </aside>
  )
}

export default SessionSidebar
