from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserResponse
from app.services.authentication import AuthenticationService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(login_req: LoginRequest, db: Session = Depends(get_db)) -> Any:
    """Authenticates user with email and password and returns a JWT bearer token."""
    auth_service = AuthenticationService(db)
    user = auth_service.authenticate_user(login_req.email, login_req.password)

    access_token = create_access_token(subject=str(user.id), role=user.role.value)

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role.value,
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user_profile(current_user: User = Depends(get_current_user)) -> Any:
    """Retrieves the profile of the currently authenticated user."""
    return current_user
