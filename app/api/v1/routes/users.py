from typing import Any, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.authentication import AuthenticationService

router = APIRouter(prefix="/users", tags=["System Users Management"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Any:
    """Creates a new application user (ADMIN only)."""
    auth_service = AuthenticationService(db)
    return auth_service.create_user(user_in, actor=current_admin)


@router.get(
    "",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> Any:
    """Lists application users (ADMIN only)."""
    auth_service = AuthenticationService(db)
    return auth_service.list_users(skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)) -> Any:
    """Retrieves a specific application user by ID (ADMIN only)."""
    auth_service = AuthenticationService(db)
    return auth_service.get_user_by_id(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Any:
    """Updates an application user's details, role, or active status (ADMIN only)."""
    auth_service = AuthenticationService(db)
    return auth_service.update_user(user_id, user_in, actor=current_admin)
