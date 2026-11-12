from fastapi.testclient import TestClient
from app.main import app

def test_health_endpoint():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert isinstance(body["data"]["uptimeSeconds"], int)
    assert body["data"]["timestamp"].endswith("Z")

def test_auth_options_uses_shared_envelope():
    response = TestClient(app).get("/api/v1/auth/options")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "selfRegistration" in response.json()["data"]

def test_security_headers_are_present():
    response = TestClient(app).get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"

def test_openapi_exposes_the_express_route_contract():
    paths = TestClient(app).get("/openapi.json").json()["paths"]
    expected = {
        "/api/v1/auth/options", "/api/v1/auth/register", "/api/v1/auth/login",
        "/api/v1/auth/refresh", "/api/v1/auth/logout", "/api/v1/auth/me",
        "/api/v1/users", "/api/v1/users/{user_id}/roles", "/api/v1/roles",
        "/api/v1/demo/map/states", "/api/v1/demo/charts", "/api/v1/demo/tables",
    }
    assert expected.issubset(paths)

def test_me_requires_authentication_and_returns_shared_error_envelope():
    response = TestClient(app).get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "UNAUTHORIZED"

def test_refresh_requires_csrf_token():
    response = TestClient(app).post("/api/v1/auth/refresh")
    assert response.status_code == 403
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "FORBIDDEN"
