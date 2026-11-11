# CDIS Engineering Template

Production-ready full-stack engineering template for building secure, scalable, and maintainable web applications using standardized engineering practices.

**Start here**: [`docs/START-HERE.md`](docs/START-HERE.md) — the full golden path from clone to a first PR, in one place.

This repository is the complete, canonical CDIS template: frontend, backend, deployment, and documentation, all together and kept current. The default frontend is React; an alternative Vue 3 frontend is available in `front-end-vue/`. Both frontends use the same Express backend and API contracts. Three sibling repositories — [`cdis-frontend`](https://github.com/WorkGaurav1/cdis-frontend), [`cdis-backend`](https://github.com/WorkGaurav1/cdis-backend), [`cdis-deployment`](https://github.com/WorkGaurav1/cdis-deployment) — are independently clone/build/run-able exports of this repo's `front-end/`, `back-end/`, and `deployment/` folders, for teams that only need one piece standalone. All new work happens here first; the three repos are regenerated from this one via `scripts/export-to-repos.sh`, never edited directly.

---

## Features

- React + TypeScript + Vite, with an alternative Vue 3 + TypeScript + Vite frontend
- Node.js + Express + TypeScript backend
- MySQL via Prisma, with real migrations and idempotent seeding
- Cookie-based auth: JWT access tokens, rotating refresh tokens with reuse detection, CSRF (double-submit), RBAC permissions
- Sign-in and self-registration pages (sign-up can be switched off), an admin role editor, and an initial admin seeded from env vars
- React Hook Form + Zod on the React frontend; Zod validation on the Vue frontend; Zod DTOs on the backend
- Docker (multi-stage, non-root, multi-platform) for the existing React app and backend; the Vue alternative has its own multi-stage Nginx image
- Apache httpd reverse proxy, Docker Compose (dev database, local stack, production, HTTPS), deploy/rollback/health-check scripts with migrations applied on every deploy
- Unit, integration (real MySQL), and end-to-end (Playwright) testing with enforced coverage floors for the existing stack; Vue frontend unit checks run in its own workflow
- Real CI on every push and PR (lint → type-check → tests → build → E2E → coverage → security), then image publishing and optional continuous deployment

---

## Repository Structure

```text
.
├── front-end/          # React application (default)
├── front-end-vue/      # Vue 3 alternative frontend
├── back-end/           # Node.js application / shared API
├── deployment/         # Docker Compose, reverse proxy, deploy scripts, E2E suite
├── docs/               # Engineering documentation
├── scripts/            # Tooling for this repo itself (e.g. exporting to the 3 sibling repos)
└── README.md
```

---

## Prerequisites

- Git
- Node.js 22+
- npm
- Docker + Docker Compose v2

---

# Bootstrap

## 1. Clone Repository

```bash
git clone <repository-url>
cd cdis-engineering-template
```

## 2. Install Dependencies

### React frontend

```bash
cd front-end
npm install
```

### Vue frontend (alternative)

```bash
cd front-end-vue
npm install
```

### Backend

```bash
cd ../back-end
npm install
```

## 3. Configure Environment

```bash
cp back-end/.env.example back-end/.env
cp front-end/.env.example front-end/.env
cp front-end-vue/.env.example front-end-vue/.env
```

The defaults match the dev database below — no edits needed for local development. When running the Vue frontend, ensure `CORS_ORIGIN` in the backend environment matches the Vue dev-server origin. The Vite dev server uses port 5173 by default.

## 4. Start the Database and Prepare It

```bash
docker compose -f deployment/compose/compose.dev.yaml up -d --wait

cd back-end
npx prisma migrate deploy   # create the tables
npm run prisma:seed         # roles/permissions + demo data
npm run db:test:prepare     # the separate database integration tests use
```

`compose.dev.yaml` is MySQL only, on `localhost:3308`, with fixed dev credentials. It creates both the `cdis` (dev) and `cdis_test` (integration tests) databases.

## 5. Start Backend and Frontend

Start the backend:

```bash
cd back-end && npm run dev     # http://localhost:4000
```

Start either frontend in a separate terminal:

```bash
cd front-end && npm run dev       # React, http://localhost:5173
# or
cd front-end-vue && npm run dev   # Vue, http://localhost:5173
```

Use one frontend at a time with the default Vite port. Open the selected frontend and create an account with **Create one** on the sign-in page. To make yourself an admin, see [`docs/START-HERE.md`](docs/START-HERE.md#8-sign-in-and-become-an-admin).

Alternatively, bring up the entire existing stack (MySQL + backend + React frontend + Apache reverse proxy) in containers at once with `deployment/scripts/e2e-up.sh` — see [`deployment/README.md`](deployment/README.md). To use the Vue container instead, set `FRONTEND_BUILD_CONTEXT=../../front-end-vue` in `deployment/compose/.env` before building the `frontend` service.

---

# Build

### React frontend

```bash
cd front-end
npm run build
```

### Vue frontend

```bash
cd front-end-vue
npm run build
```

### Backend

```bash
cd back-end
npm run build   # type-check only — the backend ships TypeScript source, run via tsx, not a compiled build
```

---

# Testing

### React frontend

```bash
cd front-end
npm test
```

### Vue frontend

```bash
cd front-end-vue
npm test
npm run lint
```

### Backend

```bash
cd back-end
npm test                  # unit
npm run test:integration  # real MySQL — needs the dev database (step 4)
```

### End-to-End

The existing cross-application E2E suite drives a real browser against the deployed React stack — see [`deployment/README.md`](deployment/README.md):

```bash
cd deployment
./scripts/e2e-up.sh
npm run test:e2e
```

Vue-specific browser E2E coverage remains to be added; the Vue unit workflow does not yet establish full browser-level parity.

---

# Development Workflow

## Add a New Feature

See [`docs/development/adding-feature.md`](docs/development/adding-feature.md) for the actual, project-specific sequence (feature-module registration, route/nav wiring, permission gating, tests).

## Add an API Endpoint

See [`docs/development/adding-api.md`](docs/development/adding-api.md) for the real route → DTO → middleware → controller → service → repository sequence.

---

# Documentation

| Document | Purpose |
|----------|---------|
| [`docs/START-HERE.md`](docs/START-HERE.md) | The golden path — read this first |
| `front-end/README.md` | React frontend development guide |
| [`front-end-vue/README.md`](front-end-vue/README.md) | Vue frontend development guide |
| `back-end/README.md` | Backend development guide |
| `deployment/README.md` | Docker Compose, reverse proxy, deploy/rollback, HTTPS |
| `docs/architecture/` | System architecture, request flow, auth/authz |
| `docs/standards/` | Engineering standards (code style, Docker, deployment, security, testing, etc.) |
| `docs/development/` | Development workflows (starting a new project, adding a feature, an endpoint, a module) |
| `docs/architecture-decision-record/` | Architectural decision records |

---

# References

- React — https://react.dev
- Vue — https://vuejs.org/
- Vite — https://vite.dev
- Node.js — https://nodejs.org
- Express — https://expressjs.com
- TypeScript — https://www.typescriptlang.org
- MySQL — https://dev.mysql.com/doc/
- Docker — https://docs.docker.com/
- Apache httpd — https://httpd.apache.org/docs/2.4/
- OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
