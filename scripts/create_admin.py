import os
import sys

# Ensure app is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.logging import logger
from app.db.session import SessionLocal
from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.services.authentication import AuthenticationService


def create_initial_admin():
    db = SessionLocal()
    try:
        auth_service = AuthenticationService(db)
        existing = auth_service.user_repo.get_by_email(settings.FIRST_SUPERADMIN_EMAIL)
        if existing:
            print(f"[*] Admin user '{settings.FIRST_SUPERADMIN_EMAIL}' already exists.")
            return

        admin_in = UserCreate(
            email=settings.FIRST_SUPERADMIN_EMAIL,
            full_name=settings.FIRST_SUPERADMIN_FULL_NAME,
            password=settings.FIRST_SUPERADMIN_PASSWORD,
            role=UserRole.ADMIN,
        )

        admin_user = auth_service.create_user(admin_in, actor=None)
        print(f"[+] Initial Superadmin successfully created:")
        print(f"    Email: {admin_user.email}")
        print(f"    Role:  {admin_user.role.value}")
        print(f"    ID:    {admin_user.id}")
    except Exception as e:
        print(f"[!] Error creating admin user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_admin()
