'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  Bot, 
  User, 
  Settings, 
  Moon, 
  Sun, 
  Trash2, 
  Sparkles,
  Code2,
  Bug,
  Lightbulb,
  Zap,
  MessageCircle,
  Menu,
  X,
  ChevronDown,
  Copy,
  Check
} from 'lucide-react'

// Types
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface Settings {
  temperature: number
  maxTokens: number
  reasoningMode: boolean
}

// Quick actions
const quickActions = [
  { label: 'Write Python', icon: Code2, prompt: 'Write a Python function to calculate factorial with proper documentation' },
  { label: 'Debug Code', icon: Bug, prompt: 'Help me debug this JavaScript code: function add(a,b) return a + b' },
  { label: 'Explain', icon: Lightbulb, prompt: 'Explain what is recursion in programming with examples' },
  { label: 'Best Practices', icon: Zap, prompt: 'What are the best practices for Python development in 2024?' },
]

export default function Home() {
  // State
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [settings, setSettings] = useState<Settings>({
    temperature: 0.7,
    maxTokens: 2048,
    reasoningMode: false
  })
  const [usage, setUsage] = useState({ messages: 0, tokens: 0 })
  const [modelLoaded, setModelLoaded] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Apply theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  // Toggle theme
  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark')
  }

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
          message: settings.reasoningMode ? `Think step by step: ${content}` : content,
          temperature: settings.temperature,
          maxTokens: settings.maxTokens
        })
      })

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || data.error || 'No response',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Update usage (mock for now)
      setUsage(prev => ({
        messages: prev.messages + 1,
        tokens: prev.tokens + (data.tokens || 0)
      }))
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
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

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="w-[280px] bg-[var(--bg-secondary)] border-r border-[var(--bg-border)] flex flex-col"
          >
            {/* Logo */}
            <div className="p-4 border-b border-[var(--bg-border)]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-light)] flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="font-semibold text-lg gradient-text">Zord Coder</h1>
                  <p className="text-xs text-[var(--text-muted)]">by SaJad</p>
                </div>
              </div>
            </div>

            {/* Settings */}
            <div className="p-4 space-y-4 flex-1 overflow-y-auto">
              {/* Theme Toggle */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">Appearance</label>
                <button
                  onClick={toggleTheme}
                  className="w-full flex items-center justify-between p-3 rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--bg-border)] transition-colors"
                >
                  <span className="text-sm">{theme === 'dark' ? '🌙 Dark' : '☀️ Light'}</span>
                  {theme === 'dark' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
                </button>
              </div>

              {/* Generation Settings */}
              <div className="space-y-3">
                <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">Generation</label>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Temperature</span>
                    <span className="text-[var(--accent)]">{settings.temperature}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={settings.temperature}
                    onChange={(e) => setSettings(s => ({ ...s, temperature: parseFloat(e.target.value) }))}
                    className="w-full accent"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Max Tokens</span>
                    <span className="text-[var(--accent)]">{settings.maxTokens}</span>
                  </div>
                  <input
                    type="range"
                    min="256"
                    max="4096"
                    step="256"
                    value={settings.maxTokens}
                    onChange={(e) => setSettings(s => ({ ...s, maxTokens: parseInt(e.target.value) }))}
                    className="w-full accent"
                  />
                </div>

                <label className="flex items-center gap-3 p-3 rounded-xl bg-[var(--bg-tertiary)] cursor-pointer hover:bg-[var(--bg-border)] transition-colors">
                  <input
                    type="checkbox"
                    checked={settings.reasoningMode}
                    onChange={(e) => setSettings(s => ({ ...s, reasoningMode: e.target.checked }))}
                    className="w-4 h-4 accent"
                  />
                  <span className="text-sm">🧠 Reasoning Mode</span>
                </label>
              </div>

              {/* Usage */}
              <div className="space-y-3">
                <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">Today's Usage</label>
                
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Messages</span>
                      <span className="text-[var(--text-muted)]">0 / 50</span>
                    </div>
                    <div className="h-2 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
                      <div className="h-full w-0 bg-[var(--accent)] rounded-full" style={{ width: '0%' }} />
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Tokens</span>
                      <span className="text-[var(--text-muted)]">0 / 50K</span>
                    </div>
                    <div className="h-2 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
                      <div className="h-full w-0 bg-[var(--accent)] rounded-full" style={{ width: '0%' }} />
                    </div>
                  </div>
                </div>
              </div>

              {/* Model Status */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">Model</label>
                <div className="flex items-center gap-2 p-3 rounded-xl bg-[var(--bg-tertiary)]">
                  <div className={`w-2 h-2 rounded-full ${modelLoaded ? 'bg-green-500' : 'bg-yellow-500'}`} />
                  <span className="text-sm">{modelLoaded ? 'Loaded' : 'Not Loaded'}</span>
                </div>
              </div>
            </div>

            {/* Clear Chat */}
            <div className="p-4 border-t border-[var(--bg-border)]">
              <button
                onClick={clearChat}
                className="w-full flex items-center justify-center gap-2 p-3 rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--bg-border)] transition-colors text-sm"
              >
                <Trash2 className="w-4 h-4" />
                Clear Chat
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-14 border-b border-[var(--bg-border)] flex items-center justify-between px-4 bg-[var(--bg-secondary)]">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-[var(--bg-tertiary)] transition-colors"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[var(--accent)]" />
              <span className="font-semibold">Zord Coder</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-[var(--text-muted)]">v1.0.0</span>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            /* Welcome Screen */
            <div className="max-w-2xl mx-auto mt-20 space-y-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center space-y-4"
              >
                <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-light)] flex items-center justify-center">
                  <Bot className="w-10 h-10 text-white" />
                </div>
                
                <h1 className="text-4xl font-bold gradient-text">Zord Coder</h1>
                <p className="text-[var(--text-secondary)] text-lg">AI Coding Assistant by SaJad</p>
              </motion.div>

              {/* Quick Actions */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="grid grid-cols-2 gap-3"
              >
                {quickActions.map((action, index) => (
                  <button
                    key={action.label}
                    onClick={() => handleQuickAction(action.prompt)}
                    className="flex items-center gap-3 p-4 rounded-xl bg-[var(--bg-secondary)] border border-[var(--bg-border)] hover:border-[var(--accent)] hover:bg-[var(--bg-tertiary)] transition-all group"
                  >
                    <action.icon className="w-5 h-5 text-[var(--accent)] group-hover:scale-110 transition-transform" />
                    <span className="text-sm font-medium">{action.label}</span>
                  </button>
                ))}
              </motion.div>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="text-center text-[var(--text-muted)] text-sm"
              >
                Or start typing below to begin...
              </motion.p>
            </div>
          ) : (
            /* Messages */
            <div className="max-w-3xl mx-auto space-y-4">
              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
                    message.role === 'user' 
                      ? 'bg-[var(--accent)]' 
                      : 'bg-[var(--bg-tertiary)] border border-[var(--bg-border)]'
                  }`}>
                    {message.role === 'user' ? (
                      <User className="w-4 h-4 text-white" />
                    ) : (
                      <Bot className="w-4 h-4 text-[var(--accent)]" />
                    )}
                  </div>
                  
                  <div className={`flex-1 max-w-[80%] ${message.role === 'user' ? 'text-right' : ''}`}>
                    <div className={`inline-block p-4 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-[var(--accent)] text-white'
                        : 'bg-[var(--bg-secondary)] border border-[var(--bg-border)]'
                    }`}>
                      <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                    </div>
                    
                    <div className={`flex items-center gap-2 mt-1 ${message.role === 'user' ? 'justify-end' : ''}`}>
                      <button
                        onClick={() => copyMessage(message.id, message.content)}
                        className="p-1 rounded hover:bg-[var(--bg-tertiary)] transition-colors"
                      >
                        {copiedId === message.id ? (
                          <Check className="w-3 h-3 text-green-500" />
                        ) : (
                          <Copy className="w-3 h-3 text-[var(--text-muted)]" />
                        )}
                      </button>
                      <span className="text-xs text-[var(--text-muted)]">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-3"
                >
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--bg-border)] flex items-center justify-center">
                    <Bot className="w-4 h-4 text-[var(--accent)]" />
                  </div>
                  <div className="bg-[var(--bg-secondary)] border border-[var(--bg-border)] rounded-2xl p-4">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-[var(--bg-border)] bg-[var(--bg-secondary)]">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit()
                  }
                }}
                placeholder="Ask Zord Coder anything..."
                rows={1}
                className="w-full bg-[var(--bg-tertiary)] border border-[var(--bg-border)] rounded-2xl pl-4 pr-12 py-3 text-sm resize-none focus:outline-none focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/20"
                style={{ maxHeight: '120px' }}
              />
              
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-xl bg-[var(--accent)] text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--accent-dark)] transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            
            <p className="text-center text-xs text-[var(--text-muted)] mt-2">
              Press Enter to send, Shift+Enter for new line
            </p>
          </form>
        </div>
      </main>
    </div>
  )
}
