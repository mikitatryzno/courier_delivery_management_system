import { useEffect, useState } from 'react'
import { useWebSocketContext } from './WebSocketProvider'
import { Bell, X, Package, Truck, CheckCircle, AlertCircle } from 'lucide-react'

interface Notification {
  id: string
  type: string
  message: string
  timestamp: string
  read: boolean
}

export default function NotificationCenter() {
  const { lastMessage } = useWebSocketContext()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    if (lastMessage && shouldShowNotification(lastMessage.type)) {
      const notification: Notification = {
        id: Date.now().toString(),
        type: lastMessage.type,
        message: lastMessage.message || 'New update received',
        timestamp: lastMessage.timestamp || new Date().toISOString(),
        read: false
      }

      setNotifications(prev => [notification, ...prev.slice(0, 9)]) // Keep last 10
      
      // Show browser notification if permission granted
      if (Notification.permission === 'granted') {
        new Notification('Courier Delivery Update', {
          body: notification.message,
          icon: '/favicon.ico'
        })
      }
    }
  }, [lastMessage])

  const shouldShowNotification = (type: string): boolean => {
    const notificationTypes = [
      'package_created',
      'package_status_updated',
      'package_assigned_to_you',
      'package_picked_up',
      'package_delivered',
      'delivery_failed',
      'system_announcement'
    ]
    return notificationTypes.includes(type)
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'package_created':
      case 'new_package_available':
        return <Package className="h-4 w-4 text-blue-500" />
      case 'package_assigned_to_you':
      case 'package_picked_up':
        return <Truck className="h-4 w-4 text-yellow-500" />
      case 'package_delivered':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'delivery_failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Bell className="h-4 w-4 text-gray-500" />
    }
  }

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      )
    )
  }

  const clearAll = () => {
    setNotifications([])
  }

  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900"
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Notifications</h3>
              <div className="flex items-center space-x-2">
                {notifications.length > 0 && (
                  <button
                    onClick={clearAll}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    Clear all
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No notifications yet
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                    !notification.read ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="flex items-start space-x-3">
                    {getNotificationIcon(notification.type)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900">{notification.message}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(notification.timestamp).toLocaleString()}
                      </p>
                    </div>
                    {!notification.read && (
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}