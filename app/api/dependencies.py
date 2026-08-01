from typing import List

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.users import UserRepository

security_bearer = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Decodes JWT access token and retrieves current authenticated user."""
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Token payload missing subject.")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user ID in token payload.")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException("Authenticated user no longer exists.")

    if not user.is_active:
        raise ForbiddenException("User account is disabled.")

    return user


class RoleChecker:
    """Dependency for enforcing Role-Based Access Control (RBAC)."""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise ForbiddenException(
                f"Role '{current_user.role.value}' is not authorized to perform this operation."
            )
        return current_user


def require_role(*roles: UserRole) -> RoleChecker:
    """Helper returning a RoleChecker instance to be used with Depends()."""
    return RoleChecker(list(roles))
