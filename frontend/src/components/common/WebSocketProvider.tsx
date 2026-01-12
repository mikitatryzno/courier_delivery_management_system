import React, { createContext, useContext, ReactNode } from 'react'
import { useWebSocket } from '@/hooks/useWebSocket'

interface WebSocketContextType {
  isConnected: boolean
  lastMessage: any
  sendMessage: (message: any) => void
  connectionError: string | null
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

interface WebSocketProviderProps {
  children: ReactNode
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const websocket = useWebSocket()

  return (
    <WebSocketContext.Provider value={websocket}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocketContext() {
  const context = useContext(WebSocketContext)
  if (context === undefined) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider')
  }
  return context
}