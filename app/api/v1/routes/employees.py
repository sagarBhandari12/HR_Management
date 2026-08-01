from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.employee import EmployeeStatus
from app.models.user import User, UserRole
from app.schemas.common import PaginatedResponse
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employees import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employee Management"])


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    emp_in: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Creates a new employee record (ADMIN and HR_OFFICER)."""
    emp_service = EmployeeService(db)
    return emp_service.create_employee(emp_in, actor=current_user)


@router.get(
    "",
    response_model=PaginatedResponse[EmployeeResponse],
    status_code=status.HTTP_200_OK,
)
def list_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, email or employee number"),
    employee_number: Optional[str] = Query(None, description="Filter by exact employee number"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    status: Optional[EmployeeStatus] = Query(None, description="Filter by employment status"),
    is_active: Optional[bool] = Query(None, description="Filter active or deactivated employees"),
    sort_by: str = Query("id", description="Allowlisted sort field (id, employee_number, first_name, last_name, work_email, created_at, status)"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort direction (asc or desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Paginated list of employees with search, multi-field filtering, and safe allowlisted sorting."""
    emp_service = EmployeeService(db)
    items, total = emp_service.search_employees(
        page=page,
        page_size=page_size,
        search_query=search,
        employee_number=employee_number,
        department_id=department_id,
        status=status,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse[EmployeeResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieves an employee record by ID (ADMIN, HR_OFFICER, VIEWER)."""
    emp_service = EmployeeService(db)
    return emp_service.get_employee_by_id(employee_id)


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def update_employee(
    employee_id: int,
    emp_in: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.HR_OFFICER)),
) -> Any:
    """Updates an employee record (ADMIN and HR_OFFICER)."""
    emp_service = EmployeeService(db)
    return emp_service.update_employee(employee_id, emp_in, actor=current_user)


@router.delete(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def deactivate_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Any:
    """Deactivates an employee record (Soft Delete) to preserve auditability (ADMIN only)."""
    emp_service = EmployeeService(db)
    return emp_service.deactivate_employee(employee_id, actor=current_admin)


@router.post(
    "/{employee_id}/reactivate",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def reactivate_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Any:
    """Reactivates a deactivated employee record (ADMIN only). Returns 409 Conflict if already active."""
    emp_service = EmployeeService(db)
    return emp_service.reactivate_employee(employee_id, actor=current_admin)
