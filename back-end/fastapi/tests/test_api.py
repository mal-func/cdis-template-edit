from fastapi.testclient import TestClient
from app.main import app
def test_health_endpoint():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
def test_auth_options_uses_shared_envelope():
    response = TestClient(app).get("/api/v1/auth/options")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "selfRegistration" in response.json()["data"]
def test_security_headers_are_present():
    response = TestClient(app).get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
