from typing import Any, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate
from app.services.departments import DepartmentService

router = APIRouter(prefix="/departments", tags=["Department Management"])


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    dept_in: DepartmentCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Any:
    """Creates a new organizational department (ADMIN only)."""
    dept_service = DepartmentService(db)
    return dept_service.create_department(dept_in, actor=current_admin)


@router.get(
    "",
    response_model=List[DepartmentResponse],
    status_code=status.HTTP_200_OK,
)
def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Lists departments (ADMIN, HR_OFFICER, VIEWER)."""
    dept_service = DepartmentService(db)
    return dept_service.list_departments(skip=skip, limit=limit)


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieves department details by ID (ADMIN, HR_OFFICER, VIEWER)."""
    dept_service = DepartmentService(db)
    return dept_service.get_department_by_id(department_id)


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
def update_department(
    department_id: int,
    dept_in: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Any:
    """Updates department details (ADMIN only)."""
    dept_service = DepartmentService(db)
    return dept_service.update_department(department_id, dept_in, actor=current_admin)


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
) -> None:
    """Deletes a department (ADMIN only, blocked if active employees exist)."""
    dept_service = DepartmentService(db)
    dept_service.delete_department(department_id, actor=current_admin)
