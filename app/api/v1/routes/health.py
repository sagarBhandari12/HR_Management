from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import __version__
from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["Health & System"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, Any]:
    """System health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": __version__,
    }


@router.get("/health/database", status_code=status.HTTP_200_OK)
def database_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Database connectivity diagnostic endpoint."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "database_url_type": settings.DATABASE_URL.split(":")[0],
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }


@router.get("/version", status_code=status.HTTP_200_OK)
def version_check() -> Dict[str, Any]:
    """API version endpoint."""
    return {
        "app_name": settings.APP_NAME,
        "version": __version__,
        "api_v1_prefix": settings.API_V1_STR,
    }
