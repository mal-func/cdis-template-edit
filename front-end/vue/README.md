# CDIS Vue frontend

This is the Vue 3 + TypeScript alternative frontend for the CDIS engineering template. It consumes the same Express API as `front-end/react/`; it does not introduce a second backend or change the API contract.

## Stack

- Vue 3, TypeScript, Vite and Vue Router
- Pinia for session state
- TanStack Vue Query for server state and cache invalidation
- Axios with cookie credentials, CSRF headers and coordinated refresh-token rotation
- Zod for client-side form validation
- ECharts for graphs and charts
- Leaflet for the India district maps

## Local development

```sh
cp .env.example .env
npm install
npm run dev
```

Set `VITE_API_BASE_URL` to the Express API base URL (including its `/api/v1` prefix). The backend must allow credentialed CORS requests from the Vite origin.

## Docker / Compose

The Vue Dockerfile serves the built SPA through Nginx. To use it with the existing local Compose stack, set the build-context override in `deployment/compose/.env`:

```dotenv
FRONTEND_BUILD_CONTEXT=../../front-end/vue
```

Then build and start the same Compose services from the repository root:

```sh
docker compose -f deployment/compose/compose.yaml build frontend
docker compose -f deployment/compose/compose.yaml up -d
```

The existing Apache reverse proxy and Express backend remain unchanged.

## Checks

```sh
npm run lint
npm test
npm run build
```

The Vue app deliberately shares API endpoints and the backend's cookie-based authentication model with the React frontend. Access control in the router and UI is a usability layer; the Express backend remains the security boundary and must enforce permissions itself.

## Feature coverage

The Vue app includes login/registration, session restoration, silent refresh, permission-gated routes, dashboard map visualizations, charts, graphs, searchable/sortable/paginated tables, user listing/role assignment and account settings. The included unit tests cover form schemas, permission checks and map tier/color helpers. Component, integration and browser E2E parity still need to be added and run before calling the two frontends fully verified equivalents.