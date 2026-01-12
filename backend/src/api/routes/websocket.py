"""WebSocket routes for real-time updates."""
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.websocket.connection_manager import connection_manager
from src.websocket.auth import authenticate_websocket, close_websocket_with_error
from src.models.package import Package
from src.api.schemas.package import PackageResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time updates."""
    user = None
    
    try:
        # Authenticate user
        user = await authenticate_websocket(websocket, token)
        if not user:
            await close_websocket_with_error(
                websocket, 
                code=4001, 
                reason="Authentication failed"
            )
            return
        
        # Connect user
        await connection_manager.connect(websocket, user)
        
        # Auto-subscribe to relevant packages based on user role
        await auto_subscribe_user_packages(user, db)
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await handle_websocket_message(user, message, db)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected normally for user {user.id}")
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from user {user.id}")
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, user.id)
            except Exception as e:
                logger.error(f"Error handling WebSocket message for user {user.id}: {e}")
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Message processing failed"
                }, user.id)
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        if user:
            connection_manager.disconnect(user.id)
    finally:
        if user:
            connection_manager.disconnect(user.id)

async def auto_subscribe_user_packages(user, db: Session):
    """Auto-subscribe user to relevant packages based on their role."""
    try:
        packages = []
        
        if user.role.value == "admin":
            # Admin sees all packages
            packages = db.query(Package).all()
        elif user.role.value == "courier":
            # Courier sees assigned packages and unassigned packages
            packages = db.query(Package).filter(
                (Package.courier_id == user.id) | 
                (Package.courier_id.is_(None))
            ).all()
        elif user.role.value == "sender":
            # Sender sees their own packages
            packages = db.query(Package).filter(Package.sender_id == user.id).all()
        elif user.role.value == "recipient":
            # Recipient sees packages addressed to them
            packages = db.query(Package).filter(
                (Package.recipient_name == user.name) |
                (Package.recipient_phone == user.phone)
            ).all()
        
        # Subscribe to all relevant packages
        for package in packages:
            await connection_manager.subscribe_to_package(user.id, package.id)
        
        logger.info(f"Auto-subscribed user {user.id} to {len(packages)} packages")
        
    except Exception as e:
        logger.error(f"Error auto-subscribing user {user.id}: {e}")

async def handle_websocket_message(user, message: dict, db: Session):
    """Handle incoming WebSocket messages from clients."""
    try:
        message_type = message.get("type")
        
        if message_type == "ping":
            # Respond to ping with pong
            await connection_manager.send_personal_message({
                "type": "pong",
                "timestamp": "2024-01-01T00:00:00Z"
            }, user.id)
            
        elif message_type == "subscribe_package":
            # Subscribe to specific package updates
            package_id = message.get("package_id")
            if package_id:
                await connection_manager.subscribe_to_package(user.id, int(package_id))
            
        elif message_type == "unsubscribe_package":
            # Unsubscribe from specific package updates
            package_id = message.get("package_id")
            if package_id:
                await connection_manager.unsubscribe_from_package(user.id, int(package_id))
                
        elif message_type == "subscribe_delivery":
            delivery_id = message.get("delivery_id")
            if delivery_id:
                await connection_manager.subscribe_to_delivery(user.id, int(delivery_id))

        elif message_type == "unsubscribe_delivery":
            delivery_id = message.get("delivery_id")
            if delivery_id:
                await connection_manager.unsubscribe_from_delivery(user.id, int(delivery_id))
                
        elif message_type == "get_stats":
            # Send connection statistics (admin only)
            if user.role.value == "admin":
                stats = connection_manager.get_connection_stats()
                await connection_manager.send_personal_message({
                    "type": "stats",
                    "data": stats
                }, user.id)
            else:
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Insufficient permissions"
                }, user.id)
                
        else:
            logger.warning(f"Unknown message type from user {user.id}: {message_type}")
            await connection_manager.send_personal_message({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }, user.id)
            
    except Exception as e:
        logger.error(f"Error handling message from user {user.id}: {e}")
        await connection_manager.send_personal_message({
            "type": "error",
            "message": "Message handling failed"
        }, user.id)