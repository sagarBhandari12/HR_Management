from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session, joinedload

from app.models.employee import Employee, EmployeeStatus


class EmployeeRepository:
    # Allowlisted sorting fields to prevent SQL injection or un-indexed sorting attacks
    ALLOWLISTED_SORT_FIELDS = {
        "id": Employee.id,
        "employee_number": Employee.employee_number,
        "first_name": Employee.first_name,
        "last_name": Employee.last_name,
        "work_email": Employee.work_email,
        "created_at": Employee.created_at,
        "status": Employee.status,
    }

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        return (
            self.db.query(Employee)
            .options(joinedload(Employee.department))
            .filter(Employee.id == employee_id)
            .first()
        )

    def get_by_employee_number(self, employee_number: str) -> Optional[Employee]:
        return (
            self.db.query(Employee)
            .filter(Employee.employee_number == employee_number.strip())
            .first()
        )

    def get_by_work_email(self, work_email: str) -> Optional[Employee]:
        return (
            self.db.query(Employee)
            .filter(Employee.work_email.ilike(work_email.strip()))
            .first()
        )

    def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return self.get_by_id(employee.id)

    def update(self, employee: Employee) -> Employee:
        self.db.commit()
        self.db.refresh(employee)
        return self.get_by_id(employee.id)

    def search_and_filter(
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
    ) -> Tuple[List[Employee], int]:
        """
        Paginated employee retrieval with search, filtering, and allowlisted sorting.
        Returns (list_of_employees, total_count).
        """
        query = self.db.query(Employee).options(joinedload(Employee.department))

        # Filtering
        if search_query:
            term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    Employee.first_name.ilike(term),
                    Employee.last_name.ilike(term),
                    Employee.work_email.ilike(term),
                    Employee.employee_number.ilike(term),
                )
            )

        if employee_number:
            query = query.filter(Employee.employee_number == employee_number.strip())

        if department_id:
            query = query.filter(Employee.department_id == department_id)

        if status:
            query = query.filter(Employee.status == status)

        if is_active is not None:
            query = query.filter(Employee.is_active == is_active)

        total_count = query.count()

        # Safe Allowlisted Sorting
        sort_column = self.ALLOWLISTED_SORT_FIELDS.get(sort_by, Employee.id)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Pagination
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return items, total_count
