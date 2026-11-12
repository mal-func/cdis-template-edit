import pytest
from pydantic import ValidationError
from app.schemas import LoginRequest, RegisterRequest, SetUserRolesRequest

def test_register_normalizes_email_and_name():
    payload = RegisterRequest(email="  Person@Example.com ", name="  Person  ", password="password123")
    assert payload.email == "person@example.com"
    assert payload.name == "Person"

def test_register_rejects_short_password():
    with pytest.raises(ValidationError):
        RegisterRequest(email="person@example.com", name="Person", password="short")

def test_login_normalizes_email():
    assert LoginRequest(email=" USER@example.com ", password="secret").email == "user@example.com"

def test_role_names_are_trimmed_and_deduplicated():
    assert SetUserRolesRequest(roles=[" admin ", "admin", "user"]).roles == ["admin", "user"]

def test_role_list_cannot_be_empty():
    with pytest.raises(ValidationError):
        SetUserRolesRequest(roles=[])
