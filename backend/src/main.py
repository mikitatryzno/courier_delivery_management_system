from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.database import engine, Base
from src.core.openapi import custom_openapi
from src.api.routes import (
    auth_router,
    packages_router,
    users_router,
    deliveries_router,
    notifications_router,
)
from src.api.routes.websocket import router as websocket_router
from src.routes.health import router as health_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    description="Courier Delivery Management System API",
    version="1.0.0",
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    docs_url=f"{settings.api_v1_str}/docs",
    redoc_url=f"{settings.api_v1_str}/redoc"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.api_v1_str)
app.include_router(packages_router, prefix=settings.api_v1_str)
app.include_router(users_router, prefix=settings.api_v1_str)
app.include_router(deliveries_router, prefix=settings.api_v1_str)
app.include_router(notifications_router, prefix=settings.api_v1_str)
app.include_router(websocket_router, prefix=settings.api_v1_str)
app.include_router(health_router, prefix=settings.api_v1_str)

# Customize OpenAPI schema
app.openapi = lambda: custom_openapi(app)

@app.get("/", tags=["root"])
def read_root():
    """
    Root endpoint providing basic API information.
    
    Returns welcome message and links to documentation.
    """
    return {
        "message": "Courier Delivery Management System API",
        "version": "1.0.0",
        "docs": f"{settings.api_v1_str}/docs",
        "redoc": f"{settings.api_v1_str}/redoc",
        "openapi": f"{settings.api_v1_str}/openapi.json"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)