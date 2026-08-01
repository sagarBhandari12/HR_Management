from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, page: int = 1, page_size: int = 50) -> Tuple[List[AuditLog], int]:
        query = self.db.query(AuditLog).order_by(AuditLog.created_at.desc())
        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        return items, total
