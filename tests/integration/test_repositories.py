import pytest

from app.models.department import Department
from app.models.employee import Employee, EmployeeStatus
from app.models.user import User, UserRole
from app.repositories.audit_logs import AuditLogRepository
from app.repositories.departments import DepartmentRepository
from app.repositories.employees import EmployeeRepository
from app.repositories.users import UserRepository
from app.services.auditing import AuditService


@pytest.mark.integration
def test_user_repository(db_session):
    user_repo = UserRepository(db_session)
    user = User(
        email="repo.user@regent.ac.uk",
        full_name="Repo User",
        hashed_password="hashed_pass_xyz",
        role=UserRole.ADMIN,
        is_active=True,
    )
    created = user_repo.create(user)
    assert created.id is not None

    by_email = user_repo.get_by_email("repo.user@regent.ac.uk")
    assert by_email is not None
    assert by_email.id == created.id

    by_id = user_repo.get_by_id(created.id)
    assert by_id is not None

    all_users = user_repo.get_all()
    assert len(all_users) >= 1

    created.full_name = "Updated Repo User"
    updated = user_repo.update(created)
    assert updated.full_name == "Updated Repo User"


@pytest.mark.integration
def test_department_repository(db_session):
    dept_repo = DepartmentRepository(db_session)
    dept = Department(name="Physics", description="Dept of Physics", is_active=True)
    created = dept_repo.create(dept)
    assert created.id is not None

    by_name = dept_repo.get_by_name("physics")
    assert by_name is not None
    assert by_name.id == created.id

    count = dept_repo.count_active_employees(created.id)
    assert count == 0

    dept_repo.delete(created)
    assert dept_repo.get_by_id(created.id) is None


@pytest.mark.integration
def test_employee_repository_search_and_filter(db_session):
    dept_repo = DepartmentRepository(db_session)
    dept = dept_repo.create(Department(name="Chemistry", is_active=True))

    emp_repo = EmployeeRepository(db_session)
    emp1 = Employee(
        employee_number="EMP-8001",
        first_name="Brian",
        last_name="Cox",
        work_email="brian.cox@regent.ac.uk",
        department_id=dept.id,
        status=EmployeeStatus.ACTIVE,
        is_active=True,
    )
    emp2 = Employee(
        employee_number="EMP-8002",
        first_name="Ada",
        last_name="Lovelace",
        work_email="ada.lovelace@regent.ac.uk",
        department_id=dept.id,
        status=EmployeeStatus.ON_LEAVE,
        is_active=True,
    )
    emp_repo.create(emp1)
    emp_repo.create(emp2)

    # Search by name
    items, total = emp_repo.search_and_filter(search_query="Lovelace")
    assert total == 1
    assert items[0].first_name == "Ada"

    # Filter by status
    items_status, total_status = emp_repo.search_and_filter(status=EmployeeStatus.ON_LEAVE)
    assert total_status == 1
    assert items_status[0].employee_number == "EMP-8002"

    # Sorting
    items_sort, _ = emp_repo.search_and_filter(sort_by="first_name", sort_order="asc")
    assert items_sort[0].first_name == "Ada"


@pytest.mark.integration
def test_audit_log_repository(db_session):
    AuditService.log_event(
        db=db_session,
        actor_user_id=1,
        action="TEST_ACTION",
        entity_type="TestEntity",
        entity_id=99,
        description="Integration test audit entry",
    )

    audit_repo = AuditLogRepository(db_session)
    items, total = audit_repo.get_all(page=1, page_size=10)
    assert total >= 1
    assert items[0].action == "TEST_ACTION"
