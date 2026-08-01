import os
import sys

# Ensure app is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.user import UserRole
from app.schemas.department import DepartmentCreate
from app.schemas.employee import EmployeeCreate
from app.schemas.user import UserCreate
from app.services.authentication import AuthenticationService
from app.services.departments import DepartmentService
from app.services.employees import EmployeeService


def seed_demo_data():
    db = SessionLocal()
    try:
        auth_service = AuthenticationService(db)
        dept_service = DepartmentService(db)
        emp_service = EmployeeService(db)

        # 1. Fetch or ensure Admin user
        admin = auth_service.user_repo.get_by_email("admin@regent.ac.uk")
        if not admin:
            admin_in = UserCreate(
                email="admin@regent.ac.uk",
                full_name="System Administrator",
                password="AdminPassword123!",
                role=UserRole.ADMIN,
            )
            admin = auth_service.create_user(admin_in, actor=None)
            print("[+] Seeded Admin user.")

        # 2. Seed System Users (HR Officer and Viewer)
        if not auth_service.user_repo.get_by_email("hr.officer@regent.ac.uk"):
            hr_in = UserCreate(
                email="hr.officer@regent.ac.uk",
                full_name="Jane Doe (HR Officer)",
                password="HrPassword123!",
                role=UserRole.HR_OFFICER,
            )
            auth_service.create_user(hr_in, actor=admin)
            print("[+] Seeded HR Officer: hr.officer@regent.ac.uk")

        if not auth_service.user_repo.get_by_email("viewer@regent.ac.uk"):
            viewer_in = UserCreate(
                email="viewer@regent.ac.uk",
                full_name="John Smith (Viewer)",
                password="ViewerPassword123!",
                role=UserRole.VIEWER,
            )
            auth_service.create_user(viewer_in, actor=admin)
            print("[+] Seeded Viewer: viewer@regent.ac.uk")

        # 3. Seed Departments
        departments = [
            ("Human Resources", "Regent College London Central HR Team"),
            ("Academic Affairs", "Faculty of Science & Technology"),
            ("Finance & Operations", "Payroll and Institutional Finance"),
            ("IT Support & Infrastructure", "Systems and Cloud Infrastructure"),
        ]

        dept_map = {}
        for name, desc in departments:
            existing = dept_service.dept_repo.get_by_name(name)
            if not existing:
                res = dept_service.create_department(DepartmentCreate(name=name, description=desc), actor=admin)
                dept_map[name] = res.id
                print(f"[+] Seeded Department: '{name}'")
            else:
                dept_map[name] = existing.id

        # 4. Seed Synthetic Employees
        demo_employees = [
            {
                "employee_number": "EMP-1001",
                "first_name": "Alice",
                "last_name": "Taylor",
                "work_email": "alice.taylor@regent.ac.uk",
                "personal_email": "alice.t@synthetic.org",
                "telephone": "+447700900001",
                "department_id": dept_map["Human Resources"],
            },
            {
                "employee_number": "EMP-1002",
                "first_name": "Robert",
                "last_name": "Chen",
                "work_email": "robert.chen@regent.ac.uk",
                "personal_email": "robert.c@synthetic.org",
                "telephone": "+447700900002",
                "department_id": dept_map["Academic Affairs"],
            },
            {
                "employee_number": "EMP-1003",
                "first_name": "Elena",
                "last_name": "Rostova",
                "work_email": "elena.rostova@regent.ac.uk",
                "personal_email": "elena.r@synthetic.org",
                "telephone": "+447700900003",
                "department_id": dept_map["Finance & Operations"],
            },
        ]

        for emp_data in demo_employees:
            existing = emp_service.emp_repo.get_by_employee_number(emp_data["employee_number"])
            if not existing:
                emp_service.create_employee(EmployeeCreate(**emp_data), actor=admin)
                print(f"[+] Seeded Employee: {emp_data['employee_number']} ({emp_data['first_name']} {emp_data['last_name']})")

        print("[*] Demonstration data seeding completed successfully.")
    except Exception as e:
        print(f"[!] Error seeding demo data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
