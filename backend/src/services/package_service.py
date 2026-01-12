"""Package service layer for business logic."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from src.models.package import Package, PackageStatus
from src.models.user import User, UserRole
from src.api.schemas.package import PackageCreate, PackageUpdate
from src.websocket.events import websocket_events
import logging

logger = logging.getLogger(__name__)

class PackageService:
    """Service class for package-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_package(
        self,
        package_data: PackageCreate,
        sender_user: User
    ) -> Optional[Package]:
        """Create a new package."""
        try:
            package = Package(
                title=package_data.title,
                description=package_data.description,
                sender_name=package_data.sender_name,
                sender_phone=package_data.sender_phone,
                sender_address=package_data.sender_address,
                recipient_name=package_data.recipient_name,
                recipient_phone=package_data.recipient_phone,
                recipient_address=package_data.recipient_address,
                sender_id=sender_user.id,
                status=PackageStatus.CREATED
            )
            
            self.db.add(package)
            self.db.commit()
            self.db.refresh(package)
            
            logger.info(f"Package created: {package.id} by user {sender_user.id}")
            return package
            
        except Exception as e:
            logger.error(f"Error creating package: {e}")
            self.db.rollback()
            return None
    
    def get_packages(
        self,
        user: User,
        skip: int = 0,
        limit: int = 10,
        status: Optional[PackageStatus] = None,
        search: Optional[str] = None
    ) -> List[Package]:
        """Get packages based on user role and filters."""
        try:
            query = self.db.query(Package)
            
            # Apply role-based filtering
            if user.role == UserRole.ADMIN:
                # Admin sees all packages
                pass
            elif user.role == UserRole.COURIER:
                # Courier sees assigned packages and unassigned packages
                query = query.filter(
                    or_(
                        Package.courier_id == user.id,
                        Package.courier_id.is_(None)
                    )
                )
            elif user.role == UserRole.SENDER:
                # Sender sees their own packages
                query = query.filter(Package.sender_id == user.id)
            elif user.role == UserRole.RECIPIENT:
                # Recipient sees packages addressed to them
                query = query.filter(
                    or_(
                        Package.recipient_name.ilike(f"%{user.name}%"),
                        Package.recipient_phone == user.phone
                    )
                )
            
            # Apply status filter
            if status:
                query = query.filter(Package.status == status)
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Package.title.ilike(search_term),
                        Package.description.ilike(search_term),
                        Package.sender_name.ilike(search_term),
                        Package.recipient_name.ilike(search_term)
                    )
                )
            
            # Apply pagination and ordering
            packages = (
                query.order_by(Package.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            logger.debug(f"Retrieved {len(packages)} packages for user {user.id}")
            return packages
            
        except Exception as e:
            logger.error(f"Error getting packages: {e}")
            return []
    
    def get_package_by_id(self, package_id: int, user: User) -> Optional[Package]:
        """Get package by ID with permission check."""
        try:
            package = self.db.query(Package).filter(Package.id == package_id).first()
            
            if not package:
                return None
            
            # Check permissions
            if not self._can_access_package(package, user):
                logger.warning(f"User {user.id} denied access to package {package_id}")
                return None
            
            return package
            
        except Exception as e:
            logger.error(f"Error getting package {package_id}: {e}")
            return None
    
    def update_package(
        self,
        package_id: int,
        package_update: PackageUpdate,
        user: User
    ) -> Optional[Package]:
        """Update package information."""
        try:
            package = self.db.query(Package).filter(Package.id == package_id).first()
            
            if not package:
                return None
            
            # Check permissions
            if not self._can_modify_package(package, user):
                logger.warning(f"User {user.id} denied modification access to package {package_id}")
                return None
            
            # Update fields
            update_data = package_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(package, field) and value is not None:
                    setattr(package, field, value)
            
            package.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(package)
            
            logger.info(f"Package {package_id} updated by user {user.id}")
            return package
            
        except Exception as e:
            logger.error(f"Error updating package {package_id}: {e}")
            self.db.rollback()
            return None
    
    async def update_package_status(
        self,
        package_id: int,
        new_status: PackageStatus,
        user: User
    ) -> Optional[Package]:
        """Update package status with notifications."""
        try:
            package = self.db.query(Package).filter(Package.id == package_id).first()
            
            if not package:
                return None
            
            # Check permissions for status update
            if not self._can_update_status(package, user, new_status):
                logger.warning(f"User {user.id} denied status update for package {package_id}")
                return None
            
            old_status = package.status.value
            package.status = new_status
            package.updated_at = datetime.utcnow()
            
            # Handle status-specific logic
            if new_status == PackageStatus.ASSIGNED and not package.courier_id:
                package.courier_id = user.id
            
            self.db.commit()
            self.db.refresh(package)
            
            # Send WebSocket notification
            await websocket_events.package_status_updated(package, old_status, new_status.value)
            
            logger.info(f"Package {package_id} status updated from {old_status} to {new_status.value}")
            return package
            
        except Exception as e:
            logger.error(f"Error updating package {package_id} status: {e}")
            self.db.rollback()
            return None
    
    def assign_package_to_courier(
        self,
        package_id: int,
        courier_id: int,
        assigner: User
    ) -> Optional[Package]:
        """Assign package to a courier."""
        try:
            package = self.db.query(Package).filter(Package.id == package_id).first()
            courier = self.db.query(User).filter(User.id == courier_id).first()
            
            if not package or not courier:
                return None
            
            # Check permissions
            if assigner.role not in [UserRole.ADMIN, UserRole.COURIER]:
                return None
            
            # Check if courier role is valid
            if courier.role != UserRole.COURIER:
                return None
            
            package.courier_id = courier_id
            package.status = PackageStatus.ASSIGNED
            package.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(package)
            
            logger.info(f"Package {package_id} assigned to courier {courier_id}")
            return package
            
        except Exception as e:
            logger.error(f"Error assigning package {package_id}: {e}")
            self.db.rollback()
            return None
    
    def get_package_statistics(self, user: User) -> Dict[str, Any]:
        """Get package statistics based on user role."""
        try:
            base_query = self.db.query(Package)
            
            # Apply role-based filtering
            if user.role == UserRole.SENDER:
                base_query = base_query.filter(Package.sender_id == user.id)
            elif user.role == UserRole.COURIER:
                base_query = base_query.filter(Package.courier_id == user.id)
            elif user.role == UserRole.RECIPIENT:
                base_query = base_query.filter(
                    or_(
                        Package.recipient_name.ilike(f"%{user.name}%"),
                        Package.recipient_phone == user.phone
                    )
                )
            
            # Count by status
            status_counts = {}
            for status in PackageStatus:
                count = base_query.filter(Package.status == status).count()
                status_counts[status.value] = count
            
            # Total packages
            total_packages = base_query.count()
            
            # Recent packages (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_packages = base_query.filter(
                Package.created_at >= seven_days_ago
            ).count()
            
            stats = {
                "total_packages": total_packages,
                "packages_by_status": status_counts,
                "recent_packages": recent_packages,
                "user_role": user.role.value
            }
            
            # Add role-specific stats
            if user.role == UserRole.ADMIN:
                stats["total_couriers"] = self.db.query(User).filter(
                    User.role == UserRole.COURIER
                ).count()
                stats["unassigned_packages"] = base_query.filter(
                    Package.courier_id.is_(None)
                ).count()
            
            logger.debug(f"Generated package statistics for user {user.id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting package statistics: {e}")
            return {
                "total_packages": 0,
                "packages_by_status": {},
                "recent_packages": 0,
                "user_role": user.role.value
            }
    
    def get_available_packages_for_courier(self, courier: User) -> List[Package]:
        """Get packages available for courier assignment."""
        try:
            if courier.role != UserRole.COURIER:
                return []
            
            packages = (
                self.db.query(Package)
                .filter(
                    and_(
                        Package.courier_id.is_(None),
                        Package.status == PackageStatus.CREATED
                    )
                )
                .order_by(Package.created_at.asc())
                .all()
            )
            
            logger.debug(f"Found {len(packages)} available packages for courier {courier.id}")
            return packages
            
        except Exception as e:
            logger.error(f"Error getting available packages: {e}")
            return []
    
    def get_courier_packages(self, courier: User) -> List[Package]:
        """Get packages assigned to a courier."""
        try:
            if courier.role != UserRole.COURIER:
                return []
            
            packages = (
                self.db.query(Package)
                .filter(Package.courier_id == courier.id)
                .order_by(Package.updated_at.desc())
                .all()
            )
            
            logger.debug(f"Found {len(packages)} packages for courier {courier.id}")
            return packages
            
        except Exception as e:
            logger.error(f"Error getting courier packages: {e}")
            return []
    
    def search_packages(
        self,
        search_term: str,
        user: User,
        limit: int = 10
    ) -> List[Package]:
        """Search packages by various criteria."""
        try:
            search_pattern = f"%{search_term}%"
            query = self.db.query(Package)
            
            # Apply role-based filtering
            if user.role == UserRole.SENDER:
                query = query.filter(Package.sender_id == user.id)
            elif user.role == UserRole.COURIER:
                query = query.filter(Package.courier_id == user.id)
            elif user.role == UserRole.RECIPIENT:
                query = query.filter(
                    or_(
                        Package.recipient_name.ilike(f"%{user.name}%"),
                        Package.recipient_phone == user.phone
                    )
                )
            
            # Apply search criteria
            packages = (
                query.filter(
                    or_(
                        Package.title.ilike(search_pattern),
                        Package.description.ilike(search_pattern),
                        Package.sender_name.ilike(search_pattern),
                        Package.recipient_name.ilike(search_pattern),
                        Package.id == int(search_term) if search_term.isdigit() else False
                    )
                )
                .limit(limit)
                .all()
            )
            
            logger.debug(f"Found {len(packages)} packages matching '{search_term}'")
            return packages
            
        except Exception as e:
            logger.error(f"Error searching packages: {e}")
            return []
    
    def delete_package(self, package_id: int, user: User) -> bool:
        """Delete a package (Admin or sender only)."""
        try:
            package = self.db.query(Package).filter(Package.id == package_id).first()
            
            if not package:
                return False
            
            # Check permissions
            if user.role != UserRole.ADMIN and package.sender_id != user.id:
                return False
            
            # Don't allow deletion of packages in progress
            if package.status in [PackageStatus.PICKED_UP, PackageStatus.IN_TRANSIT]:
                return False
            
            self.db.delete(package)
            self.db.commit()
            
            logger.info(f"Package {package_id} deleted by user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting package {package_id}: {e}")
            self.db.rollback()
            return False
    
    def _can_access_package(self, package: Package, user: User) -> bool:
        """Check if user can access package."""
        if user.role == UserRole.ADMIN:
            return True
        elif user.role == UserRole.SENDER:
            return package.sender_id == user.id
        elif user.role == UserRole.COURIER:
            return package.courier_id == user.id or package.courier_id is None
        elif user.role == UserRole.RECIPIENT:
            return (
                user.name.lower() in package.recipient_name.lower() or
                user.phone == package.recipient_phone
            )
        return False
    
    def _can_modify_package(self, package: Package, user: User) -> bool:
        """Check if user can modify package."""
        if user.role == UserRole.ADMIN:
            return True
        elif user.role == UserRole.SENDER:
            return package.sender_id == user.id and package.status == PackageStatus.CREATED
        return False
    
    def _can_update_status(self, package: Package, user: User, new_status: PackageStatus) -> bool:
        """Check if user can update package status."""
        if user.role == UserRole.ADMIN:
            return True
        elif user.role == UserRole.COURIER:
            # Courier can update status of assigned packages
            return package.courier_id == user.id or (
                package.courier_id is None and new_status == PackageStatus.ASSIGNED
            )
        return False