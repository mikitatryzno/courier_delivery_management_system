import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuth } from './useAuth'

interface WebSocketMessage {
  type: string
  [key: string]: any
}

interface UseWebSocketReturn {
  isConnected: boolean
  lastMessage: WebSocketMessage | null
  sendMessage: (message: any) => void
  connectionError: string | null
}

export function useWebSocket(): UseWebSocketReturn {
  const { user, isAuthenticated } = useAuth()
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connect = useCallback(() => {
    if (!isAuthenticated || !user) {
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setConnectionError('No access token available')
        return
      }

      const wsUrl = `ws://localhost:8000/api/ws/connect?token=${token}`
      ws.current = new WebSocket(wsUrl)

      ws.current.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setConnectionError(null)
        reconnectAttempts.current = 0
      }

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          setLastMessage(message)
          console.log('WebSocket message received:', message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        
        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.pow(2, reconnectAttempts.current) * 1000 // Exponential backoff
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++
            console.log(`Reconnecting... Attempt ${reconnectAttempts.current}`)
            connect()
          }, delay)
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionError('WebSocket connection error')
      }

    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
      setConnectionError('Failed to create WebSocket connection')
    }
  }, [isAuthenticated, user])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (ws.current) {
      ws.current.close(1000, 'Normal closure')
      ws.current = null
    }
    
    setIsConnected(false)
    setLastMessage(null)
  }, [])

  const sendMessage = useCallback((message: any) => {
    if (ws.current && isConnected) {
      try {
        ws.current.send(JSON.stringify(message))
      } catch (error) {
        console.error('Error sending WebSocket message:', error)
      }
    } else {
      console.warn('WebSocket not connected, cannot send message')
    }
  }, [isConnected])

  useEffect(() => {
    if (isAuthenticated && user) {
      connect()
    } else {
      disconnect()
    }

    return () => {
      disconnect()
    }
  }, [isAuthenticated, user, connect, disconnect])

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connectionError
  }
}