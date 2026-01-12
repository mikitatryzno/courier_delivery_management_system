from .auth import router as auth_router
from .packages import router as packages_router
from .users import router as users_router
from .deliveries import router as deliveries_router
from .notifications import router as notifications_router

__all__ = [
	"auth_router",
	"packages_router",
	"users_router",
	"deliveries_router",
	"notifications_router",
]