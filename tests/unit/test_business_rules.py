import pytest

from app.core.exceptions import ConflictException, UnprocessableEntityException
from app.models.background_check import CheckStatus, CheckType
from app.models.department import Department
from app.models.employee import Employee, EmployeeStatus
from app.models.employment_record import EmploymentType
from app.models.user import User, UserRole
from app.schemas.background_check import BackgroundCheckUpdate
from app.schemas.employment_record import EmploymentRecordCreate
from app.services.background_checks import BackgroundCheckService
from app.services.departments import DepartmentService
from app.services.employees import EmployeeService
from app.services.employment_records import EmploymentRecordService


@pytest.fixture
def mock_actor():
    return User(id=1, email="admin@regent.ac.uk", role=UserRole.ADMIN, is_active=True)


@pytest.mark.unit
def test_department_deletion_blocked_by_active_employees(db_session, mock_actor):
    dept_service = DepartmentService(db_session)
    dept = dept_service.create_department(
        dept_in=type("Obj", (), {"name": "Maths", "description": "Mathematics"})(),
        actor=mock_actor,
    )

    # Create active employee in department
    emp = Employee(
        employee_number="EMP-MATH-01",
        first_name="Carl",
        last_name="Gauss",
        work_email="gauss@regent.ac.uk",
        department_id=dept.id,
        status=EmployeeStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(emp)
    db_session.commit()

    # Attempting to delete department should raise ConflictException (Rule 8)
    with pytest.raises(ConflictException):
        dept_service.delete_department(dept.id, actor=mock_actor)


@pytest.mark.unit
def test_terminated_employee_cannot_receive_employment_record(db_session, mock_actor):
    dept_service = DepartmentService(db_session)
    dept = dept_service.create_department(
        dept_in=type("Obj", (), {"name": "History", "description": "Dept of History"})(),
        actor=mock_actor,
    )

    emp_service = EmployeeService(db_session)
    emp_in = type(
        "Obj",
        (),
        {
            "employee_number": "EMP-HIST-01",
            "first_name": "Edward",
            "last_name": "Gibbon",
            "work_email": "gibbon@regent.ac.uk",
            "personal_email": None,
            "telephone": None,
            "date_of_birth": None,
            "department_id": dept.id,
            "status": EmployeeStatus.ACTIVE,
        },
    )()
    emp = emp_service.create_employee(emp_in, actor=mock_actor)

    # Deactivate employee
    emp_service.deactivate_employee(emp.id, actor=mock_actor)

    # Attempt to create employment record for terminated employee should raise ConflictException (Rule 11)
    rec_service = EmploymentRecordService(db_session)
    rec_in = EmploymentRecordCreate(
        job_title="Historian",
        employment_type=EmploymentType.PERMANENT,
        start_date="2025-01-01",
        salary_band="Band 6",
    )
    with pytest.raises(ConflictException):
        rec_service.create_record(emp.id, rec_in, actor=mock_actor)


@pytest.mark.unit
def test_background_check_approval_without_provider_reference_raises_unprocessable(db_session, mock_actor):
    dept = Department(name="Law", is_active=True)
    db_session.add(dept)
    db_session.commit()

    emp = Employee(
        employee_number="EMP-LAW-01",
        first_name="Hugo",
        last_name="Grotius",
        work_email="grotius@regent.ac.uk",
        department_id=dept.id,
        status=EmployeeStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(emp)
    db_session.commit()

    check_service = BackgroundCheckService(db_session)
    check_in = type("Obj", (), {"check_type": CheckType.DBS, "restricted_notes": "Initial check"})()
    check = check_service.create_check(emp.id, check_in, actor=mock_actor)

    # Attempting to set APPROVED without provider_reference raises UnprocessableEntityException (Rule 13)
    update_in = BackgroundCheckUpdate(status=CheckStatus.APPROVED, provider_reference="")
    with pytest.raises(UnprocessableEntityException):
        check_service.update_check(check.id, update_in, actor=mock_actor)
