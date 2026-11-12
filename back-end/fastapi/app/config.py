from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    node_env: str = "development"
    port: int = 4000
    cors_origin: str = "http://localhost:5173"
    database_url: str = "mysql+asyncmy://cdis:cdis_dev_password@localhost:3308/cdis"
    jwt_access_secret: str = Field(min_length=32)
    jwt_access_expires_in_minutes: int = Field(default=15, gt=0)
    refresh_token_expires_in_days: int = Field(default=7, gt=0)
    bcrypt_salt_rounds: int = Field(default=12, ge=10, le=16)
    account_lockout_max_attempts: int = Field(default=5, gt=0)
    account_lockout_duration_minutes: int = Field(default=15, gt=0)
    allow_self_registration: bool = True
    cookie_secure: bool | None = None
    trust_proxy_hops: int = Field(default=0, ge=0)
    @field_validator("node_env")
    @classmethod
    def valid_env(cls, value: str) -> str:
        if value not in {"development", "test", "staging", "production"}: raise ValueError("NODE_ENV must be development, test, staging or production")
        return value
    @property
    def secure_cookies(self) -> bool:
        return self.cookie_secure if self.cookie_secure is not None else self.node_env in {"production", "staging"}
@lru_cache
def get_settings() -> Settings: return Settings()
settings = get_settings()
