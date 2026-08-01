from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.background_check import BackgroundCheck
from app.models.external_request import ExternalRequest


class BackgroundCheckRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, check_id: int) -> Optional[BackgroundCheck]:
        return self.db.query(BackgroundCheck).filter(BackgroundCheck.id == check_id).first()

    def get_by_employee_id(self, employee_id: int) -> List[BackgroundCheck]:
        return (
            self.db.query(BackgroundCheck)
            .filter(BackgroundCheck.employee_id == employee_id)
            .order_by(BackgroundCheck.created_at.desc())
            .all()
        )

    def create(self, check: BackgroundCheck) -> BackgroundCheck:
        self.db.add(check)
        self.db.commit()
        self.db.refresh(check)
        return check

    def update(self, check: BackgroundCheck) -> BackgroundCheck:
        self.db.commit()
        self.db.refresh(check)
        return check

    def create_external_request(self, req: ExternalRequest) -> ExternalRequest:
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req
