"""WebSocket event handlers for different types of updates."""
import logging
from typing import Dict, Any
from src.websocket.connection_manager import connection_manager
from src.models.user import UserRole
from src.models.package import Package, PackageStatus
from src.api.schemas.package import PackageResponse

logger = logging.getLogger(__name__)

class WebSocketEvents:
    """Handle WebSocket events and notifications."""
    
    @staticmethod
    async def package_created(package: Package):
        """Notify about new package creation."""
        try:
            package_data = PackageResponse.model_validate(package).model_dump()
            
            # Notify admin users
            await connection_manager.broadcast_to_role({
                "type": "package_created",
                "package": package_data,
                "message": f"New package created: {package.title}",
                "timestamp": "2024-01-01T00:00:00Z"
            }, UserRole.ADMIN)
            
            # Notify available couriers about new package
            await connection_manager.broadcast_to_role({
                "type": "new_package_available",
                "package": package_data,
                "message": f"New package available for pickup: {package.title}",
                "timestamp": "2024-01-01T00:00:00Z"
            }, UserRole.COURIER)
            
            logger.info(f"Package created notification sent: {package.id}")
            
        except Exception as e:
            logger.error(f"Error sending package created notification: {e}")
    
    @staticmethod
    async def package_status_updated(package: Package, old_status: str, new_status: str):
        """Notify about package status updates."""
        try:
            package_data = PackageResponse.model_validate(package).model_dump()
            
            message = {
                "type": "package_status_updated",
                "package": package_data,
                "old_status": old_status,
                "new_status": new_status,
                "message": f"Package {package.title} status changed from {old_status} to {new_status}",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            # Notify all subscribed users
            await connection_manager.notify_package_update(
                package.id, 
                package_data, 
                "status_updated"
            )
            
            # Send specific notifications based on status
            if new_status == PackageStatus.ASSIGNED.value:
                await WebSocketEvents._notify_package_assigned(package)
            elif new_status == PackageStatus.PICKED_UP.value:
                await WebSocketEvents._notify_package_picked_up(package)
            elif new_status == PackageStatus.DELIVERED.value:
                await WebSocketEvents._notify_package_delivered(package)
            elif new_status == PackageStatus.FAILED.value:
                await WebSocketEvents._notify_delivery_failed(package)
            
            logger.info(f"Package status update notification sent: {package.id}")
            
        except Exception as e:
            logger.error(f"Error sending package status update notification: {e}")
    
    @staticmethod
    async def _notify_package_assigned(package: Package):
        """Notify when package is assigned to courier."""
        if package.courier_id:
            await connection_manager.send_personal_message({
                "type": "package_assigned_to_you",
                "package_id": package.id,
                "message": f"Package '{package.title}' has been assigned to you",
                "timestamp": "2024-01-01T00:00:00Z"
            }, package.courier_id)
    
    @staticmethod
    async def _notify_package_picked_up(package: Package):
        """Notify when package is picked up."""
        # Notify sender if they have an account
        if package.sender_id:
            await connection_manager.send_personal_message({
                "type": "package_picked_up",
                "package_id": package.id,
                "message": f"Your package '{package.title}' has been picked up",
                "timestamp": "2024-01-01T00:00:00Z"
            }, package.sender_id)
    
    @staticmethod
    async def _notify_package_delivered(package: Package):
        """Notify when package is delivered."""
        # Notify sender
        if package.sender_id:
            await connection_manager.send_personal_message({
                "type": "package_delivered",
                "package_id": package.id,
                "message": f"Your package '{package.title}' has been delivered successfully",
                "timestamp": "2024-01-01T00:00:00Z"
            }, package.sender_id)
    
    @staticmethod
    async def _notify_delivery_failed(package: Package):
        """Notify when delivery fails."""
        # Notify sender and courier
        message = {
            "type": "delivery_failed",
            "package_id": package.id,
            "message": f"Delivery failed for package '{package.title}'",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        if package.sender_id:
            await connection_manager.send_personal_message(message, package.sender_id)
        
        if package.courier_id:
            await connection_manager.send_personal_message(message, package.courier_id)
    
    @staticmethod
    async def courier_location_updated(courier_id: int, location_data: Dict[str, Any]):
        """Notify about courier location updates."""
        try:
            # This would be enhanced later with actual location tracking
            message = {
                "type": "courier_location_updated",
                "courier_id": courier_id,
                "location": location_data,
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            # For now, just notify admin users
            await connection_manager.broadcast_to_role(message, UserRole.ADMIN)
            
            logger.debug(f"Courier location update sent: {courier_id}")
            
        except Exception as e:
            logger.error(f"Error sending courier location update: {e}")
    
    @staticmethod
    async def system_announcement(message: str, target_roles: list = None):
        """Send system-wide announcements."""
        try:
            announcement = {
                "type": "system_announcement",
                "message": message,
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            if target_roles:
                for role in target_roles:
                    await connection_manager.broadcast_to_role(announcement, role)
            else:
                await connection_manager.broadcast_to_all(announcement)
            
            logger.info(f"System announcement sent: {message}")
            
        except Exception as e:
            logger.error(f"Error sending system announcement: {e}")

# Global events instance
websocket_events = WebSocketEvents()    