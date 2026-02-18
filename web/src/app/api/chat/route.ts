import { NextRequest, NextResponse } from 'next/server'

// Simple in-memory usage tracking (for demo - use Redis/DB in production)
const usageStore = new Map<string, { messages: number; tokens: number; resetAt: Date }>()

const DAILY_LIMIT = 50
const TOKEN_LIMIT = 50000

function getClientId(request: NextRequest): string {
  // Simple: use IP + user agent as ID
  const ip = request.headers.get('x-forwarded-for') || 'unknown'
  const ua = request.headers.get('user-agent') || 'unknown'
  return `${ip}-${ua}`.slice(0, 50)
}

function getUsage(clientId: string) {
  const now = new Date()
  const usage = usageStore.get(clientId)
  
  // Reset if new day
  if (!usage || usage.resetAt < now) {
    return { messages: 0, tokens: 0, resetAt: new Date(now.getTime() + 24 * 60 * 60 * 1000) }
  }
  
  return usage
}

function updateUsage(clientId: string, tokens: number) {
  const usage = getUsage(clientId)
  usage.messages += 1
  usage.tokens += tokens
  usageStore.set(clientId, usage)
}

export async function POST(request: NextRequest) {
  try {
    const clientId = getClientId(request)
    const usage = getUsage(clientId)
    
    // Check limits
    if (usage.messages >= DAILY_LIMIT) {
      return NextResponse.json(
        { error: 'Daily message limit reached. Come back tomorrow!' },
        { status: 429 }
      )
    }
    
    if (usage.tokens >= TOKEN_LIMIT) {
      return NextResponse.json(
        { error: 'Daily token limit reached. Come back tomorrow!' },
        { status: 429 }
      )
    }
    
    const body = await request.json()
    const { message, temperature = 0.7, maxTokens = 2048 } = body
    
    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }
    
    // Call Python backend (llama.cpp server)
    // This assumes a local Python server is running
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 120000) // 2 min timeout
    
    try {
      const response = await fetch(`${backendUrl}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: message,
          temperature,
          max_tokens: maxTokens,
          stream: false
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        const error = await response.text()
        return NextResponse.json(
          { error: `Backend error: ${error}` },
          { status: response.status }
        )
      }
      
      const data = await response.json()
      
      // Update usage
      const tokensUsed = data.tokens_generated || message.length / 4
      updateUsage(clientId, tokensUsed)
      
      return NextResponse.json({
        response: data.response,
        tokens: tokensUsed,
        usage: {
          messages: usage.messages + 1,
          tokens: usage.tokens + tokensUsed
        }
      })
      
    } catch (fetchError: any) {
      clearTimeout(timeoutId)
      
      // If backend not available, return a helpful message
      if (fetchError.name === 'AbortError') {
        return NextResponse.json(
          { error: 'Request timed out. Please try again.' },
          { status: 504 }
        )
      }
      
      // Return mock response for demo (when backend not running)
      return NextResponse.json({
        response: `Demo mode: Backend not connected.\n\nYour message was: "${message.slice(0, 100)}..."\n\nTo use the AI, please:\n1. Start the Python backend server\n2. Or check the model is loaded`,
        tokens: message.length / 4,
        usage: {
          messages: usage.messages + 1,
          tokens: usage.tokens + message.length / 4
        },
        demo: true
      })
    }
    
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({ 
    status: 'ok',
    message: 'Zord Coder API v1',
    endpoints: {
      POST: '/api/chat - Send a message'
    }
  })
}
