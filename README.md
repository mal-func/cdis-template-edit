# CDIS Engineering Template

Canonical full-stack template with selectable frontend and backend implementations.

- **Default frontend:** React + TypeScript + Vite at `front-end/react/`
- **Alternative frontend:** Vue 3 + TypeScript + Vite at `front-end/vue/`
- **Default backend:** Express + TypeScript at `back-end/express/`
- **Alternative backend:** FastAPI + Python at `back-end/fastapi/`

React and Vue are intended to consume the same API contract. Express is the established, production-integrated backend. FastAPI implements the corresponding HTTP API, authentication/RBAC behaviour and demo endpoints. The template now declares stack-specific production image, Compose and deploy/rollback paths for Vue and FastAPI; these must pass repository CI checks before live use.

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

The CLI reads `cdis-template.json` to select frontend/backend directories, shared components and developer tooling. `files.include` also includes the generated-project CI workflow. The compatibility map declares the frontend/backend combinations validated by maintainers.

### Linter and formatter choices

- React, Vue and Express support **ESLint or Biome**. ESLint is the default; the CLI prompts when no explicit choice is supplied.
- FastAPI uses **Ruff** as its single declared linter, so there is no redundant linter prompt.
- Biome's Vue single-file-component support is experimental; the CLI labels that option accordingly.
- Prettier and Ruff formatting are optional additions. They do not replace linting and are disabled unless selected.
- The manifest is the source of truth for supported options and defaults.

### Generated-project CI

The manifest includes `.github/workflows/cdis-generated.yml`. The CLI copies this workflow into newly generated projects so CI validates the selected frontend and backend layout. The template repository's monorepo workflows are not copied into generated projects.
## Using this repository with the CDIS CLI

The CLI uses this repository as its default template source. Its source repository and default branch are configurable in the CLI through the `CDIS_TEMPLATE_REPOSITORY` and `CDIS_TEMPLATE_BRANCH` environment variables. This lets maintainers point the CLI at a transferred repository or a fork without changing the template manifest or scattering repository URLs through the CLI code.

The CLI continues to support both branch-based generation and published Git tags. With no explicit ref option, it uses the configured default branch; `--version <tag>` selects a published template tag.

## Validation
React/Express use the existing CI workflow. Vue and FastAPI have separate validation workflows. Passing unit/build workflows is not by itself proof of cross-backend browser E2E parity; run the shared E2E suite against both backend choices before production use.

## Documentation
- `front-end/react/README.md`
- `front-end/vue/README.md`
- `back-end/express/README.md`
- `back-end/fastapi/README.md`
- `deployment/README.md`
- `docs/START-HERE.md`