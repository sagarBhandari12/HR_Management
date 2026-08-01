"""Import all declarative SQLAlchemy models here so Alembic can discover them for migrations."""

from app.db.session import Base  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.background_check import BackgroundCheck  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.employee import Employee  # noqa: F401
from app.models.employment_record import EmploymentRecord  # noqa: F401
from app.models.external_request import ExternalRequest  # noqa: F401
from app.models.user import User  # noqa: F401
