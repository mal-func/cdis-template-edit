import os
os.environ.setdefault("JWT_ACCESS_SECRET", "test-secret-that-is-long-enough-for-cdis")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("NODE_ENV", "test")
