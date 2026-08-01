import pytest

from app.core.security import hash_password
from app.models.department import Department
from app.models.employee import Employee, EmployeeStatus
from app.models.user import User, UserRole


@pytest.fixture
def m3_full_setup(db_session, client):
    admin = User(
        email="admin.m3full@regent.ac.uk",
        full_name="Admin M3 Full",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    hr_officer = User(
        email="hr.m3full@regent.ac.uk",
        full_name="HR M3 Full",
        hashed_password=hash_password("HrPass123!"),
        role=UserRole.HR_OFFICER,
        is_active=True,
    )
    db_session.add_all([admin, hr_officer])
    db_session.commit()

    dept = Department(name="Cyber Security", description="CS Dept", is_active=True)
    db_session.add(dept)
    db_session.commit()

    emp = Employee(
        employee_number="EMP-8801",
        first_name="Liam",
        last_name="Neeson",
        work_email="liam.n@regent.ac.uk",
        department_id=dept.id,
        status=EmployeeStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(emp)
    db_session.commit()

    admin_token = client.post("/api/v1/auth/login", json={"email": "admin.m3full@regent.ac.uk", "password": "AdminPass123!"}).json()["access_token"]
    hr_token = client.post("/api/v1/auth/login", json={"email": "hr.m3full@regent.ac.uk", "password": "HrPass123!"}).json()["access_token"]

    return {
        "admin_hdr": {"Authorization": f"Bearer {admin_token}"},
        "hr_hdr": {"Authorization": f"Bearer {hr_token}"},
        "emp_id": emp.id,
        "dept_id": dept.id,
    }


@pytest.mark.system
def test_all_provider_scenarios_execution(client, m3_full_setup):
    hr_hdr = m3_full_setup["hr_hdr"]
    emp_id = m3_full_setup["emp_id"]

    # 1. Right to Work - Rejected Scenario
    rtw_res = client.post(f"/api/v1/employees/{emp_id}/background-checks", headers=hr_hdr, json={"check_type": "RIGHT_TO_WORK"})
    rtw_id = rtw_res.json()["id"]
    rtw_exec = client.post(f"/api/v1/background-checks/{rtw_id}/execute", headers=hr_hdr, json={"scenario": "rejected"})
    assert rtw_exec.status_code == 200
    assert rtw_exec.json()["status"] == "REJECTED"

    # 2. Credit Agency - Review Required Scenario
    cred_res = client.post(f"/api/v1/employees/{emp_id}/background-checks", headers=hr_hdr, json={"check_type": "CREDIT"})
    cred_id = cred_res.json()["id"]
    cred_exec = client.post(f"/api/v1/background-checks/{cred_id}/execute", headers=hr_hdr, json={"scenario": "review_required"})
    assert cred_exec.status_code == 200
    assert cred_exec.json()["status"] == "REVIEW_REQUIRED"

    # 3. Bank Verification - Unavailable Scenario
    bank_res = client.post(f"/api/v1/employees/{emp_id}/background-checks", headers=hr_hdr, json={"check_type": "BANK_VERIFICATION"})
    bank_id = bank_res.json()["id"]
    bank_exec = client.post(f"/api/v1/background-checks/{bank_id}/execute", headers=hr_hdr, json={"scenario": "unavailable"})
    assert bank_exec.status_code == 200
    assert bank_exec.json()["status"] == "FAILED"

    # 4. DBS - Timeout Scenario
    dbs_res = client.post(f"/api/v1/employees/{emp_id}/background-checks", headers=hr_hdr, json={"check_type": "DBS"})
    dbs_id = dbs_res.json()["id"]
    dbs_exec = client.post(f"/api/v1/background-checks/{dbs_id}/execute", headers=hr_hdr, json={"scenario": "timeout"})
    assert dbs_exec.status_code == 200
    assert dbs_exec.json()["status"] == "FAILED"


@pytest.mark.system
def test_department_and_employee_update_routes(client, m3_full_setup):
    admin_hdr = m3_full_setup["admin_hdr"]
    hr_hdr = m3_full_setup["hr_hdr"]
    dept_id = m3_full_setup["dept_id"]
    emp_id = m3_full_setup["emp_id"]

    # Update Department as Admin
    dept_patch = client.patch(f"/api/v1/departments/{dept_id}", headers=admin_hdr, json={"description": "Updated CS Dept"})
    assert dept_patch.status_code == 200
    assert dept_patch.json()["description"] == "Updated CS Dept"

    # Get department details
    dept_get = client.get(f"/api/v1/departments/{dept_id}", headers=hr_hdr)
    assert dept_get.status_code == 200

    # Update Employee as HR Officer
    emp_patch = client.patch(f"/api/v1/employees/{emp_id}", headers=hr_hdr, json={"telephone": "+447700900999"})
    assert emp_patch.status_code == 200
    assert emp_patch.json()["telephone"] == "+447700900999"

    # List employees with search, filter, and sorting
    emp_list = client.get("/api/v1/employees?search=Liam&sort_by=first_name&sort_order=desc", headers=hr_hdr)
    assert emp_list.status_code == 200
    assert emp_list.json()["total"] >= 1
