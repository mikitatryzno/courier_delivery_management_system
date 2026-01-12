from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.api.schemas.delivery import (
    DeliveryCreate,
    DeliveryRead,
    DeliveryUpdateStatus,
    DeliveryLocationUpdate,
)
from src.services.delivery_service import DeliveryService
from src.api.middleware.auth import get_current_user, require_roles
from src.models.user import User, UserRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.post("/", response_model=DeliveryRead, status_code=status.HTTP_201_CREATED)
def create_delivery(
    payload: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeliveryService(db)
    delivery = service.create_delivery(payload.package_id)
    if not delivery:
        raise HTTPException(status_code=400, detail="Failed to create delivery")
    return DeliveryRead.model_validate(delivery, from_attributes=True)


@router.get("/", response_model=List[DeliveryRead])
def list_deliveries(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    service = DeliveryService(db)
    deliveries = service.list_deliveries(skip=skip, limit=limit)
    return [DeliveryRead.model_validate(d) for d in deliveries]


@router.get("/{delivery_id}", response_model=DeliveryRead)
def get_delivery(delivery_id: int, db: Session = Depends(get_db)):
    service = DeliveryService(db)
    delivery = service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return DeliveryRead.model_validate(delivery, from_attributes=True)


@router.put("/{delivery_id}/assign", response_model=DeliveryRead)
def assign_courier(
    delivery_id: int,
    courier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.COURIER])),
):
    service = DeliveryService(db)
    delivery = service.assign_courier(delivery_id, courier_id, current_user)
    if not delivery:
        raise HTTPException(status_code=400, detail="Failed to assign courier")
    return DeliveryRead.model_validate(delivery, from_attributes=True)


@router.put("/{delivery_id}/status", response_model=DeliveryRead)
def update_status(
    delivery_id: int,
    status_update: DeliveryUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeliveryService(db)
    delivery = service.update_status(delivery_id, status_update.status)
    if not delivery:
        raise HTTPException(status_code=400, detail="Failed to update status")
    return DeliveryRead.model_validate(delivery, from_attributes=True)


@router.put("/{delivery_id}/location", response_model=DeliveryRead)
def update_location(
    delivery_id: int,
    loc: DeliveryLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DeliveryService(db)
    delivery = service.update_location(delivery_id, loc.lat, loc.lng)
    if not delivery:
        raise HTTPException(status_code=400, detail="Failed to update location")
    return DeliveryRead.model_validate(delivery, from_attributes=True)
