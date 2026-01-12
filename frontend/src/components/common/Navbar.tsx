import { useAuth } from '@/hooks/useAuth'
import { useWebSocketContext } from './WebSocketProvider'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import NotificationCenter from './NotificationCenter'
import { LogOut, User, Wifi, WifiOff } from 'lucide-react'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { isConnected } = useWebSocketContext()

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-gray-900">
              Courier Delivery System
            </h1>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* WebSocket Connection Status */}
            <div className="flex items-center space-x-1">
              {isConnected ? (
                <Wifi className="h-4 w-4 text-green-500" title="Connected to real-time updates" />
              ) : (
                <WifiOff className="h-4 w-4 text-red-500" title="Disconnected from real-time updates" />
              )}
            </div>

            {/* Notification Center */}
            <NotificationCenter />
            
            <div className="flex items-center space-x-2">
              <User className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-700">{user?.name}</span>
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                {user?.role}
              </span>
            </div>

            {/* Quick live-tracking jump */}
            <LiveTrackingJump />
            
            <button
              onClick={logout}
              className="flex items-center space-x-1 text-gray-500 hover:text-gray-700"
            >
              <LogOut className="h-4 w-4" />
              <span className="text-sm">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

function LiveTrackingJump() {
  const [id, setId] = useState('')
  const navigate = useNavigate()

  return (
    <div className="flex items-center space-x-2">
      <input
        value={id}
        onChange={(e) => setId(e.target.value)}
        placeholder="Delivery #"
        className="border px-2 py-1 rounded text-sm w-20"
      />
      <button
        onClick={() => {
          if (id) navigate(`/track/${id}`)
        }}
        className="text-sm bg-blue-600 text-white px-2 py-1 rounded"
      >
        Track
      </button>
    </div>
  )
}