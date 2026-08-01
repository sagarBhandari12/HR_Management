from typing import Any, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.background_check import (
    BackgroundCheckCreate,
    BackgroundCheckExecutionRequest,
    BackgroundCheckResponse,
    BackgroundCheckUpdate,
)
from app.services.background_checks import BackgroundCheckService

router = APIRouter(tags=["Background Checks & Mock Integrations"])


@router.post(
    "/employees/{employee_id}/background-checks",
    response_model=BackgroundCheckResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_background_check(
    employee_id: int,
    check_in: BackgroundCheckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Initiates a background check for an employee (ADMIN and HR_OFFICER)."""
    check_service = BackgroundCheckService(db)
    return check_service.create_check(employee_id, check_in, actor=current_user)


@router.get(
    "/employees/{employee_id}/background-checks",
    response_model=List[BackgroundCheckResponse],
    status_code=status.HTTP_200_OK,
)
def list_employee_background_checks(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Lists all background checks for an employee (Restricted notes filtered for VIEWER role)."""
    check_service = BackgroundCheckService(db)
    return check_service.list_checks_for_employee(employee_id, user=current_user)


@router.get(
    "/background-checks/{check_id}",
    response_model=BackgroundCheckResponse,
    status_code=status.HTTP_200_OK,
)
def get_background_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieves specific background check details by ID (Restricted notes filtered for VIEWER role)."""
    check_service = BackgroundCheckService(db)
    return check_service.get_check_by_id(check_id, user=current_user)


@router.patch(
    "/background-checks/{check_id}",
    response_model=BackgroundCheckResponse,
    status_code=status.HTTP_200_OK,
)
def update_background_check(
    check_id: int,
    check_in: BackgroundCheckUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Manually updates background check status or notes (ADMIN and HR_OFFICER)."""
    check_service = BackgroundCheckService(db)
    return check_service.update_check(check_id, check_in, actor=current_user)


@router.post(
    "/background-checks/{check_id}/execute",
    response_model=BackgroundCheckResponse,
    status_code=status.HTTP_200_OK,
)
def execute_background_check(
    check_id: int,
    req_in: BackgroundCheckExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Triggers mock external provider execution (DBS, Home Office, Credit, Bank) for controlled scenarios."""
    check_service = BackgroundCheckService(db)
    return check_service.execute_check_simulation(check_id, req_in, actor=current_user)
