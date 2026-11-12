# CDIS FastAPI backend (alternative)

Python 3.12 + FastAPI alternative to the existing Express backend. The intended contract is the same versioned API so either frontend can target either backend.

## Local development

Create a virtual environment, install with `pip install -e ".[dev]"`, copy `.env.example` to `.env`, then run `uvicorn app.main:app --reload --port 4000`. FastAPI's interactive API documentation is at `/docs`.

## Status: scaffold only

This initial scaffold provides application configuration, health endpoint, CORS setup and OpenAPI generation. It is **not feature-equivalent to Express**. Authentication, refresh-token rotation, CSRF, account lockout, RBAC, user/role APIs, database models/migrations, seed data, demo endpoints, integration tests and deployment integration remain to be implemented before this backend should be selected for a real project.
