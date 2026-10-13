import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api/client'
import { useAuthStore } from '../stores/authStore'
import './Login.css'

function Login() {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isRegister) {
        // 注册
        const response = await authApi.register({
          username,
          password,
          email: email || undefined,
        })
        
        // 注册成功后自动登录
        const loginResponse = await authApi.login(username, password)
        const { access_token, refresh_token, user } = loginResponse.data
        setAuth(user, access_token, refresh_token)
        navigate('/')
      } else {
        // 登录
        const response = await authApi.login(username, password)
        const { access_token, refresh_token, user } = response.data
        setAuth(user, access_token, refresh_token)
        navigate('/')
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        err.response?.data?.message || 
        '操作失败，请重试'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🤖 AI Agent 对话平台</h1>
          <p>{isRegister ? '创建新账户' : '欢迎回来'}</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">用户名</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="请输入用户名"
              required
              minLength={3}
              maxLength={50}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">密码</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
              required
              minLength={8}
              disabled={loading}
            />
          </div>

          {isRegister && (
            <div className="form-group">
              <label htmlFor="email">邮箱（可选）</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="请输入邮箱"
                disabled={loading}
              />
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? '处理中...' : isRegister ? '注册' : '登录'}
          </button>
        </form>

        <div className="login-footer">
          {isRegister ? (
            <p>
              已有账户？{' '}
              <button
                type="button"
                className="link-button"
                onClick={() => {
                  setIsRegister(false)
                  setError('')
                }}
              >
                立即登录
              </button>
            </p>
          ) : (
            <p>
              没有账户？{' '}
              <button
                type="button"
                className="link-button"
                onClick={() => {
                  setIsRegister(true)
                  setError('')
                }}
              >
                立即注册
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Login
