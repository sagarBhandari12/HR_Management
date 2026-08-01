from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.employment_record import EmploymentRecord


class EmploymentRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, record_id: int) -> Optional[EmploymentRecord]:
        return self.db.query(EmploymentRecord).filter(EmploymentRecord.id == record_id).first()

    def get_by_employee_id(self, employee_id: int) -> List[EmploymentRecord]:
        return (
            self.db.query(EmploymentRecord)
            .filter(EmploymentRecord.employee_id == employee_id)
            .order_by(EmploymentRecord.start_date.desc())
            .all()
        )

    def create(self, record: EmploymentRecord) -> EmploymentRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: EmploymentRecord) -> EmploymentRecord:
        self.db.commit()
        self.db.refresh(record)
        return record
