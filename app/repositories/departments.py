from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.employee import Employee


class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, department_id: int) -> Optional[Department]:
        return self.db.query(Department).filter(Department.id == department_id).first()

    def get_by_name(self, name: str) -> Optional[Department]:
        return self.db.query(Department).filter(Department.name.ilike(name.strip())).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Department]:
        return self.db.query(Department).offset(skip).limit(limit).all()

    def create(self, department: Department) -> Department:
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        return department

    def update(self, department: Department) -> Department:
        self.db.commit()
        self.db.refresh(department)
        return department

    def delete(self, department: Department) -> None:
        self.db.delete(department)
        self.db.commit()

    def count_active_employees(self, department_id: int) -> int:
        return (
            self.db.query(Employee)
            .filter(
                Employee.department_id == department_id,
                Employee.is_active,
            )
            .count()
        )
