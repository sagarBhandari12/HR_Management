from typing import Any, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.employment_record import EmploymentRecordCreate, EmploymentRecordResponse, EmploymentRecordUpdate
from app.services.employment_records import EmploymentRecordService

router = APIRouter(tags=["Employment Records"])


@router.post(
    "/employees/{employee_id}/employment-records",
    response_model=EmploymentRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employment_record(
    employee_id: int,
    record_in: EmploymentRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Adds a new employment record for a specific employee (ADMIN and HR_OFFICER)."""
    record_service = EmploymentRecordService(db)
    return record_service.create_record(employee_id, record_in, actor=current_user)


@router.get(
    "/employees/{employee_id}/employment-records",
    response_model=List[EmploymentRecordResponse],
    status_code=status.HTTP_200_OK,
)
def list_employee_employment_records(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Lists all employment records for a specific employee (ADMIN, HR_OFFICER, VIEWER)."""
    record_service = EmploymentRecordService(db)
    return record_service.list_records_for_employee(employee_id)


@router.get(
    "/employment-records/{record_id}",
    response_model=EmploymentRecordResponse,
    status_code=status.HTTP_200_OK,
)
def get_employment_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieves a specific employment record by ID (ADMIN, HR_OFFICER, VIEWER)."""
    record_service = EmploymentRecordService(db)
    return record_service.get_record_by_id(record_id)


@router.patch(
    "/employment-records/{record_id}",
    response_model=EmploymentRecordResponse,
    status_code=status.HTTP_200_OK,
)
def update_employment_record(
    record_id: int,
    record_in: EmploymentRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Updates an existing employment record (ADMIN and HR_OFFICER)."""
    record_service = EmploymentRecordService(db)
    return record_service.update_record(record_id, record_in, actor=current_user)
