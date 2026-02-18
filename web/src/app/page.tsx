'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

// Types
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

// Icon components
const Icons = {
  Send: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13"></line>
      <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
    </svg>
  ),
  Bot: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="10" rx="2"></rect>
      <circle cx="12" cy="5" r="2"></circle>
      <path d="M12 7v4"></path>
      <line x1="8" y1="16" x2="8" y2="16"></line>
      <line x1="16" y1="16" x2="16" y2="16"></line>
    </svg>
  ),
  User: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
      <circle cx="12" cy="7" r="4"></circle>
    </svg>
  ),
  Settings: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3"></circle>
      <path d="M12 1v6m0 6v10M4.22 4.22l4.24 4.24m7.08 7.08l4.24 4.24M1 12h6m6 0h10M4.22 19.78l4.24-4.24m7.08-7.08l4.24-4.24"></path>
    </svg>
  ),
  Moon: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
    </svg>
  ),
  Sun: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5"></circle>
      <line x1="12" y1="1" x2="12" y2="3"></line>
      <line x1="12" y1="21" x2="12" y2="23"></line>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
      <line x1="1" y1="12" x2="3" y2="12"></line>
      <line x1="21" y1="12" x2="23" y2="12"></line>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
    </svg>
  ),
  Trash: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6"></polyline>
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
    </svg>
  ),
  Sparkles: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3L13.5 8.5L19 10L13.5 11.5L12 17L10.5 11.5L5 10L10.5 8.5L12 3Z"></path>
      <path d="M19 15L19.5 17L21.5 17.5L19.5 18L19 20L18.5 18L16.5 17.5L18.5 17L19 15Z"></path>
      <path d="M5 2L5.5 4L7.5 4.5L5.5 5L5 7L4.5 5L2.5 4.5L4.5 4L5 2Z"></path>
    </svg>
  ),
  Copy: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
    </svg>
  ),
  Check: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
  ),
  Menu: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="3" y1="12" x2="21" y2="12"></line>
      <line x1="3" y1="6" x2="21" y2="6"></line>
      <line x1="3" y1="18" x2="21" y2="18"></line>
    </svg>
  ),
  X: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"></line>
      <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
  ),
  Loader: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="animate-spin">
      <line x1="12" y1="2" x2="12" y2="6"></line>
      <line x1="12" y1="18" x2="12" y2="22"></line>
      <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
      <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
      <line x1="2" y1="12" x2="6" y2="12"></line>
      <line x1="18" y1="12" x2="22" y2="12"></line>
      <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
      <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
    </svg>
  ),
}

// Quick actions
const quickActions = [
  { label: 'Write Python code', prompt: 'Write a Python function to calculate factorial with proper documentation' },
  { label: 'Debug my code', prompt: 'Help me debug this code and explain what went wrong' },
  { label: 'Explain concept', prompt: 'Explain what is recursion in programming with simple examples' },
  { label: 'Best practices', prompt: 'What are the best practices for clean code in Python?' },
]

export default function Home() {
  // State
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [modelLoaded, setModelLoaded] = useState(false)
  const [modelLoading, setModelLoading] = useState(false)
  const [temperature, setTemperature] = useState(0.7)
  const [maxTokens, setMaxTokens] = useState(2048)
  const [reasoningMode, setReasoningMode] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [usage, setUsage] = useState({ messages: 0, tokens: 0, limit: { messages: 50, tokens: 50000 } })
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Apply theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.body.style.background = theme === 'dark' ? '#000' : '#fff'
    document.body.style.color = theme === 'dark' ? '#fff' : '#000'
  }, [theme])

  // Check model status
  const checkModelStatus = useCallback(async () => {
    try {
      const res = await fetch('/api/chat')
      const data = await res.json()
      setModelLoaded(data.modelLoaded || false)
    } catch {
      setModelLoaded(false)
    }
  }, [])

  useEffect(() => {
    checkModelStatus()
  }, [checkModelStatus])

  // Send message
  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: reasoningMode ? `Think step by step: ${content}` : content,
          temperature,
          maxTokens
        })
      })

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || data.error || 'Sorry, I could not generate a response.',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
      
      if (data.usage) {
        setUsage(data.usage)
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, something went wrong. Please make sure the backend server is running.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Handle submit
  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault()
    sendMessage(input)
  }

  // Handle keyboard
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  // Quick action click
  const handleQuickAction = (prompt: string) => {
    sendMessage(prompt)
  }

  // Copy message
  const copyMessage = (id: string, content: string) => {
    navigator.clipboard.writeText(content)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  // Clear chat
  const clearChat = () => {
    setMessages([])
  }

  // Format code in message
  const formatMessage = (content: string) => {
    // Simple markdown-like formatting
    return content.split('\n').map((line, i) => {
      // Code blocks
      if (line.startsWith('```')) {
        return null
      }
      // Inline code
      if (line.includes('`')) {
        return <p key={i} className="my-1" dangerouslySetInnerHTML={{ 
          __html: line.replace(/`([^`]+)`/g, '<code class="bg-gray-800 px-1.5 py-0.5 rounded text-sm font-mono text-green-400">$1</code>')
        }} />
      }
      return <p key={i} className="my-1">{line}</p>
    })
  }

  return (
    <div style={{ 
      display: 'flex', 
      height: '100vh', 
      background: theme === 'dark' ? '#000' : '#fff',
      color: theme === 'dark' ? '#fff' : '#000',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ x: -280, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -280, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            style={{
              width: 280,
              background: theme === 'dark' ? '#0a0a0a' : '#f5f5f5',
              borderRight: `1px solid ${theme === 'dark' ? '#1a1a1a' : '#e5e5e5'}`,
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {/* Logo */}
            <div style={{ 
              padding: '20px', 
              borderBottom: `1px solid ${theme === 'dark' ? '#1a1a1a' : '#e5e5e5'}` 
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{
                  width: 40,
                  height: 40,
                  borderRadius: 12,
                  background: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white'
                }}>
                  <Icons.Bot />
                </div>
                <div>
                  <h1 style={{ 
                    fontSize: 18, 
                    fontWeight: 600,
                    background: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}>Zord Coder</h1>
                  <p style={{ fontSize: 12, color: theme === 'dark' ? '#666' : '#999' }}>by SaJad</p>
                </div>
              </div>
            </div>

            {/* Settings */}
            <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
              {/* Theme Toggle */}
              <div style={{ marginBottom: 20 }}>
                <label style={{ 
                  fontSize: 11, 
                  fontWeight: 600, 
                  textTransform: 'uppercase', 
                  letterSpacing: '0.5px',
                  color: theme === 'dark' ? '#666' : '#999',
                  marginBottom: 8,
                  display: 'block'
                }}>
                  Appearance
                </label>
                <button
                  onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    borderRadius: 12,
                    border: 'none',
                    background: theme === 'dark' ? '#141414' : '#fff',
                    color: theme === 'dark' ? '#fff' : '#000',
                    cursor: 'pointer',
                    fontSize: 14
                  }}
                >
                  <span>{theme === 'dark' ? '🌙 Dark' : '☀️ Light'}</span>
                  <span style={{ opacity: 0.6 }}>{theme === 'dark' ? <Icons.Moon /> : <Icons.Sun />}</span>
                </button>
              </div>

              {/* Generation Settings */}
              <div style={{ marginBottom: 20 }}>
                <label style={{ 
                  fontSize: 11, 
                  fontWeight: 600, 
                  textTransform: 'uppercase', 
                  letterSpacing: '0.5px',
                  color: theme === 'dark' ? '#666' : '#999',
                  marginBottom: 12,
                  display: 'block'
                }}>
                  Generation
                </label>
                
                <div style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 6 }}>
                    <span>Temperature</span>
                    <span style={{ color: '#10B981' }}>{temperature}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    style={{ width: '100%', accentColor: '#10B981' }}
                  />
                </div>

                <div style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 6 }}>
                    <span>Max Tokens</span>
                    <span style={{ color: '#10B981' }}>{maxTokens}</span>
                  </div>
                  <input
                    type="range"
                    min="256"
                    max="4096"
                    step="256"
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                    style={{ width: '100%', accentColor: '#10B981' }}
                  />
                </div>

                <label style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  padding: '12px 16px',
                  borderRadius: 12,
                  background: theme === 'dark' ? '#141414' : '#fff',
                  cursor: 'pointer',
                  fontSize: 14
                }}>
                  <input
                    type="checkbox"
                    checked={reasoningMode}
                    onChange={(e) => setReasoningMode(e.target.checked)}
                    style={{ width: 16, height: 16, accentColor: '#10B981' }}
                  />
                  <span>🧠 Reasoning Mode</span>
                </label>
              </div>

              {/* Usage */}
              <div style={{ marginBottom: 20 }}>
                <label style={{ 
                  fontSize: 11, 
                  fontWeight: 600, 
                  textTransform: 'uppercase', 
                  letterSpacing: '0.5px',
                  color: theme === 'dark' ? '#666' : '#999',
                  marginBottom: 12,
                  display: 'block'
                }}>
                  Today's Usage
                </label>
                
                <div style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 4 }}>
                    <span>Messages</span>
                    <span style={{ color: theme === 'dark' ? '#666' : '#999' }}>{usage.messages} / {usage.limit.messages}</span>
                  </div>
                  <div style={{ 
                    height: 6, 
                    background: theme === 'dark' ? '#1a1a1a' : '#e5e5e5', 
                    borderRadius: 3,
                    overflow: 'hidden'
                  }}>
                    <div style={{ 
                      height: '100%', 
                      width: `${(usage.messages / usage.limit.messages) * 100}%`,
                      background: '#10B981',
                      borderRadius: 3,
                      transition: 'width 0.3s'
                    }} />
                  </div>
                </div>
                
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 4 }}>
                    <span>Tokens</span>
                    <span style={{ color: theme === 'dark' ? '#666' : '#999' }}>{usage.tokens.toLocaleString()} / {usage.limit.tokens.toLocaleString()}</span>
                  </div>
                  <div style={{ 
                    height: 6, 
                    background: theme === 'dark' ? '#1a1a1a' : '#e5e5e5', 
                    borderRadius: 3,
                    overflow: 'hidden'
                  }}>
                    <div style={{ 
                      height: '100%', 
                      width: `${(usage.tokens / usage.limit.tokens) * 100}%`,
                      background: '#10B981',
                      borderRadius: 3,
                      transition: 'width 0.3s'
                    }} />
                  </div>
                </div>
              </div>

              {/* Model Status */}
              <div>
                <label style={{ 
                  fontSize: 11, 
                  fontWeight: 600, 
                  textTransform: 'uppercase', 
                  letterSpacing: '0.5px',
                  color: theme === 'dark' ? '#666' : '#999',
                  marginBottom: 8,
                  display: 'block'
                }}>
                  Model Status
                </label>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '12px 16px',
                  borderRadius: 12,
                  background: theme === 'dark' ? '#141414' : '#fff',
                  fontSize: 14
                }}>
                  <div style={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: modelLoaded ? '#10B981' : modelLoading ? '#F59E0B' : '#EF4444'
                  }} />
                  <span>{modelLoaded ? 'Ready' : modelLoading ? 'Loading...' : 'Not Connected'}</span>
                </div>
              </div>
            </div>

            {/* Clear Chat */}
            <div style={{ 
              padding: 16, 
              borderTop: `1px solid ${theme === 'dark' ? '#1a1a1a' : '#e5e5e5'}` 
            }}>
              <button
                onClick={clearChat}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  padding: '12px 16px',
                  borderRadius: 12,
                  border: 'none',
                  background: theme === 'dark' ? '#141414' : '#fff',
                  color: theme === 'dark' ? '#fff' : '#000',
                  cursor: 'pointer',
                  fontSize: 14
                }}
              >
                <Icons.Trash />
                Clear Chat
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <header style={{
          height: 56,
          borderBottom: `1px solid ${theme === 'dark' ? '#1a1a1a' : '#e5e5e5'}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 16px',
          background: theme === 'dark' ? '#0a0a0a' : '#fafafa'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              style={{
                padding: 8,
                borderRadius: 8,
                border: 'none',
                background: 'transparent',
                color: theme === 'dark' ? '#fff' : '#000',
                cursor: 'pointer'
              }}
            >
              {sidebarOpen ? <Icons.X /> : <Icons.Menu />}
            </button>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ color: '#10B981' }}><Icons.Sparkles /></span>
              <span style={{ fontWeight: 600, fontSize: 16 }}>Zord Coder</span>
            </div>
          </div>

          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 8,
            padding: '6px 12px',
            borderRadius: 20,
            background: modelLoaded ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            fontSize: 13
          }}>
            <div style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: modelLoaded ? '#10B981' : '#EF4444'
            }} />
            <span style={{ color: modelLoaded ? '#10B981' : '#EF4444' }}>
              {modelLoaded ? 'Online' : 'Offline'}
            </span>
          </div>
        </header>

        {/* Chat Area */}
        <div style={{ 
          flex: 1, 
          overflow: 'auto', 
          padding: 20,
          display: 'flex',
          flexDirection: 'column'
        }}>
          {messages.length === 0 ? (
            /* Welcome Screen */
            <div style={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center',
              maxWidth: 600,
              margin: '0 auto',
              textAlign: 'center'
            }}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ marginBottom: 32 }}
              >
                <div style={{
                  width: 80,
                  height: 80,
                  borderRadius: 20,
                  background: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                  color: 'white',
                  fontSize: 32
                }}>
                  <Icons.Bot />
                </div>
                
                <h1 style={{ 
                  fontSize: 36, 
                  fontWeight: 700,
                  marginBottom: 8,
                  background: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}>Zord Coder</h1>
                <p style={{ 
                  fontSize: 16, 
                  color: theme === 'dark' ? '#666' : '#999' 
                }}>AI Coding Assistant by SaJad</p>
              </motion.div>

              {/* Quick Actions */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(2, 1fr)', 
                  gap: 12,
                  width: '100%',
                  marginBottom: 24
                }}
              >
                {quickActions.map((action, index) => (
                  <button
                    key={action.label}
                    onClick={() => handleQuickAction(action.prompt)}
                    style={{
                      padding: '16px 20px',
                      borderRadius: 16,
                      border: `1px solid ${theme === 'dark' ? '#1a1a1a' : '#e5e5e5'}`,
                      background: theme === 'dark' ? '#0a0a0a' : '#fafafa',
                      color: theme === 'dark' ? '#fff' : '#000',
                      cursor: 'pointer',
                      fontSize: 14,
                      fontWeight: 500,
                      textAlign: 'left',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#10B981'
                      e.currentTarget.style.background = theme === 'dark' ? '#141414' : '#fff'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = theme === 'dark' ? '#1a1a1a' : '#e5e5e5'
                      e.currentTarget.style.background = theme === 'dark' ? '#0a0a0a' : '#fafafa'
                    }}
                  >
                    {action.label}
                  </button>
                ))}
              </motion.div>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                style={{ color: theme === 'dark' ? '#444' : '#aaa', fontSize: 14 }}
              >
                Or start typing below to begin...
              </motion.p>
            </div>
          ) : (
            /* Messages */
            <div style={{ 
              maxWidth: 800, 
              width: '100%', 
              margin: '0 auto',
              display: 'flex',
              flexDirection: 'column',
              gap: 16
            }}>
              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
                  style={{
                    display: 'flex',
                    gap: 12,
                    flexDirection: message.role === 'user' ? 'row-reverse' : 'row'
                  }}
                >
                  {/* Avatar */}
                  <div style={{
                    width: 32,
                    height: 32,
                    borderRadius: 8,
                    background: message.role === 'user' ? '#10B981' : (theme === 'dark' ? '#1a1a1a' : '#e5e5e5'),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: message.role === 'user' ? 'white' : (theme === 'dark' ? '#10B981' : '#059669'),
                    flexShrink: 0
                  }}>
                    {message.role === 'user' ? <Icons.User /> : <Icons.Bot />}
                  </div>
                  
                  {/* Message Content */}
                  <div style={{ flex: 1, maxWidth: '80%' }}>
                    <div style={{
                      padding: '16px 20px',
                      borderRadius: 20,
                      background: message.role === 'user' 
                        ? '#10B981' 
                        : (theme === 'dark' ? '#0a0a0a' : '#f5f5f5'),
                      border: message.role === 'user' 
                        ? 'none' 
                        : `1px solid ${theme === 'dark' ? '#1a1a1a' : '#e5e5e5'}`,
                      color: message.role === 'user' ? 'white' : (theme === 'dark' ? '#fff' : '#000'),
                      fontSize: 15,
                      lineHeight: 1.6,
                      whiteSpace: 'pre-wrap'
                    }}>
                      {message.content}
                    </div>
                    
                    {/* Meta */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      marginTop: 4,
                      flexDirection: message.role === 'user' ? 'row-reverse' : 'row'
                    }}>
                      <button
                        onClick={() => copyMessage(message.id, message.content)}
                        style={{
                          padding: 4,
                          borderRadius: 4,
                          border: 'none',
                          background: 'transparent',
                          color: theme === 'dark' ? '#444' : '#aaa',
                          cursor: 'pointer'
                        }}
                      >
                        {copiedId === message.id ? <Icons.Check /> : <Icons.Copy />}
                      </button>
                      <span style={{ fontSize: 12, color: theme === 'dark' ? '#444' : '#aaa' }}>
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {/* Loading */}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  style={{ display: 'flex', gap: 12 }}
                >
                  <div style={{
                    width: 32,
                    height: 32,
                    borderRadius: 8,
                    background: theme === 'dark' ? '#1a1a1a' : '#e5e5e5',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#10B981'
                  }}>
                    <Icons.Bot />
                  </div>
                  <div style={{
                    padding: '16px 20px',
                    borderRadius: 20,
                    background: theme === 'dark' ? '#0a0a0a' : '#f5f5f5',
                    border: `1px solid ${theme === 'dark' ? '#1a1a1a' : '#e5e5e5'}`,
                    display: 'flex',
                    gap: 4,
                    alignItems: 'center'
                  }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#10B981', animation: 'bounce 1s infinite' }} />
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#10B981', animation: 'bounce 1s infinite 0.2s' }} />
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#10B981', animation: 'bounce 1s infinite 0.4s' }} />
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div style={{ 
          padding: '16px 20px', 
          borderTop: `1px solid ${theme === 'dark' ? '#1a1a1a' : '#e5e5e5'}`,
          background: theme === 'dark' ? '#0a0a0a' : '#fafafa'
        }}>
          <form 
            onSubmit={handleSubmit}
            style={{ maxWidth: 800, margin: '0 auto', position: 'relative' }}
          >
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask Zord Coder anything..."
              rows={1}
              style={{
                width: '100%',
                padding: '14px 50px 14px 20px',
                borderRadius: 24,
                border: `2px solid ${theme === 'dark' ? '#1a1a1a' : '#e5e5e5'}`,
                background: theme === 'dark' ? '#141414' : '#fff',
                color: theme === 'dark' ? '#fff' : '#000',
                fontSize: 15,
                resize: 'none',
                outline: 'none',
                fontFamily: 'inherit',
                lineHeight: 1.5,
                maxHeight: 120
              }}
            />
            
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              style={{
                position: 'absolute',
                right: 8,
                top: '50%',
                transform: 'translateY(-50%)',
                width: 40,
                height: 40,
                borderRadius: '50%',
                border: 'none',
                background: input.trim() ? '#10B981' : (theme === 'dark' ? '#1a1a1a' : '#e5e5e5'),
                color: input.trim() ? 'white' : (theme === 'dark' ? '#333' : '#ccc'),
                cursor: input.trim() ? 'pointer' : 'not-allowed',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s'
              }}
            >
              <Icons.Send />
            </button>
          </form>
          
          <p style={{ 
            textAlign: 'center', 
            fontSize: 12, 
            color: theme === 'dark' ? '#444' : '#aaa',
            marginTop: 8 
          }}>
            Press Enter to send • Shift+Enter for new line
          </p>
        </div>
      </main>

      {/* Animations */}
      <style jsx global>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-8px); }
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        .animate-spin {
          animation: spin 1s linear infinite;
        }
        
        * {
          box-sizing: border-box;
        }
        
        ::-webkit-scrollbar {
          width: 6px;
        }
        
        ::-webkit-scrollbar-track {
          background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
          background: ${theme === 'dark' ? '#1a1a1a' : '#e5e5e5'};
          border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: ${theme === 'dark' ? '#333' : '#ccc'};
        }
      `}</style>
    </div>
  )
}
