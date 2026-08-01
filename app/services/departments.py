from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.department import Department
from app.models.user import User
from app.repositories.departments import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate
from app.services.auditing import AuditService


class DepartmentService:
    def __init__(self, db: Session):
        self.db = db
        self.dept_repo = DepartmentRepository(db)

    def create_department(self, dept_in: DepartmentCreate, actor: User) -> DepartmentResponse:
        existing = self.dept_repo.get_by_name(dept_in.name)
        if existing:
            raise ConflictException(f"Department with name '{dept_in.name}' already exists.")

        department = Department(
            name=dept_in.name.strip(),
            description=dept_in.description,
            is_active=True,
        )
        created_dept = self.dept_repo.create(department)

        AuditService.log_event(
            db=self.db,
            actor_user_id=actor.id,
            action="DEPARTMENT_CREATED",
            entity_type="Department",
            entity_id=created_dept.id,
            description=f"Created department '{created_dept.name}'",
        )

        return DepartmentResponse(
            id=created_dept.id,
            name=created_dept.name,
            description=created_dept.description,
            is_active=created_dept.is_active,
            created_at=created_dept.created_at,
            updated_at=created_dept.updated_at,
            active_employee_count=0,
        )

    def get_department_by_id(self, department_id: int) -> DepartmentResponse:
        department = self.dept_repo.get_by_id(department_id)
        if not department:
            raise NotFoundException(f"Department with ID {department_id} not found.")

        count = self.dept_repo.count_active_employees(department_id)

        return DepartmentResponse(
            id=department.id,
            name=department.name,
            description=department.description,
            is_active=department.is_active,
            created_at=department.created_at,
            updated_at=department.updated_at,
            active_employee_count=count,
        )

    def list_departments(self, skip: int = 0, limit: int = 100) -> List[DepartmentResponse]:
        departments = self.dept_repo.get_all(skip=skip, limit=limit)
        results = []
        for d in departments:
            count = self.dept_repo.count_active_employees(d.id)
            results.append(
                DepartmentResponse(
                    id=d.id,
                    name=d.name,
                    description=d.description,
                    is_active=d.is_active,
                    created_at=d.created_at,
                    updated_at=d.updated_at,
                    active_employee_count=count,
                )
            )
        return results

    def update_department(
        self, department_id: int, dept_in: DepartmentUpdate, actor: User
    ) -> DepartmentResponse:
        department = self.dept_repo.get_by_id(department_id)
        if not department:
            raise NotFoundException(f"Department with ID {department_id} not found.")

        changes = []
        if dept_in.name is not None and dept_in.name.strip() != department.name:
            existing = self.dept_repo.get_by_name(dept_in.name)
            if existing and existing.id != department.id:
                raise ConflictException(f"Department name '{dept_in.name}' is already in use.")
            changes.append(f"name: '{department.name}' -> '{dept_in.name}'")
            department.name = dept_in.name.strip()

        if dept_in.description is not None:
            changes.append("updated description")
            department.description = dept_in.description

        if dept_in.is_active is not None and dept_in.is_active != department.is_active:
            changes.append(f"is_active: {department.is_active} -> {dept_in.is_active}")
            department.is_active = dept_in.is_active

        updated = self.dept_repo.update(department)

        if changes:
            AuditService.log_event(
                db=self.db,
                actor_user_id=actor.id,
                action="DEPARTMENT_UPDATED",
                entity_type="Department",
                entity_id=updated.id,
                description=f"Updated department '{updated.name}': " + ", ".join(changes),
            )

        count = self.dept_repo.count_active_employees(updated.id)
        return DepartmentResponse(
            id=updated.id,
            name=updated.name,
            description=updated.description,
            is_active=updated.is_active,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
            active_employee_count=count,
        )

    def delete_department(self, department_id: int, actor: User) -> None:
        department = self.dept_repo.get_by_id(department_id)
        if not department:
            raise NotFoundException(f"Department with ID {department_id} not found.")

        # Business Rule 8: A department with active employees cannot be deleted.
        active_emp_count = self.dept_repo.count_active_employees(department_id)
        if active_emp_count > 0:
            raise ConflictException(
                f"Cannot delete department '{department.name}' because it contains {active_emp_count} active employee(s)."
            )

        dept_name = department.name
        self.dept_repo.delete(department)

        AuditService.log_event(
            db=self.db,
            actor_user_id=actor.id,
            action="DEPARTMENT_DELETED",
            entity_type="Department",
            entity_id=department_id,
            description=f"Deleted department '{dept_name}'",
        )
