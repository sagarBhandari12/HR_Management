import pytest

from app.core.security import hash_password
from app.models.user import User, UserRole


@pytest.fixture
def auth_tokens(client, db_session):
    # Admin
    admin = User(
        email="admin.sys@regent.ac.uk",
        full_name="System Admin",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    # HR Officer
    hr_officer = User(
        email="hr.sys@regent.ac.uk",
        full_name="HR Officer",
        hashed_password=hash_password("HrPass123!"),
        role=UserRole.HR_OFFICER,
        is_active=True,
    )
    # Viewer
    viewer = User(
        email="viewer.sys@regent.ac.uk",
        full_name="Viewer User",
        hashed_password=hash_password("ViewerPass123!"),
        role=UserRole.VIEWER,
        is_active=True,
    )
    db_session.add_all([admin, hr_officer, viewer])
    db_session.commit()

    admin_token = client.post(
        "/api/v1/auth/login",
        json={"email": "admin.sys@regent.ac.uk", "password": "AdminPass123!"},
    ).json()["access_token"]

    hr_token = client.post(
        "/api/v1/auth/login",
        json={"email": "hr.sys@regent.ac.uk", "password": "HrPass123!"},
    ).json()["access_token"]

    viewer_token = client.post(
        "/api/v1/auth/login",
        json={"email": "viewer.sys@regent.ac.uk", "password": "ViewerPass123!"},
    ).json()["access_token"]

    return {
        "admin": admin_token,
        "hr": hr_token,
        "viewer": viewer_token,
    }


@pytest.mark.system
def test_department_and_employee_lifecycle(client, auth_tokens):
    admin_hdr = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    hr_hdr = {"Authorization": f"Bearer {auth_tokens['hr']}"}
    viewer_hdr = {"Authorization": f"Bearer {auth_tokens['viewer']}"}

    # 1. Create Department as Admin
    dept_res = client.post(
        "/api/v1/departments",
        headers=admin_hdr,
        json={"name": "Computer Science", "description": "Faculty of Computing"},
    )
    assert dept_res.status_code == 201
    dept_id = dept_res.json()["id"]

    # 2. Viewer attempt to create department should be Forbidden (403)
    viewer_create_dept = client.post(
        "/api/v1/departments",
        headers=viewer_hdr,
        json={"name": "Illegal Dept"},
    )
    assert viewer_create_dept.status_code == 403

    # 3. Create Employee as HR Officer
    emp_res = client.post(
        "/api/v1/employees",
        headers=hr_hdr,
        json={
            "employee_number": "EMP-9901",
            "first_name": "Marcus",
            "last_name": "Vance",
            "work_email": "marcus.vance@regent.ac.uk",
            "department_id": dept_id,
            "status": "ACTIVE",
        },
    )
    assert emp_res.status_code == 201
    emp_id = emp_res.json()["id"]
    assert emp_res.json()["is_active"] is True

    # 4. Duplicate employee number conflict (409)
    dup_res = client.post(
        "/api/v1/employees",
        headers=hr_hdr,
        json={
            "employee_number": "EMP-9901",
            "first_name": "Marcus",
            "last_name": "Vance",
            "work_email": "marcus.different@regent.ac.uk",
            "department_id": dept_id,
        },
    )
    assert dup_res.status_code == 409

    # 5. Delete department blocked by active employee (409 Conflict)
    del_dept_res = client.delete(
        f"/api/v1/departments/{dept_id}",
        headers=admin_hdr,
    )
    assert del_dept_res.status_code == 409
    assert del_dept_res.json()["error"]["code"] == "CONFLICT"

    # 6. Deactivate employee (Soft Delete as Admin)
    deact_res = client.delete(
        f"/api/v1/employees/{emp_id}",
        headers=admin_hdr,
    )
    assert deact_res.status_code == 200
    assert deact_res.json()["is_active"] is False
    assert deact_res.json()["status"] == "TERMINATED"
    assert deact_res.json()["deactivated_at"] is not None

    # 7. Reactivate employee (Admin)
    react_res = client.post(
        f"/api/v1/employees/{emp_id}/reactivate",
        headers=admin_hdr,
    )
    assert react_res.status_code == 200
    assert react_res.json()["is_active"] is True
    assert react_res.json()["status"] == "ACTIVE"

    # 8. Reactivating already active employee returns controlled conflict (409)
    react_conflict = client.post(
        f"/api/v1/employees/{emp_id}/reactivate",
        headers=admin_hdr,
    )
    assert react_conflict.status_code == 409
