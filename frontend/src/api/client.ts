import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = '/api/v1'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 自动添加 Token
apiClient.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理 401 错误
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // 如果是 401 错误且不是刷新 token 的请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const { refreshToken, clearAuth } = useAuthStore.getState()
      
      if (refreshToken) {
        try {
          // 尝试刷新 token
          const response = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            null,
            {
              params: { refresh_token: YOUR_SECRET },
            }
          )
          
          const { access_token, refresh_token, user } = response.data
          useAuthStore.getState().setAuth(user, access_token, refresh_token)
          
          // 重试原请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          // 刷新失败，清除认证状态
          clearAuth()
          window.location.href = '/login'
        }
      } else {
        // 没有 refresh token，直接清除认证
        clearAuth()
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

// API 方法
export const authApi = {
  register: (data: { username: string; password: YOUR_PASSWORD; email?: string }) =>
    apiClient.post('/auth/register', data),
  
  login: (username: string, password: YOUR_PASSWORD) => {
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    return apiClient.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  
  getMe: () => apiClient.get('/auth/me'),
  
  refreshToken: (refreshToken: string) =>
    apiClient.post('/auth/refresh', null, {
      params: { refresh_token: YOUR_SECRET },
    }),
}

export const chatApi = {
  sendMessage: (data: { message: string; session_id?: string; agent?: string }) =>
    apiClient.post('/chat', data),
  
  sendMessageStream: (data: { message: string; session_id?: string; agent?: string }) =>
    apiClient.post('/chat/stream', data, {
      responseType: 'stream',
    }),
  
  getSessions: () => apiClient.get('/sessions'),
  
  getSession: (sessionId: string) => apiClient.get(`/sessions/${sessionId}`),
  
  getMessages: (sessionId: string) => apiClient.get(`/sessions/${sessionId}/messages`),
}

export default apiClient
