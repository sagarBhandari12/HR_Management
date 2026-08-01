import pytest

from app.core.security import hash_password
from app.models.user import User, UserRole


@pytest.fixture
def test_admin_user(db_session):
    user = User(
        email="admin.test@regent.ac.uk",
        full_name="Test Administrator",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.mark.system
def test_login_success(client, test_admin_user):
    """Test successful login returns JWT bearer token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin.test@regent.ac.uk", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "ADMIN"


@pytest.mark.system
def test_login_invalid_password(client, test_admin_user):
    """Test login with invalid password returns 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin.test@regent.ac.uk", "password": "WrongPassword123!"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.system
def test_get_current_user_profile(client, test_admin_user):
    """Test fetching current user profile using JWT token."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin.test@regent.ac.uk", "password": "AdminPass123!"},
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin.test@regent.ac.uk"
    assert data["role"] == "ADMIN"
    assert "hashed_password" not in data
