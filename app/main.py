from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import __version__
from app.api.v1.router import api_router
from app.api.v1.routes.health import router as health_router
from app.core.config import settings
from app.core.exceptions import BaseAppException, app_exception_handler


def create_application() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        description=(
            "RESTful API for Regent College London Human Resource Management System. "
            "Supports Employee Lifecycle, Background Check Mock Integrations, HR Analytics, and Immutable Audit Trails."
        ),
        version="1.0.0",
    )

    # CORS Middleware Setup
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Register Exception Handlers
    app.add_exception_handler(BaseAppException, app_exception_handler)

    # Root Endpoint
    @app.get("/", tags=["Root"])
    def root() -> Dict[str, Any]:
        """Root landing endpoint providing quick links to interactive documentation and health diagnostics."""
        return {
            "message": "Welcome to Regent College London HR Management RESTful API",
            "version": __version__,
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "health_check": "/health",
            "api_v1_prefix": settings.API_V1_STR,
        }

    # Mount API v1 router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Mount root system endpoints (/health, /health/database, /version)
    app.include_router(health_router)

    return app


app = create_application()
