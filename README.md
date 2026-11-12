# CDIS Engineering Template

Canonical full-stack template with selectable frontend and backend implementations.

- **Default frontend:** React + TypeScript + Vite at `front-end/react/`
- **Alternative frontend:** Vue 3 + TypeScript + Vite at `front-end/vue/`
- **Default backend:** Express + TypeScript at `back-end/express/`
- **Alternative backend:** FastAPI + Python scaffold at `back-end/fastapi/`

React and Vue are intended to consume the same API contract. Express is the established backend and currently provides the complete application API. FastAPI is an initial scaffold only and is not yet feature-equivalent.

All changes belong in this canonical repository first. The sibling frontend, backend and deployment repositories are exports maintained through `scripts/export-to-repos.sh`.

## Repository structure

```text
.
├── front-end/
│   ├── react/       # Default frontend
│   └── vue/         # Alternative frontend
├── back-end/
│   ├── express/     # Default backend
│   └── fastapi/     # Alternative backend scaffold
├── deployment/
├── docs/
├── scripts/
└── cdis-template.json
```

## Prerequisites

- Node.js 22+ and npm for React, Vue and Express
- Python 3.12+ for FastAPI
- Docker and Docker Compose v2 for the containerized stack

## Run the default React + Express stack

Install the Express backend:

```bash
cd back-end/express
npm ci
cp .env.example .env
```

Install React:

```bash
cd ../../front-end/react
npm ci
cp .env.example .env
```

Start MySQL and prepare the Express database from the repository root:

```bash
docker compose -f deployment/compose/compose.dev.yaml up -d --wait
cd back-end/express
npx prisma migrate deploy
npm run prisma:seed
npm run dev
```

In another terminal, start React:

```bash
cd front-end/react
npm run dev
```

## Run the Vue frontend

Vue uses the same Express API. Install and start it instead of React:

```bash
cd front-end/vue
npm install
npm run dev
```

Ensure the Express `CORS_ORIGIN` setting allows the Vue development server origin. The Vue app's own README documents its stack and Docker configuration.

## FastAPI backend option

The FastAPI directory is currently a scaffold, not a production-ready alternative. See `back-end/fastapi/README.md` for its current scope and missing parity work. Do not select it for a real application until authentication/session security, RBAC, database migrations, seed data, full API compatibility and tests have been implemented.

## Build and test

React and Express have their existing project-specific build and test commands in their respective READMEs. Vue has lint, unit-test and build scripts; its lockfile and browser-level parity coverage still need to be completed and verified. FastAPI currently has no complete test or migration suite.

The combined CI workflow currently validates the established React + Express stack. Vue has a separate workflow. FastAPI needs its own validation workflow once its implementation is mature enough.

## Template manifest

`cdis-template.json` currently records the frontend/backend identifiers, paths and defaults:

- `react` → `front-end/react` (default)
- `vue` → `front-end/vue`
- `express` → `back-end/express` (default)
- `fastapi` → `back-end/fastapi`

The CLI integration is being developed separately. Treat this manifest structure as the template-side working contract until the CLI schema is confirmed.

## Documentation

- `front-end/react/README.md`
- `front-end/vue/README.md`
- `back-end/express/README.md`
- `back-end/fastapi/README.md`
- `deployment/README.md`
- `docs/START-HERE.md`
