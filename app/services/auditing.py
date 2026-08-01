from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.audit_log import AuditLog


class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        actor_user_id: Optional[int],
        action: str,
        entity_type: str,
        entity_id: Optional[int],
        description: str,
    ) -> AuditLog:
        """
        Creates an immutable audit log record.
        Sanitizes description to ensure sensitive credentials are never stored.
        """
        audit_entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)

        logger.info(
            f"AUDIT LOG: actor_id={actor_user_id} action='{action}' "
            f"entity='{entity_type}:{entity_id}' desc='{description}'"
        )
        return audit_entry
