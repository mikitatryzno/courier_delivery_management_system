"""Package-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.models.package import PackageStatus

class PackageBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    sender_name: str = Field(..., min_length=1, max_length=100)
    sender_phone: str = Field(..., min_length=1, max_length=20)
    sender_address: str = Field(..., min_length=1, max_length=500)
    recipient_name: str = Field(..., min_length=1, max_length=100)
    recipient_phone: str = Field(..., min_length=1, max_length=20)
    recipient_address: str = Field(..., min_length=1, max_length=500)

class PackageCreate(PackageBase):
    """Schema for creating a new package."""
    pass

class PackageUpdate(BaseModel):
    """Schema for updating package information."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    sender_name: Optional[str] = Field(None, min_length=1, max_length=100)
    sender_phone: Optional[str] = Field(None, min_length=1, max_length=20)
    sender_address: Optional[str] = Field(None, min_length=1, max_length=500)
    recipient_name: Optional[str] = Field(None, min_length=1, max_length=100)
    recipient_phone: Optional[str] = Field(None, min_length=1, max_length=20)
    recipient_address: Optional[str] = Field(None, min_length=1, max_length=500)

class PackageStatusUpdate(BaseModel):
    """Schema for updating package status."""
    status: PackageStatus = Field(..., description="New package status")

class PackageAssignment(BaseModel):
    """Schema for assigning package to courier."""
    courier_id: int = Field(..., gt=0, description="ID of the courier to assign")

class PackageResponse(PackageBase):
    """Schema for package response."""
    id: int
    status: PackageStatus
    sender_id: Optional[int] = None
    courier_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PackageListResponse(BaseModel):
    """Schema for paginated package list response."""
    packages: List[PackageResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

class PackageStatsResponse(BaseModel):
    """Schema for package statistics response."""
    total_packages: int
    packages_by_status: Dict[str, int]
    recent_packages: int
    user_role: str
    total_couriers: Optional[int] = None
    unassigned_packages: Optional[int] = None

class PackageSearchResponse(BaseModel):
    """Schema for package search response."""
    packages: List[PackageResponse]
    search_term: str
    total_found: int

class PackageHistoryEntry(BaseModel):
    """Schema for package history/audit entry."""
    id: int
    package_id: int
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    user_id: int
    user_name: str
    timestamp: datetime

class PackageHistoryResponse(BaseModel):
    """Schema for package history response."""
    package_id: int
    history: List[PackageHistoryEntry]

# WebSocket message schemas
class PackageNotification(BaseModel):
    """Schema for package-related WebSocket notifications."""
    type: str
    package_id: int
    package: PackageResponse
    message: str
    timestamp: datetime

class PackageStatusNotification(PackageNotification):
    """Schema for package status update notifications."""
    old_status: str
    new_status: str

class PackageAssignmentNotification(PackageNotification):
    """Schema for package assignment notifications."""
    courier_id: int
    courier_name: str