from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    UnprocessableEntityException,
)
from app.core.security import hash_password, validate_password_strength, verify_password
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.auditing import AuditService


class AuthenticationService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedException("Invalid email or password.")
        if not user.is_active:
            raise ForbiddenException("User account is disabled. Contact system administrator.")
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")
        return user

    def create_user(self, user_in: UserCreate, actor: Optional[User] = None) -> User:
        # Check duplicate email
        existing = self.user_repo.get_by_email(user_in.email)
        if existing:
            raise ConflictException(f"User with email '{user_in.email}' already exists.")

        # Validate password strength
        password_err = validate_password_strength(user_in.password)
        if password_err:
            raise UnprocessableEntityException(password_err)

        # Hash password and create user
        hashed = hash_password(user_in.password)
        new_user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hashed,
            role=user_in.role,
            is_active=True,
        )
        created_user = self.user_repo.create(new_user)

        # Log audit event
        actor_id = actor.id if actor else None
        AuditService.log_event(
            db=self.db,
            actor_user_id=actor_id,
            action="USER_CREATED",
            entity_type="User",
            entity_id=created_user.id,
            description=f"Created user '{created_user.email}' with role '{created_user.role.value}'",
        )
        return created_user

    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found.")
        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.user_repo.get_all(skip=skip, limit=limit)

    def update_user(self, user_id: int, user_in: UserUpdate, actor: User) -> User:
        user = self.get_user_by_id(user_id)

        changes = []
        if user_in.full_name is not None and user_in.full_name != user.full_name:
            changes.append(f"full_name: '{user.full_name}' -> '{user_in.full_name}'")
            user.full_name = user_in.full_name

        if user_in.email is not None and user_in.email != user.email:
            existing = self.user_repo.get_by_email(user_in.email)
            if existing and existing.id != user.id:
                raise ConflictException(f"Email '{user_in.email}' is already in use.")
            changes.append(f"email: '{user.email}' -> '{user_in.email}'")
            user.email = user_in.email

        if user_in.role is not None and user_in.role != user.role:
            changes.append(f"role: '{user.role.value}' -> '{user_in.role.value}'")
            user.role = user_in.role

        if user_in.is_active is not None and user_in.is_active != user.is_active:
            changes.append(f"is_active: {user.is_active} -> {user_in.is_active}")
            user.is_active = user_in.is_active

        updated_user = self.user_repo.update(user)

        if changes:
            AuditService.log_event(
                db=self.db,
                actor_user_id=actor.id,
                action="USER_UPDATED",
                entity_type="User",
                entity_id=updated_user.id,
                description=f"Updated user {updated_user.email}: " + ", ".join(changes),
            )
        return updated_user
