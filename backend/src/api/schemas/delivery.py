from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.models.delivery import DeliveryStatus


class DeliveryCreate(BaseModel):
    package_id: int
    courier_id: Optional[int] = None


class DeliveryUpdateStatus(BaseModel):
    status: DeliveryStatus


class DeliveryLocationUpdate(BaseModel):
    lat: float
    lng: float


class DeliveryRead(BaseModel):
    id: int
    package_id: int
    courier_id: Optional[int]
    status: DeliveryStatus
    current_lat: Optional[float]
    current_lng: Optional[float]
    last_update: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
