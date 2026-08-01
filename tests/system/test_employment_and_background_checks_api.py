import pytest

from app.core.security import hash_password
from app.models.department import Department
from app.models.employee import Employee, EmployeeStatus
from app.models.user import User, UserRole
from app.services.auditing import AuditService


@pytest.fixture
def test_setup(db_session, client):
    admin = User(
        email="admin.m3@regent.ac.uk",
        full_name="Admin M3",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    hr_officer = User(
        email="hr.m3@regent.ac.uk",
        full_name="HR Officer M3",
        hashed_password=hash_password("HrPass123!"),
        role=UserRole.HR_OFFICER,
        is_active=True,
    )
    viewer = User(
        email="viewer.m3@regent.ac.uk",
        full_name="Viewer M3",
        hashed_password=hash_password("ViewerPass123!"),
        role=UserRole.VIEWER,
        is_active=True,
    )
    db_session.add_all([admin, hr_officer, viewer])
    db_session.commit()

    dept = Department(name="Software Engineering", description="SE Faculty", is_active=True)
    db_session.add(dept)
    db_session.commit()

    emp = Employee(
        employee_number="EMP-7701",
        first_name="Sophia",
        last_name="Martinez",
        work_email="sophia.m@regent.ac.uk",
        department_id=dept.id,
        status=EmployeeStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(emp)
    db_session.commit()

    # Log initial setup audit event
    AuditService.log_event(
        db=db_session,
        actor_user_id=admin.id,
        action="SYSTEM_INIT",
        entity_type="System",
        entity_id=1,
        description="Initial test system setup",
    )

    admin_token = client.post("/api/v1/auth/login", json={"email": "admin.m3@regent.ac.uk", "password": "AdminPass123!"}).json()["access_token"]
    hr_token = client.post("/api/v1/auth/login", json={"email": "hr.m3@regent.ac.uk", "password": "HrPass123!"}).json()["access_token"]
    viewer_token = client.post("/api/v1/auth/login", json={"email": "viewer.m3@regent.ac.uk", "password": "ViewerPass123!"}).json()["access_token"]

    return {
        "admin_hdr": {"Authorization": f"Bearer {admin_token}"},
        "hr_hdr": {"Authorization": f"Bearer {hr_token}"},
        "viewer_hdr": {"Authorization": f"Bearer {viewer_token}"},
        "emp_id": emp.id,
        "dept_id": dept.id,
    }


@pytest.mark.system
def test_employment_records_and_invalid_date_rule(client, test_setup):
    hr_hdr = test_setup["hr_hdr"]
    emp_id = test_setup["emp_id"]

    # 1. Add valid employment record
    rec_res = client.post(
        f"/api/v1/employees/{emp_id}/employment-records",
        headers=hr_hdr,
        json={
            "job_title": "Lead Software Engineer",
            "employment_type": "PERMANENT",
            "start_date": "2024-01-01",
            "salary_band": "Band 8",
        },
    )
    assert rec_res.status_code == 201
    assert rec_res.json()["job_title"] == "Lead Software Engineer"

    # 2. Invalid date range (end_date < start_date) returns 422
    bad_date_res = client.post(
        f"/api/v1/employees/{emp_id}/employment-records",
        headers=hr_hdr,
        json={
            "job_title": "Short Contract",
            "start_date": "2025-06-01",
            "end_date": "2024-01-01",
            "salary_band": "Band 5",
        },
    )
    assert bad_date_res.status_code == 422


@pytest.mark.system
def test_background_check_execution_and_privacy_rule(client, test_setup):
    hr_hdr = test_setup["hr_hdr"]
    viewer_hdr = test_setup["viewer_hdr"]
    emp_id = test_setup["emp_id"]

    # 1. Initiate background check
    check_res = client.post(
        f"/api/v1/employees/{emp_id}/background-checks",
        headers=hr_hdr,
        json={"check_type": "DBS", "restricted_notes": "Sensitive HR background notes"},
    )
    assert check_res.status_code == 201
    check_id = check_res.json()["id"]

    # 2. Execute mock check simulation (Approved scenario)
    exec_res = client.post(
        f"/api/v1/background-checks/{check_id}/execute",
        headers=hr_hdr,
        json={"scenario": "approved"},
    )
    assert exec_res.status_code == 200
    assert exec_res.json()["status"] == "APPROVED"
    assert exec_res.json()["provider_reference"].startswith("DBS-CERT-")

    # 3. Fetch check details as HR Officer (restricted notes visible)
    hr_get = client.get(f"/api/v1/background-checks/{check_id}", headers=hr_hdr)
    assert hr_get.status_code == 200
    assert hr_get.json()["restricted_notes"] is not None

    # 4. Fetch check details as Viewer (Rule 22: restricted_notes must be None)
    viewer_get = client.get(f"/api/v1/background-checks/{check_id}", headers=viewer_hdr)
    assert viewer_get.status_code == 200
    assert viewer_get.json()["restricted_notes"] is None


@pytest.mark.system
def test_reports_and_audit_logs_endpoints(client, test_setup):
    admin_hdr = test_setup["admin_hdr"]
    hr_hdr = test_setup["hr_hdr"]
    viewer_hdr = test_setup["viewer_hdr"]

    # 1. Dashboard summary report
    dash_res = client.get("/api/v1/reports/dashboard", headers=hr_hdr)
    assert dash_res.status_code == 200
    assert "total_employees" in dash_res.json()

    # 2. Headcount by department report
    headcount_res = client.get("/api/v1/reports/headcount-by-department", headers=hr_hdr)
    assert headcount_res.status_code == 200
    assert len(headcount_res.json()) >= 1

    # 3. Audit log endpoint (Admin allowed, Viewer forbidden)
    audit_admin = client.get("/api/v1/audit-logs", headers=admin_hdr)
    assert audit_admin.status_code == 200
    assert audit_admin.json()["total"] >= 1

    audit_viewer = client.get("/api/v1/audit-logs", headers=viewer_hdr)
    assert audit_viewer.status_code == 403
