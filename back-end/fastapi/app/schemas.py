from pydantic import BaseModel, EmailStr, Field, field_validator
class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    @field_validator("name")
    @classmethod
    def trim_name(cls, value):
        value = value.strip()
        if not value: raise ValueError("Name is required.")
        return value
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value): return value.strip().lower()
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value): return value.strip().lower()
class SetUserRolesRequest(BaseModel):
    roles: list[str] = Field(min_length=1, max_length=50)
    @field_validator("roles")
    @classmethod
    def normalize_roles(cls, values):
        cleaned = [v.strip() for v in values]
        if any(not v for v in cleaned): raise ValueError("Role names can't be empty.")
        return list(dict.fromkeys(cleaned))
