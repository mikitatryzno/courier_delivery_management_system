"""WebSocket connection manager for real-time updates."""
import json
import logging
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from src.models.user import User, UserRole
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Store active connections by user ID
        self.active_connections: Dict[int, WebSocket] = {}
        # Store connections by user role for broadcasting
        self.connections_by_role: Dict[UserRole, Set[int]] = {
            UserRole.ADMIN: set(),
            UserRole.COURIER: set(),
            UserRole.SENDER: set(),
            UserRole.RECIPIENT: set()
        }
        # Store package subscriptions (user_id -> set of package_ids)
        self.package_subscriptions: Dict[int, Set[int]] = {}
        # Store delivery subscriptions (user_id -> set of delivery_ids)
        self.delivery_subscriptions: Dict[int, Set[int]] = {}
        # Event loop used by the running ASGI server (set on first connect)
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
    async def connect(self, websocket: WebSocket, user: User):
        """Accept a new WebSocket connection."""
        try:
            await websocket.accept()
            # Capture the running event loop so background tasks can be scheduled
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:
                self.loop = None
            
            # Store connection
            self.active_connections[user.id] = websocket
            self.connections_by_role[user.role].add(user.id)
            
            # Initialize package subscriptions
            if user.id not in self.package_subscriptions:
                self.package_subscriptions[user.id] = set()
            
            logger.info(f"WebSocket connected: User {user.id} ({user.email}) - Role: {user.role}")
            
            # Send welcome message
            await self.send_personal_message({
                "type": "connection_established",
                "message": "Connected to real-time updates",
                "user_id": user.id,
                "role": user.role.value
            }, user.id)
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket for user {user.id}: {e}")
            raise
    
    def disconnect(self, user_id: int):
        """Remove a WebSocket connection."""
        try:
            if user_id in self.active_connections:
                # Remove from active connections
                del self.active_connections[user_id]
                
                # Remove from role-based connections
                for role_set in self.connections_by_role.values():
                    role_set.discard(user_id)
                
                # Remove package subscriptions
                if user_id in self.package_subscriptions:
                    del self.package_subscriptions[user_id]

            # If no active connections remain, clear stored loop
            if not self.active_connections:
                self.loop = None
                
                logger.info(f"WebSocket disconnected: User {user_id}")
                
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket for user {user_id}: {e}")
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: int):
        """Send a message to a specific user."""
        try:
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message))
                logger.debug(f"Message sent to user {user_id}: {message['type']}")
            else:
                logger.warning(f"User {user_id} not connected for personal message")
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected during message send to user {user_id}")
            self.disconnect(user_id)
        except Exception as e:
            logger.error(f"Error sending personal message to user {user_id}: {e}")
    
    async def broadcast_to_role(self, message: Dict[str, Any], role: UserRole):
        """Broadcast a message to all users with a specific role."""
        try:
            user_ids = list(self.connections_by_role[role])
            if not user_ids:
                logger.debug(f"No users connected with role {role} for broadcast")
                return
            
            # Send to all users with the role
            disconnected_users = []
            for user_id in user_ids:
                try:
                    await self.send_personal_message(message, user_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
                    disconnected_users.append(user_id)
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                self.disconnect(user_id)
                
            logger.debug(f"Broadcast sent to {len(user_ids)} users with role {role}")
            
        except Exception as e:
            logger.error(f"Error broadcasting to role {role}: {e}")
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all connected users."""
        try:
            user_ids = list(self.active_connections.keys())
            if not user_ids:
                logger.debug("No users connected for broadcast")
                return
            
            disconnected_users = []
            for user_id in user_ids:
                try:
                    await self.send_personal_message(message, user_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
                    disconnected_users.append(user_id)
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                self.disconnect(user_id)
                
            logger.debug(f"Broadcast sent to {len(user_ids)} users")
            
        except Exception as e:
            logger.error(f"Error broadcasting to all users: {e}")
    
    async def subscribe_to_package(self, user_id: int, package_id: int):
        """Subscribe a user to package updates."""
        try:
            if user_id not in self.package_subscriptions:
                self.package_subscriptions[user_id] = set()
            
            self.package_subscriptions[user_id].add(package_id)
            
            await self.send_personal_message({
                "type": "package_subscribed",
                "package_id": package_id,
                "message": f"Subscribed to package {package_id} updates"
            }, user_id)
            
            logger.debug(f"User {user_id} subscribed to package {package_id}")
            
        except Exception as e:
            logger.error(f"Error subscribing user {user_id} to package {package_id}: {e}")
    
    async def unsubscribe_from_package(self, user_id: int, package_id: int):
        """Unsubscribe a user from package updates."""
        try:
            if user_id in self.package_subscriptions:
                self.package_subscriptions[user_id].discard(package_id)
            
            await self.send_personal_message({
                "type": "package_unsubscribed",
                "package_id": package_id,
                "message": f"Unsubscribed from package {package_id} updates"
            }, user_id)
            
            logger.debug(f"User {user_id} unsubscribed from package {package_id}")
            
        except Exception as e:
            logger.error(f"Error unsubscribing user {user_id} from package {package_id}: {e}")
    
    async def notify_package_update(self, package_id: int, package_data: Dict[str, Any], update_type: str = "updated"):
        """Notify all subscribed users about package updates."""
        try:
            # Find all users subscribed to this package
            subscribed_users = []
            for user_id, package_ids in self.package_subscriptions.items():
                if package_id in package_ids:
                    subscribed_users.append(user_id)
            
            if not subscribed_users:
                logger.debug(f"No users subscribed to package {package_id}")
                return
            
            message = {
                "type": "package_update",
                "update_type": update_type,
                "package_id": package_id,
                "package": package_data,
                "timestamp": "2024-01-01T00:00:00Z"  # This would be dynamic
            }
            
            # Send to all subscribed users
            for user_id in subscribed_users:
                await self.send_personal_message(message, user_id)
            
            logger.info(f"Package {package_id} update sent to {len(subscribed_users)} users")
            
        except Exception as e:
            logger.error(f"Error notifying package {package_id} update: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "connections_by_role": {
                role.value: len(user_ids) 
                for role, user_ids in self.connections_by_role.items()
            },
            "total_package_subscriptions": sum(
                len(packages) for packages in self.package_subscriptions.values()
            ),
            "total_delivery_subscriptions": sum(
                len(ds) for ds in self.delivery_subscriptions.values()
            )
        }

    async def subscribe_to_delivery(self, user_id: int, delivery_id: int):
        """Subscribe a user to delivery location updates."""
        try:
            if user_id not in self.delivery_subscriptions:
                self.delivery_subscriptions[user_id] = set()

            self.delivery_subscriptions[user_id].add(delivery_id)

            await self.send_personal_message({
                "type": "delivery_subscribed",
                "delivery_id": delivery_id,
                "message": f"Subscribed to delivery {delivery_id} location updates"
            }, user_id)

            logger.debug(f"User {user_id} subscribed to delivery {delivery_id}")
        except Exception as e:
            logger.error(f"Error subscribing user {user_id} to delivery {delivery_id}: {e}")

    async def unsubscribe_from_delivery(self, user_id: int, delivery_id: int):
        """Unsubscribe a user from delivery updates."""
        try:
            if user_id in self.delivery_subscriptions:
                self.delivery_subscriptions[user_id].discard(delivery_id)

            await self.send_personal_message({
                "type": "delivery_unsubscribed",
                "delivery_id": delivery_id,
                "message": f"Unsubscribed from delivery {delivery_id} updates"
            }, user_id)

            logger.debug(f"User {user_id} unsubscribed from delivery {delivery_id}")
        except Exception as e:
            logger.error(f"Error unsubscribing user {user_id} from delivery {delivery_id}: {e}")

    async def notify_delivery_location(self, delivery_id: int, lat: float, lng: float, timestamp: Optional[str] = None):
        """Notify subscribed users about delivery location updates."""
        try:
            subscribed_users = []
            for user_id, delivery_ids in self.delivery_subscriptions.items():
                if delivery_id in delivery_ids:
                    subscribed_users.append(user_id)

            if not subscribed_users:
                logger.debug(f"No users subscribed to delivery {delivery_id}")
                return

            message = {
                "type": "delivery_location",
                "delivery_id": delivery_id,
                "lat": lat,
                "lng": lng,
                "timestamp": timestamp or "2024-01-01T00:00:00Z"
            }

            for user_id in subscribed_users:
                await self.send_personal_message(message, user_id)

            logger.info(f"Delivery {delivery_id} location update sent to {len(subscribed_users)} users")
        except Exception as e:
            logger.error(f"Error notifying delivery {delivery_id} location update: {e}")

# Global connection manager instance
connection_manager = ConnectionManager()