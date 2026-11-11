# CDIS Engineering Template

Production-ready full-stack engineering template for building secure, scalable, and maintainable web applications using standardized engineering practices.

**Start here**: [`docs/START-HERE.md`](docs/START-HERE.md) — the full golden path from clone to a first PR, in one place.

This repository is the complete, canonical CDIS template: frontend implementations, backend, deployment, and documentation, all together and kept current. The default frontend is React; an alternative Vue 3 frontend is provided in `front-end-vue/`. The Node.js + Express backend and API contract are shared by both frontends. Three sibling repositories — [`cdis-frontend`](https://github.com/WorkGaurav1/cdis-frontend), [`cdis-backend`](https://github.com/WorkGaurav1/cdis-backend), [`cdis-deployment`](https://github.com/WorkGaurav1/cdis-deployment) — are independently clone/build/run-able exports of this repo's `front-end/`, `back-end/`, and `deployment/` folders. All new work happens here first; those exports are regenerated via `scripts/export-to-repos.sh`.

---

## Features

- React + TypeScript + Vite frontend and alternative Vue 3 + TypeScript + Vite frontend
- Node.js + Express + TypeScript backend
- MySQL via Prisma, with real migrations and idempotent seeding
- Cookie-based auth: JWT access tokens, rotating refresh tokens with reuse detection, CSRF (double-submit), RBAC permissions
- Sign-in and self-registration pages (sign-up can be switched off), an admin role editor, and an initial admin seeded from env vars
- React Hook Form + Zod in React; Zod validation in Vue; Zod DTOs on the backend
- Docker (multi-stage, non-root) for both frontends and backend
- Apache httpd reverse proxy, Docker Compose, deploy/rollback/health-check scripts and migrations
- Unit, integration (real MySQL), and end-to-end (Playwright) testing

---

## Repository Structure

```text
.
├── front-end/          # React application (existing default)
├── front-end-vue/      # Vue 3 alternative frontend
├── back-end/           # Shared Node.js + Express API
├── deployment/         # Docker Compose, reverse proxy, deploy scripts, E2E suite
├── docs/               # Engineering documentation
└── scripts/            # Tooling for this repo
```

## Vue frontend

See [`front-end-vue/README.md`](front-end-vue/README.md) for the stack, local development, and checks. Start it with:

```sh
cd front-end-vue
cp .env.example .env
npm install
npm run dev
```

Point `VITE_API_BASE_URL` at the same Express API used by the React frontend (for example `http://localhost:4000/api/v1`). The backend must allow credentialed CORS requests from the Vue dev-server origin.

## Existing React / backend bootstrap

The original React and Express setup remains unchanged. See [`docs/START-HERE.md`](docs/START-HERE.md) for the complete golden path. The defaults match the dev MySQL database in `deployment/compose/compose.dev.yaml`.

### Build and test

```sh
cd front-end && npm install && npm run build && npm test
cd ../front-end-vue && npm install && npm run lint && npm test && npm run build
cd ../back-end && npm install && npm run build
```

## References

- Vue — https://vuejs.org/
- React — https://react.dev
- Vite — https://vite.dev
- Node.js — https://nodejs.org
- Express — https://expressjs.com
- TypeScript — https://www.typescriptlang.org
- MySQL — https://dev.mysql.com/doc/
- Docker — https://docs.docker.com/
- OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/