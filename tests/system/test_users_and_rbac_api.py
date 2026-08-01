import pytest

from app.core.security import hash_password
from app.models.user import User, UserRole


@pytest.fixture
def user_tokens(client, db_session):
    admin = User(
        email="admin.users@regent.ac.uk",
        full_name="Admin Users",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    viewer = User(
        email="viewer.users@regent.ac.uk",
        full_name="Viewer Users",
        hashed_password=hash_password("ViewerPass123!"),
        role=UserRole.VIEWER,
        is_active=True,
    )
    disabled_user = User(
        email="disabled.user@regent.ac.uk",
        full_name="Disabled User",
        hashed_password=hash_password("DisabledPass123!"),
        role=UserRole.HR_OFFICER,
        is_active=False,
    )
    db_session.add_all([admin, viewer, disabled_user])
    db_session.commit()

    admin_token = client.post("/api/v1/auth/login", json={"email": "admin.users@regent.ac.uk", "password": "AdminPass123!"}).json()["access_token"]
    viewer_token = client.post("/api/v1/auth/login", json={"email": "viewer.users@regent.ac.uk", "password": "ViewerPass123!"}).json()["access_token"]

    return {
        "admin_hdr": {"Authorization": f"Bearer {admin_token}"},
        "viewer_hdr": {"Authorization": f"Bearer {viewer_token}"},
    }


@pytest.mark.system
def test_admin_user_management_flow(client, user_tokens):
    admin_hdr = user_tokens["admin_hdr"]
    viewer_hdr = user_tokens["viewer_hdr"]

    # 1. Admin creates a new HR Officer system user
    create_res = client.post(
        "/api/v1/users",
        headers=admin_hdr,
        json={
            "email": "new.hr@regent.ac.uk",
            "full_name": "New HR Officer",
            "password": "HrPassword123!",
            "role": "HR_OFFICER",
        },
    )
    assert create_res.status_code == 201
    new_user_id = create_res.json()["id"]

    # 2. Viewer attempt to create user is forbidden (403)
    viewer_create = client.post(
        "/api/v1/users",
        headers=viewer_hdr,
        json={
            "email": "illegal.user@regent.ac.uk",
            "full_name": "Illegal User",
            "password": "Password123!",
            "role": "VIEWER",
        },
    )
    assert viewer_create.status_code == 403

    # 3. Admin lists users
    list_res = client.get("/api/v1/users", headers=admin_hdr)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 2

    # 4. Admin updates user
    patch_res = client.patch(
        f"/api/v1/users/{new_user_id}",
        headers=admin_hdr,
        json={"full_name": "Updated HR Officer", "role": "ADMIN"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["full_name"] == "Updated HR Officer"
    assert patch_res.json()["role"] == "ADMIN"


@pytest.mark.system
def test_disabled_user_cannot_authenticate(client, user_tokens):
    """Test that inactive users cannot log in (403 Forbidden)."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "disabled.user@regent.ac.uk", "password": "DisabledPass123!"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
