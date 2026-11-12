# CDIS Engineering Template

Canonical full-stack template with selectable frontend and backend implementations.

- **Default frontend:** React + TypeScript + Vite at `front-end/react/`
- **Alternative frontend:** Vue 3 + TypeScript + Vite at `front-end/vue/`
- **Default backend:** Express + TypeScript at `back-end/express/`
- **Alternative backend:** FastAPI + Python at `back-end/fastapi/`

React and Vue are intended to consume the same API contract. Express is the established, production-integrated backend. FastAPI implements the corresponding HTTP API, authentication/RBAC behaviour and demo endpoints, and has a local Compose + shared E2E path; production image publishing and deploy/rollback integration remain separate work.

All changes belong in this canonical repository first. The sibling frontend, backend and deployment repositories are exports maintained through `scripts/export-to-repos.sh`.

## Repository structure
```text
.
├── front-end/
│   ├── react/
│   └── vue/
├── back-end/
│   ├── express/
│   └── fastapi/
├── deployment/
├── docs/
├── scripts/
└── cdis-template.json
```

## Default React + Express stack
Install each application from its own directory with `npm ci`, copy the relevant `.env.example` files to `.env`, start the MySQL service using `deployment/compose/compose.dev.yaml`, apply Express migrations and seed data, then run the Express and React dev servers. See the individual READMEs for exact commands.

## Alternative implementations
- Vue: see `front-end/vue/README.md`. It consumes the same Express API; use it instead of React.
- FastAPI: see `back-end/fastapi/README.md`. Install with `pip install -e ".[dev]"`, configure its environment, run `alembic upgrade head`, then `python -m app.seed` and `uvicorn app.main:app --reload --port 4000`.

To run the Compose stack with FastAPI instead of Express, combine the base file with `deployment/compose/compose.fastapi.yaml`. For Vue, set `FRONTEND_BUILD_CONTEXT=../../front-end/vue` in the Compose environment file.

## Manifest options
- `react` → `front-end/react` (default frontend)
- `vue` → `front-end/vue`
- `express` → `back-end/express` (default backend)
- `fastapi` → `back-end/fastapi`

The CLI integration is developed separately; confirm its manifest schema and compatibility-selection behaviour before treating the current `cdis-template.json` structure as a finalized cross-repository contract.

## Validation
React/Express use the existing CI workflow. Vue and FastAPI have separate validation workflows. Passing unit/build workflows is not by itself proof of cross-backend browser E2E parity; run the shared E2E suite against both backend choices before production use.

## Documentation
- `front-end/react/README.md`
- `front-end/vue/README.md`
- `back-end/express/README.md`
- `back-end/fastapi/README.md`
- `deployment/README.md`
- `docs/START-HERE.md`