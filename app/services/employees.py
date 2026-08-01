from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.employee import Employee, EmployeeStatus
from app.models.user import User
from app.repositories.departments import DepartmentRepository
from app.repositories.employees import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.auditing import AuditService


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.emp_repo = EmployeeRepository(db)
        self.dept_repo = DepartmentRepository(db)

    def _to_response(self, emp: Employee) -> EmployeeResponse:
        dept_name = emp.department.name if emp.department else None
        return EmployeeResponse(
            id=emp.id,
            employee_number=emp.employee_number,
            first_name=emp.first_name,
            last_name=emp.last_name,
            work_email=emp.work_email,
            personal_email=emp.personal_email,
            telephone=emp.telephone,
            date_of_birth=emp.date_of_birth,
            department_id=emp.department_id,
            department_name=dept_name,
            status=emp.status,
            is_active=emp.is_active,
            created_at=emp.created_at,
            updated_at=emp.updated_at,
            deactivated_at=emp.deactivated_at,
        )

    def create_employee(self, emp_in: EmployeeCreate, actor: User) -> EmployeeResponse:
        # Check department exists
        dept = self.dept_repo.get_by_id(emp_in.department_id)
        if not dept:
            raise NotFoundException(f"Department with ID {emp_in.department_id} not found.")

        # Business Rule 2: Unique employee number
        if self.emp_repo.get_by_employee_number(emp_in.employee_number):
            raise ConflictException(f"Employee number '{emp_in.employee_number}' is already registered.")

        # Business Rule 3: Unique work email
        if self.emp_repo.get_by_work_email(emp_in.work_email):
            raise ConflictException(f"Work email '{emp_in.work_email}' is already registered.")

        employee = Employee(
            employee_number=emp_in.employee_number.strip(),
            first_name=emp_in.first_name.strip(),
            last_name=emp_in.last_name.strip(),
            work_email=emp_in.work_email.strip(),
            personal_email=emp_in.personal_email.strip() if emp_in.personal_email else None,
            telephone=emp_in.telephone.strip() if emp_in.telephone else None,
            date_of_birth=emp_in.date_of_birth,
            department_id=emp_in.department_id,
            status=emp_in.status,
            is_active=True,
        )

        created_emp = self.emp_repo.create(employee)

        AuditService.log_event(
            db=self.db,
            actor_user_id=actor.id,
            action="EMPLOYEE_CREATED",
            entity_type="Employee",
            entity_id=created_emp.id,
            description=f"Created employee '{created_emp.employee_number}' ({created_emp.first_name} {created_emp.last_name})",
        )

        return self._to_response(created_emp)

    def get_employee_by_id(self, employee_id: int) -> EmployeeResponse:
        emp = self.emp_repo.get_by_id(employee_id)
        if not emp:
            raise NotFoundException(f"Employee with ID {employee_id} not found.")
        return self._to_response(emp)

    def search_employees(
        self,
        page: int = 1,
        page_size: int = 10,
        search_query: Optional[str] = None,
        employee_number: Optional[str] = None,
        department_id: Optional[int] = None,
        status: Optional[EmployeeStatus] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> Tuple[List[EmployeeResponse], int]:
        items, total = self.emp_repo.search_and_filter(
            page=page,
            page_size=page_size,
            search_query=search_query,
            employee_number=employee_number,
            department_id=department_id,
            status=status,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [self._to_response(emp) for emp in items], total

    def update_employee(self, employee_id: int, emp_in: EmployeeUpdate, actor: User) -> EmployeeResponse:
        emp = self.emp_repo.get_by_id(employee_id)
        if not emp:
            raise NotFoundException(f"Employee with ID {employee_id} not found.")

        changes = []
        if emp_in.first_name:
            emp.first_name = emp_in.first_name.strip()
            changes.append("first_name")
        if emp_in.last_name:
            emp.last_name = emp_in.last_name.strip()
            changes.append("last_name")
        if emp_in.work_email and emp_in.work_email != emp.work_email:
            existing = self.emp_repo.get_by_work_email(emp_in.work_email)
            if existing and existing.id != emp.id:
                raise ConflictException(f"Work email '{emp_in.work_email}' is already in use.")
            emp.work_email = emp_in.work_email.strip()
            changes.append("work_email")
        if emp_in.personal_email is not None:
            emp.personal_email = emp_in.personal_email.strip() if emp_in.personal_email else None
            changes.append("personal_email")
        if emp_in.telephone is not None:
            emp.telephone = emp_in.telephone.strip() if emp_in.telephone else None
            changes.append("telephone")
        if emp_in.date_of_birth is not None:
            emp.date_of_birth = emp_in.date_of_birth
            changes.append("date_of_birth")
        if emp_in.department_id and emp_in.department_id != emp.department_id:
            dept = self.dept_repo.get_by_id(emp_in.department_id)
            if not dept:
                raise NotFoundException(f"Department with ID {emp_in.department_id} not found.")
            emp.department_id = emp_in.department_id
            changes.append("department_id")
        if emp_in.status and emp_in.status != emp.status:
            emp.status = emp_in.status
            changes.append(f"status: {emp_in.status.value}")

        updated_emp = self.emp_repo.update(emp)

        if changes:
            AuditService.log_event(
                db=self.db,
                actor_user_id=actor.id,
                action="EMPLOYEE_UPDATED",
                entity_type="Employee",
                entity_id=updated_emp.id,
                description=f"Updated employee '{updated_emp.employee_number}': " + ", ".join(changes),
            )

        return self._to_response(updated_emp)

    def deactivate_employee(self, employee_id: int, actor: User) -> EmployeeResponse:
        """
        Business Rule 9: Employee deletion must deactivate (soft-delete) rather than permanently remove.
        """
        emp = self.emp_repo.get_by_id(employee_id)
        if not emp:
            raise NotFoundException(f"Employee with ID {employee_id} not found.")

        if not emp.is_active:
            raise ConflictException(f"Employee '{emp.employee_number}' is already deactivated.")

        emp.is_active = False
        emp.status = EmployeeStatus.TERMINATED
        emp.deactivated_at = datetime.now(timezone.utc)

        deactivated_emp = self.emp_repo.update(emp)

        AuditService.log_event(
            db=self.db,
            actor_user_id=actor.id,
            action="EMPLOYEE_DEACTIVATED",
            entity_type="Employee",
            entity_id=deactivated_emp.id,
            description=f"Deactivated employee '{deactivated_emp.employee_number}'",
        )

        return self._to_response(deactivated_emp)

    def reactivate_employee(self, employee_id: int, actor: User) -> EmployeeResponse:
        """
        Reactivates a soft-deactivated employee.
        Business Rule 10: Reactivating an already active employee returns a controlled conflict (409).
        """
        emp = self.emp_repo.get_by_id(employee_id)
        if not emp:
            raise NotFoundException(f"Employee with ID {employee_id} not found.")

        if emp.is_active:
            raise ConflictException(f"Employee '{emp.employee_number}' is already active.")

        emp.is_active = True
        emp.status = EmployeeStatus.ACTIVE
        emp.deactivated_at = None

        reactivated_emp = self.emp_repo.update(emp)

        AuditService.log_event(
            db=self.db,
            actor_user_id=actor.id,
            action="EMPLOYEE_REACTIVATED",
            entity_type="Employee",
            entity_id=reactivated_emp.id,
            description=f"Reactivated employee '{reactivated_emp.employee_number}'",
        )

        return self._to_response(reactivated_emp)
