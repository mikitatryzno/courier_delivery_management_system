"""Delivery service for handling delivery lifecycle and location updates."""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from src.models.delivery import Delivery, DeliveryStatus
from src.models.package import Package
from src.models.user import User, UserRole
import logging
import asyncio
from src.websocket.connection_manager import connection_manager

logger = logging.getLogger(__name__)


class DeliveryService:
    def __init__(self, db: Session):
        self.db = db

    def create_delivery(self, package_id: int) -> Optional[Delivery]:
        package = self.db.query(Package).filter(Package.id == package_id).first()
        if not package:
            return None

        delivery = Delivery(package_id=package_id, status=DeliveryStatus.CREATED)
        try:
            self.db.add(delivery)
            self.db.commit()
            self.db.refresh(delivery)
            logger.info(f"Created delivery {delivery.id} for package {package_id}")
            return delivery
        except Exception as e:
            logger.error(f"Error creating delivery: {e}")
            self.db.rollback()
            return None

    def assign_courier(self, delivery_id: int, courier_id: int, assigner: User) -> Optional[Delivery]:
        delivery = self.db.query(Delivery).filter(Delivery.id == delivery_id).first()
        courier = self.db.query(User).filter(User.id == courier_id).first()
        if not delivery or not courier:
            return None

        if assigner.role not in [UserRole.ADMIN, UserRole.COURIER]:
            return None

        if courier.role != UserRole.COURIER:
            return None

        delivery.courier_id = courier_id
        delivery.status = DeliveryStatus.ASSIGNED
        delivery.updated_at = datetime.utcnow()
        try:
            self.db.commit()
            self.db.refresh(delivery)
            return delivery
        except Exception:
            self.db.rollback()
            return None

    def update_status(self, delivery_id: int, status: DeliveryStatus) -> Optional[Delivery]:
        delivery = self.db.query(Delivery).filter(Delivery.id == delivery_id).first()
        if not delivery:
            return None

        delivery.status = status
        delivery.updated_at = datetime.utcnow()
        try:
            self.db.commit()
            self.db.refresh(delivery)
            return delivery
        except Exception:
            self.db.rollback()
            return None

    def update_location(self, delivery_id: int, lat: float, lng: float) -> Optional[Delivery]:
        delivery = self.db.query(Delivery).filter(Delivery.id == delivery_id).first()
        if not delivery:
            return None

        delivery.current_lat = lat
        delivery.current_lng = lng
        delivery.last_update = datetime.utcnow()
        try:
            self.db.commit()
            self.db.refresh(delivery)

            # Emit realtime location update to subscribed websocket clients
            try:
                loop = getattr(connection_manager, 'loop', None)
                if loop:
                    try:
                        asyncio.run_coroutine_threadsafe(
                            connection_manager.notify_delivery_location(delivery.id, lat, lng),
                            loop,
                        )
                    except Exception:
                        logging.getLogger(__name__).debug("Could not schedule delivery location notify on server loop")
                else:
                    # Fallback: attempt to schedule on the current event loop or run synchronously
                    try:
                        cur_loop = asyncio.get_event_loop()
                        if cur_loop.is_running():
                            cur_loop.create_task(connection_manager.notify_delivery_location(delivery.id, lat, lng))
                        else:
                            asyncio.run(connection_manager.notify_delivery_location(delivery.id, lat, lng))
                    except Exception:
                        logging.getLogger(__name__).debug("Could not schedule delivery location notify task")
            except Exception:
                logging.getLogger(__name__).debug("Error while attempting to notify websocket clients")

            return delivery
        except Exception:
            self.db.rollback()
            return None

    def get_delivery(self, delivery_id: int) -> Optional[Delivery]:
        return self.db.query(Delivery).filter(Delivery.id == delivery_id).first()

    def list_deliveries(self, skip: int = 0, limit: int = 50) -> List[Delivery]:
        return self.db.query(Delivery).order_by(Delivery.created_at.desc()).offset(skip).limit(limit).all()
