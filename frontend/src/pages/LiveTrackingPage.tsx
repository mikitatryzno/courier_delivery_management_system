import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useWebSocketContext } from '../components/common/WebSocketProvider'

export default function LiveTrackingPage() {
  const { deliveryId } = useParams<{ deliveryId: string }>()
  const { isConnected, lastMessage, sendMessage } = useWebSocketContext()
  const [location, setLocation] = useState<{ lat?: number; lng?: number }>(() => ({}))

  useEffect(() => {
    if (!deliveryId) return

    // Subscribe to delivery updates when connected
    if (isConnected) {
      sendMessage({ type: 'subscribe_delivery', delivery_id: Number(deliveryId) })
    }

    return () => {
      if (isConnected) {
        sendMessage({ type: 'unsubscribe_delivery', delivery_id: Number(deliveryId) })
      }
    }
  }, [deliveryId, isConnected, sendMessage])

  useEffect(() => {
    if (!lastMessage) return
    if (lastMessage.type === 'delivery_location' && Number(lastMessage.delivery_id) === Number(deliveryId)) {
      setLocation({ lat: Number(lastMessage.lat), lng: Number(lastMessage.lng) })
    }
  }, [lastMessage, deliveryId])

  return (
    <div className="live-tracking">
      <h2>Live Tracking: Delivery {deliveryId}</h2>
      <p>WebSocket status: {isConnected ? 'Connected' : 'Disconnected'}</p>

      <div>
        <strong>Current location:</strong>
        {location.lat !== undefined ? (
          <div>
            <div>Latitude: {location.lat}</div>
            <div>Longitude: {location.lng}</div>
          </div>
        ) : (
          <div>No location updates yet.</div>
        )}
      </div>
    </div>
  )
}
