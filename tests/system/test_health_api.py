import pytest


@pytest.mark.system
def test_root_endpoint(client):
    """Test root GET / landing endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["docs_url"] == "/docs"


@pytest.mark.system
def test_health_endpoint(client):
    """Test /health endpoint returns 200 OK and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "version" in data


@pytest.mark.system
def test_health_database_endpoint(client):
    """Test /health/database endpoint checks DB connectivity."""
    response = client.get("/health/database")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


@pytest.mark.system
def test_version_endpoint(client):
    """Test /version endpoint returns API version info."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["api_v1_prefix"] == "/api/v1"
