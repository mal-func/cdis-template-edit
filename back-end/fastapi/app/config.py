from functools import lru_cache
import re
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    node_env: str = "development"
    port: int = 4000
    cors_origin: str = "http://localhost:5173"
    database_url: str = "mysql+asyncmy://cdis:cdis_dev_password@localhost:3308/cdis"
    jwt_access_secret: str = Field(min_length=32)
    jwt_access_expires_in: str = "15m"
    refresh_token_expires_in_days: int = Field(default=7, gt=0)
    bcrypt_salt_rounds: int = Field(default=12, ge=10, le=16)
    account_lockout_max_attempts: int = Field(default=5, gt=0)
    account_lockout_duration_minutes: int = Field(default=15, gt=0)
    allow_self_registration: bool = True
    trust_proxy_hops: int = Field(default=0, ge=0)
    @field_validator("jwt_access_expires_in")
    @classmethod
    def valid_access_duration(cls, value: str) -> str:
        if not re.fullmatch(r"[1-9][0-9]*(ms|s|m|h|d)", value.strip()):
            raise ValueError("JWT_ACCESS_EXPIRES_IN must be a positive duration such as 15m, 1h or 30s")
        return value.strip()
    @field_validator("node_env")
    @classmethod
    def valid_env(cls, value: str) -> str:
        if value not in {"development", "test", "staging", "production"}: raise ValueError("NODE_ENV must be development, test, staging or production")
        return value
    @property
    def jwt_access_expires_in_seconds(self) -> int:
        match = re.fullmatch(r"([1-9][0-9]*)(ms|s|m|h|d)", self.jwt_access_expires_in.strip())
        if not match:
            raise ValueError("JWT_ACCESS_EXPIRES_IN must be a positive duration such as 15m, 1h or 30s")
        amount, unit = int(match.group(1)), match.group(2)
        return max(1, amount // 1000) if unit == "ms" else amount * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    @property
    def secure_cookies(self) -> bool:
        return self.node_env in {"production", "staging"}
@lru_cache
def get_settings() -> Settings: return Settings()
settings = get_settings()
