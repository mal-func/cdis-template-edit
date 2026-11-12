# CDIS FastAPI backend

Python/FastAPI alternative to Express. It implements the same versioned API routes and response envelope, with SQLAlchemy models mapped to the same logical tables and camelCase database columns as the Prisma schema.

## Stack
- Python 3.12+, FastAPI, Pydantic Settings
- SQLAlchemy 2 async ORM + MySQL (`asyncmy`)
- Alembic migrations
- JWT access tokens, bcrypt password hashes, SHA-256 hashed opaque refresh tokens
- CSRF double-submit cookies, account lockout, rate limiting and security headers
- Pytest and Ruff

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
cp .env.example .env
# Set JWT_ACCESS_SECRET to a unique random value of at least 32 characters.
# Start MySQL using deployment/compose/compose.dev.yaml.
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 4000
```

Interactive API documentation is at `/docs`. Set `CORS_ORIGIN` to the frontend origin. Use `COOKIE_SECURE=true` (or `NODE_ENV=staging/production`) behind HTTPS. Never use the example secret in production.

## API compatibility
- `GET /health`
- `GET /api/v1/auth/options`
- `POST /api/v1/auth/register`, `/login`, `/refresh`, `/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/users?limit=&offset=`
- `PUT /api/v1/users/{id}/roles`
- `GET /api/v1/roles`
- `GET /api/v1/demo/map/states`, `/charts?type=`, `/tables`

Success responses use `{success:true,data:{...}}`; errors use `{success:false,error:{code,message}}`. Cookie names, paths, CSRF header, permission keys and safe-user response shape follow Express.

## Security and operations
Access tokens are httpOnly cookies (15 minutes by default); refresh tokens are random 256-bit values, stored only as SHA-256 hashes and rotated on refresh. Reuse of a revoked refresh token revokes all active sessions for that user. The refresh cookie is scoped to `/api/v1/auth`; the readable CSRF cookie must be echoed in `X-CSRF-Token` for refresh, logout and role changes. Role permissions are loaded from the database for each authenticated request. Login is rate-limited to 10 attempts per 15 minutes per client IP and normalized email, and accounts lock after the configured number of failed attempts.

SlowAPI's default in-memory storage is suitable only for a single-process template deployment. Use shared Redis-backed rate limiting or a gateway policy for multi-worker/multi-instance production. Set `TRUST_PROXY_HOPS` only to the number of reverse proxies you control; do not trust arbitrary forwarded headers.

## Migrations, seed and tests
`alembic upgrade head` creates the schema. `python -m app.seed` idempotently seeds roles, permissions, optional initial admin (`SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD`, both or neither), and synthetic map/chart/table data. Run `pytest` and `ruff check .`.

## Deployment boundary

The FastAPI backend currently has a local Compose overlay and can be exercised by the shared Playwright suite. The production image-publishing and deploy/rollback workflow still targets the established Express image; do not select FastAPI for production deployment until its image publishing, production Compose overlay, migration/rollback procedure and deployment workflow have been added and reviewed.

## Validation status
The implementation targets the Express API contract. The FastAPI workflow and the shared frontend E2E suite must pass against this backend before declaring verified feature parity. Review proxy trust, rate-limit storage, secrets, TLS and database operations for each deployment.