"""Package management routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.package import Package, PackageStatus
from src.models.user import User, UserRole
from src.api.schemas.package import (
    PackageCreate,
    PackageResponse,
    PackageUpdate,
    PackageStatusUpdate,
    PackageAssignment,
    PackageListResponse,
    PackageStatsResponse
)
from src.api.middleware.auth import (
    get_current_user,
    require_roles,
    require_admin
)
from src.services.package_service import PackageService
from src.websocket.events import websocket_events
from src.api.schemas.openapi import OPENAPI_RESPONSES
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/packages", tags=["packages"])

@router.post(
    "/",
    response_model=PackageResponse,
    status_code=status.HTTP_200_OK,
    summary="Create Package",
    description="Create a new package for delivery",
    responses={
        201: {
            "description": "Package created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Important Documents",
                        "description": "Legal documents for delivery",
                        "status": "created",
                        "sender_name": "John Doe",
                        "recipient_name": "Jane Smith",
                        "created_at": "2024-01-01T10:00:00Z"
                    }
                }
            }
        },
        **OPENAPI_RESPONSES
    }
)
async def create_package(
    package_data: PackageCreate,
    current_user: User = Depends(require_roles([UserRole.SENDER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Create a new package for delivery.
    
    **Sender and Admin access**
    
    - **title**: Package title/name
    - **description**: Detailed description of package contents
    - **sender_name**: Name of the sender
    - **sender_phone**: Sender's phone number
    - **sender_address**: Pickup address
    - **recipient_name**: Name of the recipient
    - **recipient_phone**: Recipient's phone number
    - **recipient_address**: Delivery address
    """
    try:
        package_service = PackageService(db)
        package = package_service.create_package(package_data, current_user)
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create package"
            )
        
        # Send WebSocket notification
        await websocket_events.package_created(package)
        
        return PackageResponse.model_validate(package)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating package: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create package"
        )

@router.get(
    "/",
    response_model=List[PackageResponse],
    summary="List Packages",
    description="Get list of packages based on user role and filters"
)
def list_packages(
    skip: int = Query(0, ge=0, description="Number of packages to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of packages to return"),
    status: Optional[PackageStatus] = Query(None, description="Filter by package status"),
    search: Optional[str] = Query(None, description="Search packages by title, description, or names"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of packages with role-based filtering.
    
    **Role-based access:**
    - **Admin**: See all packages
    - **Courier**: See assigned packages and available packages
    - **Sender**: See own packages
    - **Recipient**: See packages addressed to them
    
    **Filters:**
    - **status**: Filter by package status
    - **search**: Search in title, description, sender/recipient names
    """
    try:
        package_service = PackageService(db)
        packages = package_service.get_packages(
            user=current_user,
            skip=skip,
            limit=limit,
            status=status,
            search=search
        )
        
        return [PackageResponse.model_validate(package) for package in packages]
        
    except Exception as e:
        logger.error(f"Error listing packages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve packages"
        )

@router.get(
    "/available",
    response_model=List[PackageResponse],
    summary="Get Available Packages",
    description="Get packages available for courier assignment"
)
def get_available_packages(
    current_user: User = Depends(require_roles([UserRole.COURIER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Get packages available for courier assignment.
    
    **Courier and Admin access**
    
    Returns packages that are created but not yet assigned to any courier.
    """
    try:
        package_service = PackageService(db)
        packages = package_service.get_available_packages_for_courier(current_user)
        
        return [PackageResponse.model_validate(package) for package in packages]
        
    except Exception as e:
        logger.error(f"Error getting available packages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available packages"
        )

@router.get(
    "/my-deliveries",
    response_model=List[PackageResponse],
    summary="Get My Deliveries",
    description="Get packages assigned to current courier"
)
def get_my_deliveries(
    current_user: User = Depends(require_roles([UserRole.COURIER])),
    db: Session = Depends(get_db)
):
    """
    Get packages assigned to the current courier.
    
    **Courier access only**
    
    Returns all packages currently assigned to the authenticated courier.
    """
    try:
        package_service = PackageService(db)
        packages = package_service.get_courier_packages(current_user)
        
        return [PackageResponse.model_validate(package) for package in packages]
        
    except Exception as e:
        logger.error(f"Error getting courier deliveries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve deliveries"
        )

@router.get(
    "/stats",
    response_model=PackageStatsResponse,
    summary="Get Package Statistics",
    description="Get package statistics based on user role"
)
def get_package_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get package statistics.
    
    Returns statistics relevant to the user's role:
    - **Admin**: System-wide statistics
    - **Courier**: Personal delivery statistics
    - **Sender**: Own package statistics
    - **Recipient**: Received package statistics
    """
    try:
        package_service = PackageService(db)
        stats = package_service.get_package_statistics(current_user)
        
        return PackageStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting package statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )

@router.get(
    "/{package_id}",
    response_model=PackageResponse,
    summary="Get Package Details",
    description="Get detailed information about a specific package"
)
def get_package(
    package_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific package.
    
    **Access control:**
    - **Admin**: Can view any package
    - **Sender**: Can view own packages
    - **Courier**: Can view assigned packages
    - **Recipient**: Can view packages addressed to them
    """
    try:
        package_service = PackageService(db)
        package = package_service.get_package_by_id(package_id, current_user)
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or access denied"
            )
        
        return PackageResponse.model_validate(package)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting package {package_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve package"
        )

@router.put(
    "/{package_id}",
    response_model=PackageResponse,
    summary="Update Package",
    description="Update package information"
)
def update_package(
    package_id: int,
    package_update: PackageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update package information.
    
    **Access control:**
    - **Admin**: Can update any package
    - **Sender**: Can update own packages (if not yet picked up)
    
    Note: Some fields may be restricted based on package status.
    """
    try:
        package_service = PackageService(db)
        package = package_service.update_package(package_id, package_update, current_user)
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or access denied"
            )
        
        return PackageResponse.model_validate(package)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating package {package_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update package"
        )

@router.put(
    "/{package_id}/status",
    response_model=PackageResponse,
    summary="Update Package Status",
    description="Update package delivery status"
)
async def update_package_status(
    package_id: int,
    status_update: PackageStatusUpdate,
    current_user: User = Depends(require_roles([UserRole.COURIER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Update package delivery status.
    
    **Courier and Admin access**
    
    **Status flow:**
    - created → assigned → picked_up → in_transit → delivered
    - Any status can go to → failed
    
    **Courier permissions:**
    - Can update status of assigned packages
    - Can assign themselves to unassigned packages
    """
    try:
        package_service = PackageService(db)
        package = await package_service.update_package_status(
            package_id, status_update.status, current_user
        )
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or access denied"
            )
        
        return PackageResponse.model_validate(package)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating package {package_id} status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update package status"
        )

@router.put(
    "/{package_id}/assign",
    response_model=PackageResponse,
    summary="Assign Package to Courier",
    description="Assign package to a specific courier"
)
def assign_package(
    package_id: int,
    assignment: PackageAssignment,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.COURIER])),
    db: Session = Depends(get_db)
):
    """
    Assign package to a courier.
    
    **Admin and Courier access**
    
    - **Admin**: Can assign any package to any courier
    - **Courier**: Can assign unassigned packages to themselves
    """
    try:
        package_service = PackageService(db)
        
        # If courier is assigning to themselves
        if current_user.role == UserRole.COURIER:
            assignment.courier_id = current_user.id
        
        package = package_service.assign_package_to_courier(
            package_id, assignment.courier_id, current_user
        )
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or assignment failed"
            )
        
        return PackageResponse.model_validate(package)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning package {package_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign package"
        )

@router.delete(
    "/{package_id}",
    summary="Delete Package",
    description="Delete a package (Admin or sender only)"
)
def delete_package(
    package_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a package.
    
    **Access control:**
    - **Admin**: Can delete any package
    - **Sender**: Can delete own packages (if not in progress)
    
    **Restrictions:**
    - Cannot delete packages that are picked up or in transit
    """
    try:
        package_service = PackageService(db)
        success = package_service.delete_package(package_id, current_user)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found, access denied, or cannot be deleted"
            )
        
        return {"message": "Package deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting package {package_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete package"
        )

@router.get(
    "/search/{search_term}",
    response_model=List[PackageResponse],
    summary="Search Packages",
    description="Search packages by various criteria"
)
def search_packages(
    search_term: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search packages by title, description, names, or ID.
    
    **Role-based filtering applied:**
    - Results are filtered based on user's access permissions
    
    **Search criteria:**
    - Package title
    - Package description
    - Sender name
    - Recipient name
    - Package ID (if numeric)
    """
    try:
        package_service = PackageService(db)
        packages = package_service.search_packages(search_term, current_user, limit)
        
        return [PackageResponse.model_validate(package) for package in packages]
        
    except Exception as e:
        logger.error(f"Error searching packages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search packages"
        )