# 06 - 前端设计文档

**项目名称**：AI Agent 对话平台  
**版本**：v1.0  
**日期**：2026-04-21  
**技术栈**：React 18 + TypeScript + Tailwind CSS + Vite  
**编写人**：AI Agent 团队  
**目标读者**：前端开发、UI/UX 设计师

---

## 目录

1. [技术选型](#1-技术选型)
2. [项目结构](#2-项目结构)
3. [状态管理](#3-状态管理)
4. [组件设计](#4-组件设计)
5. [路由设计](#5-路由设计)
6. [API 集成](#6-api-集成)
7. [SSE 实时通信](#7-sse-实时通信)
8. [样式设计](#8-样式设计)
9. [性能优化](#9-性能优化)
10. [开发规范](#10-开发规范)

---

## 1. 技术选型

### 1.1 核心技术栈

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| **React** | 18.x | UI 框架 | 组件化、生态成熟、Concurrent Features |
| **TypeScript** | 5.x | 类型系统 | 编译时类型检查、IDE 支持、减少运行时错误 |
| **Tailwind CSS** | 3.x | 样式框架 | 原子化 CSS、开发效率高、包体积小 |
| **shadcn/ui** | 最新 | UI 组件库 | 可定制、源码开放、无依赖锁定 |
| **Vite** | 5.x | 构建工具 | 快速热更新、ESM 支持、优化构建 |
| **Zustand** | 4.x | 状态管理 | 轻量、简洁、TypeScript 友好 |
| **React Query** | 5.x | 服务端状态 | 缓存、重试、自动刷新 |
| **Axios** | 1.x | HTTP 客户端 | 拦截器、取消请求、进度监控 |

### 1.2 辅助库

| 库 | 用途 |
|-----|------|
| **react-markdown** | Markdown 渲染 |
| **react-syntax-highlighter** | 代码高亮 |
| **remark-gfm** | GitHub Flavored Markdown |
| **rehype-raw** | 支持 HTML in Markdown |
| **framer-motion** | 动画效果 |
| **lucide-react** | 图标库 |
| **date-fns** | 日期处理 |
| **zod** | 运行时类型校验 |

---

## 2. 项目结构

```
frontend/
├── public/
│   ├── favicon.ico
│   └── manifest.json          # PWA 配置
├── src/
│   ├── main.tsx               # 应用入口
│   ├── App.tsx                # 根组件
│   ├── index.css              # 全局样式
│   │
│   ├── components/            # 公共组件
│   │   ├── ui/               # shadcn/ui 组件
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── MainLayout.tsx
│   │   └── common/
│   │       ├── Loading.tsx
│   │       ├── ErrorBoundary.tsx
│   │       └── EmptyState.tsx
│   │
│   ├── features/             # 功能模块（按领域划分）
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── RegisterForm.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.ts
│   │   │   ├── stores/
│   │   │   │   └── authStore.ts
│   │   │   ├── types.ts
│   │   │   └── api.ts
│   │   │
│   │   ├── chat/
│   │   │   ├── components/
│   │   │   │   ├── ChatWindow.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   ├── ToolCallPanel.tsx
│   │   │   │   ├── CodeBlock.tsx
│   │   │   │   └── FileUpload.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useChat.ts
│   │   │   │   ├── useSSE.ts
│   │   │   │   └── useMessageActions.ts
│   │   │   ├── stores/
│   │   │   │   └── chatStore.ts
│   │   │   ├── types.ts
│   │   │   └── api.ts
│   │   │
│   │   ├── sessions/
│   │   │   ├── components/
│   │   │   │   ├── SessionList.tsx
│   │   │   │   ├── SessionItem.tsx
│   │   │   │   └── SessionSidebar.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useSessions.ts
│   │   │   ├── stores/
│   │   │   │   └── sessionStore.ts
│   │   │   ├── types.ts
│   │   │   └── api.ts
│   │   │
│   │   ├── agents/
│   │   │   ├── components/
│   │   │   │   ├── AgentList.tsx
│   │   │   │   ├── AgentCard.tsx
│   │   │   │   └── AgentConfigModal.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useAgents.ts
│   │   │   ├── stores/
│   │   │   │   └── agentStore.ts
│   │   │   ├── types.ts
│   │   │   └── api.ts
│   │   │
│   │   └── admin/
│   │       ├── components/
│   │       │   ├── UserManagement.tsx
│   │       │   ├── UsageStats.tsx
│   │       │   ├── AuditLogs.tsx
│   │       │   └── SystemConfig.tsx
│   │       ├── hooks/
│   │       │   └── useAdmin.ts
│   │       ├── stores/
│   │       │   └── adminStore.ts
│   │       ├── types.ts
│   │       └── api.ts
│   │
│   ├── hooks/                # 全局 Hooks
│   │   ├── useLocalStorage.ts
│   │   ├── useDebounce.ts
│   │   └── useMediaQuery.ts
│   │
│   ├── stores/               # 全局状态
│   │   ├── uiStore.ts        # UI 状态（主题、侧边栏等）
│   │   └── globalStore.ts    # 全局状态
│   │
│   ├── lib/                  # 工具库
│   │   ├── api.ts            # Axios 实例配置
│   │   ├── sse.ts            # SSE 工具
│   │   ├── utils.ts          # 通用工具
│   │   └── constants.ts      # 常量定义
│   │
│   ├── types/                # 全局类型定义
│   │   ├── index.ts
│   │   ├── api.ts
│   │   └── models.ts
│   │
│   └── styles/               # 样式文件
│       └── markdown.css      # Markdown 自定义样式
│
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── package.json
└── .env
```

---

## 3. 状态管理

### 3.1 状态分层

| 层级 | 状态类型 | 管理工具 | 示例 |
|------|---------|----------|------|
| **服务端状态** | 远程数据 | React Query | 会话列表、消息列表、用户信息 |
| **全局客户端状态** | 应用级共享 | Zustand | 当前用户、主题、侧边栏状态 |
| **局部客户端状态** | 组件级 | useState/useReducer | 表单输入、弹窗显隐 |
| **URL 状态** | 路由参数 | React Router | 当前会话 ID、筛选条件 |

### 3.2 Zustand Store 设计

#### 3.2.1 Auth Store

```typescript
// features/auth/stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  username: string;
  displayName: string;
  email: string;
  avatarUrl?: string;
  role: 'superadmin' | 'admin' | 'user' | 'guest';
}

interface AuthState {
  user: User | null;
  accessToken: YOUR_SECRET | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  
  // Actions
  setAuth: (user: User, accessToken: YOUR_SECRET, refreshToken: string) => void;
  updateUser: (user: Partial<User>) => void;
  clearAuth: () => void;
  setAccessToken: (token: YOUR_SECRET) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      
      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken, isAuthenticated: true }),
      
      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),
      
      clearAuth: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
      
      setAccessToken: (token) => set({ accessToken: YOUR_SECRET }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: YOUR_SECRET,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

#### 3.2.2 Chat Store

```typescript
// features/chat/stores/chatStore.ts
import { create } from 'zustand';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  parts: Part[];
  toolCalls?: ToolCall[];
  tokensUsed?: number;
  latencyMs?: number;
  createdAt: string;
  status: 'sending' | 'streaming' | 'complete' | 'error';
}

interface Part {
  type: 'text' | 'code' | 'image';
  text?: string;
  code?: string;
  language?: string;
}

interface ToolCall {
  name: string;
  arguments: Record<string, any>;
  result?: string;
  status: 'pending' | 'success' | 'error';
  durationMs?: number;
}

interface ChatState {
  currentSessionId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  streamingMessage: Message | null;
  
  // Actions
  setCurrentSession: (sessionId: string | null) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  setStreamingMessage: (message: Message | null) => void;
  appendStreamingContent: (content: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  currentSessionId: null,
  messages: [],
  isLoading: false,
  error: null,
  streamingMessage: null,
  
  setCurrentSession: (sessionId) =>
    set({ currentSessionId: sessionId, messages: [], error: null }),
  
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  
  updateMessage: (id, updates) =>
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, ...updates } : msg
      ),
    })),
  
  setStreamingMessage: (message) => set({ streamingMessage: message }),
  
  appendStreamingContent: (content) =>
    set((state) => ({
      streamingMessage: state.streamingMessage
        ? {
            ...state.streamingMessage,
            content: state.streamingMessage.content + content,
          }
        : null,
    })),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),
  
  clearMessages: () => set({ messages: [] }),
}));
```

### 3.3 React Query 配置

```typescript
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 分钟
      gcTime: 1000 * 60 * 30,   // 30 分钟（原 cacheTime）
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});
```

---

## 4. 组件设计

### 4.1 核心组件

#### 4.1.1 ChatWindow（对话窗口）

```typescript
// features/chat/components/ChatWindow.tsx
import { useEffect, useRef } from 'react';
import { useChatStore } from '../stores/chatStore';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

export function ChatWindow() {
  const { currentSessionId, messages } = useChatStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  
  // 自动滚动到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  if (!currentSessionId) {
    return (
      <div className="flex items-center justify-center h-full">
        <EmptyState
          title="开始新的对话"
          description="选择或创建一个会话开始与 AI 交流"
        />
      </div>
    );
  }
  
  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} />
        <div ref={bottomRef} />
      </div>
      
      {/* 输入框 */}
      <div className="border-t p-4">
        <MessageInput />
      </div>
    </div>
  );
}
```

#### 4.1.2 MessageBubble（消息气泡）

```typescript
// features/chat/components/MessageBubble.tsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { CodeBlock } from './CodeBlock';
import { ToolCallPanel } from './ToolCallPanel';
import { cn } from '@/lib/utils';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  
  return (
    <div
      className={cn(
        'flex gap-4 p-4',
        isUser ? 'bg-white' : 'bg-gray-50'
      )}
    >
      {/* 头像 */}
      <div className="flex-shrink-0">
        {isUser ? (
          <UserAvatar />
        ) : (
          <AIAvatar />
        )}
      </div>
      
      {/* 内容 */}
      <div className="flex-1 min-w-0">
        {/* 角色标签 */}
        <div className="text-sm font-medium mb-1">
          {isUser ? 'You' : 'AI Assistant'}
        </div>
        
        {/* 消息内容 */}
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code: ({ node, inline, className, children, ...props }) => {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <CodeBlock
                    language={match[1]}
                    code={String(children).replace(/\n$/, '')}
                  />
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
        
        {/* 工具调用 */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.toolCalls.map((toolCall, index) => (
              <ToolCallPanel key={index} toolCall={toolCall} />
            ))}
          </div>
        )}
        
        {/* 元信息 */}
        <div className="mt-2 text-xs text-gray-400 flex items-center gap-2">
          <span>{formatTime(message.createdAt)}</span>
          {message.tokensUsed && (
            <span>· {message.tokensUsed} tokens</span>
          )}
          {message.latencyMs && (
            <span>· {message.latencyMs}ms</span>
          )}
        </div>
      </div>
    </div>
  );
}
```

#### 4.1.3 MessageInput（消息输入框）

```typescript
// features/chat/components/MessageInput.tsx
import { useState, useRef, useCallback } from 'react';
import { useChatStore } from '../stores/chatStore';
import { useSendMessage } from '../hooks/useChat';

export function MessageInput() {
  const [content, setContent] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { isLoading } = useChatStore();
  const sendMessage = useSendMessage();
  
  // 自动调整高度
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, []);
  
  const handleSubmit = async () => {
    if (!content.trim() || isLoading) return;
    
    await sendMessage({
      message: content.trim(),
      attachments: files,
    });
    
    setContent('');
    setFiles([]);
    adjustHeight();
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };
  
  return (
    <div className="border rounded-lg bg-white">
      {/* 附件预览 */}
      {files.length > 0 && (
        <div className="flex gap-2 p-2 border-b">
          {files.map((file, index) => (
            <FilePreview
              key={index}
              file={file}
              onRemove={() => setFiles(files.filter((_, i) => i !== index))}
            />
          ))}
        </div>
      )}
      
      {/* 输入框 */}
      <div className="flex items-end p-2">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => {
            setContent(e.target.value);
            adjustHeight();
          }}
          onKeyDown={handleKeyDown}
          placeholder="输入消息... (Shift+Enter 换行)"
          className="flex-1 resize-none border-0 bg-transparent p-2 focus:outline-none focus:ring-0 max-h-[200px]"
          rows={1}
          disabled={isLoading}
        />
        
        {/* 工具栏 */}
        <div className="flex items-center gap-2 p-2">
          <FileUploadButton
            onFilesSelected={setFiles}
            disabled={files.length >= 5}
          />
          <button
            onClick={handleSubmit}
            disabled={!content.trim() || isLoading}
            className="p-2 rounded-lg bg-blue-600 text-white disabled:opacity-50"
          >
            {isLoading ? <LoadingSpinner /> : <SendIcon />}
          </button>
        </div>
      </div>
    </div>
  );
}
```

#### 4.1.4 SessionSidebar（会话侧边栏）

```typescript
// features/sessions/components/SessionSidebar.tsx
import { useState } from 'react';
import { useSessions } from '../hooks/useSessions';
import { SessionItem } from './SessionItem';
import { NewSessionButton } from './NewSessionButton';

export function SessionSidebar() {
  const [searchQuery, setSearchQuery] = useState('');
  const { data: sessions, isLoading } = useSessions({
    search: searchQuery,
    status: 'active',
  });
  
  return (
    <div className="w-64 h-full bg-gray-50 border-r flex flex-col">
      {/* 头部 */}
      <div className="p-4 border-b">
        <NewSessionButton />
      </div>
      
      {/* 搜索 */}
      <div className="p-2">
        <input
          type="text"
          placeholder="搜索会话..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 rounded-md border text-sm"
        />
      </div>
      
      {/* 会话列表 */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <SessionListSkeleton />
        ) : sessions?.items.length === 0 ? (
          <EmptyState message="暂无会话" />
        ) : (
          <div className="divide-y">
            {sessions?.items.map((session) => (
              <SessionItem key={session.id} session={session} />
            ))}
          </div>
        )}
      </div>
      
      {/* 底部 */}
      <div className="p-4 border-t">
        <UserProfile />
      </div>
    </div>
  );
}
```

---

## 5. 路由设计

### 5.1 路由结构

```typescript
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

// 页面组件
import { LoginPage } from '@/features/auth/pages/LoginPage';
import { RegisterPage } from '@/features/auth/pages/RegisterPage';
import { ChatPage } from '@/features/chat/pages/ChatPage';
import { AgentPage } from '@/features/agents/pages/AgentPage';
import { AdminLayout } from '@/features/admin/components/AdminLayout';
import { UserManagementPage } from '@/features/admin/pages/UserManagementPage';
import { UsageStatsPage } from '@/features/admin/pages/UsageStatsPage';
import { AuditLogsPage } from '@/features/admin/pages/AuditLogsPage';
import { SettingsPage } from '@/features/admin/pages/SettingsPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* 受保护路由 */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            {/* 对话页面 */}
            <Route path="/" element={<ChatPage />} />
            <Route path="/chat/:sessionId" element={<ChatPage />} />
            
            {/* Agent 管理 */}
            <Route path="/agents" element={<AgentPage />} />
            
            {/* 管理后台 */}
            <Route path="/admin" element={<AdminLayout />}>
              <Route index element={<UserManagementPage />} />
              <Route path="users" element={<UserManagementPage />} />
              <Route path="usage" element={<UsageStatsPage />} />
              <Route path="audit" element={<AuditLogsPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Route>
        </Route>
        
        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### 5.2 路由守卫

```typescript
// components/auth/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/features/auth/stores/authStore';

export function ProtectedRoute({ children }: { children?: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  const location = useLocation();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  return children;
}
```

---

## 6. API 集成

### 6.1 Axios 配置

```typescript
// lib/api.ts
import axios from 'axios';
import { useAuthStore } from '@/features/auth/stores/authStore';
import { queryClient } from './queryClient';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = YOUR_SECRET).accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config;
    
    // Token 过期，尝试刷新
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = useAuthStore.getState().refreshToken;
        const response = await axios.post('/api/v1/auth/refresh', {
          refresh_token: YOUR_SECRET,
        });
        
        const { access_token } = response.data.data;
        useAuthStore.getState().setAccessToken(access_token);
        
        // 重试原请求
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // 刷新失败，登出
        useAuthStore.getState().clearAuth();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### 6.2 API Hooks

```typescript
// features/chat/api.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

// 获取消息列表
export function useMessages(sessionId: string | null) {
  return useQuery({
    queryKey: ['messages', sessionId],
    queryFn: async () => {
      if (!sessionId) return [];
      const response = await api.get(`/sessions/${sessionId}/messages`);
      return response.data.items;
    },
    enabled: !!sessionId,
  });
}

// 发送消息
export function useSendMessage() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({
      sessionId,
      message,
      agentId,
    }: {
      sessionId: string;
      message: string;
      agentId?: string;
    }) => {
      // 使用 SSE 发送
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${useAuthStore.getState().accessToken}`,
        },
        body: JSON.stringify({
          session_id: sessionId,
          message,
          agent_id: agentId,
        }),
      });
      
      return response;
    },
    onSuccess: (_, variables) => {
      // 使消息列表缓存失效
      queryClient.invalidateQueries({
        queryKey: ['messages', variables.sessionId],
      });
    },
  });
}
```

---

## 7. SSE 实时通信

### 7.1 useSSE Hook

```typescript
// features/chat/hooks/useSSE.ts
import { useCallback, useRef, useState } from 'react';
import { useChatStore } from '../stores/chatStore';

interface SSEOptions {
  onMessage?: (data: any) => void;
  onToolCall?: (data: any) => void;
  onToolResult?: (data: any) => void;
  onError?: (error: string) => void;
  onDone?: () => void;
}

export function useSSE() {
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 5;
  
  const connect = useCallback((
    sessionId: string,
    message: string,
    options: SSEOptions = {}
  ) => {
    const token = YOUR_SECRET).accessToken;
    
    // 关闭现有连接
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    
    // 创建 EventSource
    const url = new URL('/api/v1/chat/stream', window.location.origin);
    const es = new EventSource(url.toString(), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    
    eventSourceRef.current = es;
    setIsConnected(true);
    
    // 处理事件
    es.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'thinking':
        case 'text':
          options.onMessage?.(data);
          break;
        case 'tool_call':
          options.onToolCall?.(data);
          break;
        case 'tool_result':
          options.onToolResult?.(data);
          break;
        case 'error':
          options.onError?.(data.message);
          break;
        case 'done':
          options.onDone?.();
          es.close();
          setIsConnected(false);
          break;
      }
    });
    
    es.addEventListener('error', (error) => {
      console.error('SSE error:', error);
      setIsConnected(false);
      
      // 自动重连
      if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
        const delay = Math.min(1000 * 2 ** reconnectAttemptsRef.current, 30000);
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current++;
          connect(sessionId, message, options);
        }, delay);
      } else {
        options.onError?.('连接失败，请刷新页面重试');
      }
    });
    
    // 发送消息
    fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ session_id: sessionId, message }),
    });
    
    return () => {
      es.close();
      clearTimeout(reconnectTimeoutRef.current);
    };
  }, []);
  
  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    clearTimeout(reconnectTimeoutRef.current);
    setIsConnected(false);
  }, []);
  
  return { connect, disconnect, isConnected };
}
```

---

## 8. 样式设计

### 8.1 主题配置

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
```

### 8.2 CSS 变量

```css
/* index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}
```

---

## 9. 性能优化

### 9.1 虚拟滚动

```typescript
// features/chat/components/VirtualMessageList.tsx
import { useRef, useEffect } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

export function VirtualMessageList({ messages }: { messages: Message[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100,
    overscan: 5,
  });
  
  return (
    <div ref={parentRef} className="h-full overflow-auto">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <MessageBubble message={messages[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 9.2 代码分割

```typescript
// 路由懒加载
import { lazy, Suspense } from 'react';

const ChatPage = lazy(() => import('@/features/chat/pages/ChatPage'));
const AdminPage = lazy(() => import('@/features/admin/pages/AdminPage'));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/admin/*" element={<AdminPage />} />
      </Routes>
    </Suspense>
  );
}
```

---

## 10. 开发规范

### 10.1 命名规范

| 类型 | 命名规范 | 示例 |
|------|---------|------|
| 组件 | PascalCase | `ChatWindow.tsx` |
| Hooks | camelCase, use 前缀 | `useChat.ts` |
| Stores | camelCase, store 后缀 | `chatStore.ts` |
| 工具函数 | camelCase | `formatDate.ts` |
| 类型 | PascalCase | `Message.ts` |
| 常量 | SCREAMING_SNAKE_CASE | `MAX_FILE_SIZE` |

### 10.2 文件组织

- 每个组件一个文件
- 相关组件放入同一目录
- Hooks 与使用它的组件放在同一目录
- 跨功能共享的 Hooks 放入 `src/hooks/`

### 10.3 代码风格

- 使用 ESLint + Prettier
- 强制 TypeScript strict 模式
- 组件 props 使用 interface 定义
- 避免使用 `any` 类型

---

**文档结束**
