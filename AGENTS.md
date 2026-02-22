# AGENTS.md

## 1. Project Overview

- **EduStart** is an adaptive learning platform for children (ages 4–10), supporting reading, counting, and cognitive modules with gamified progress tracking and AI-powered recommendations.
- Two user roles exist: **parent** (manages children profiles, views progress) and **educator** (creates/manages learning modules and questions).
- High-level architecture: FastAPI (Python) REST backend + React (TypeScript) SPA frontend within a single monorepo.
- Frontend communicates with backend via a custom `fetch`-based HTTP client (`ui/src/api/client.ts`) targeting `/api/v1` endpoints, authenticated with Bearer JWT tokens stored in `localStorage`.
- In development, Vite proxies `/api` to the backend at `localhost:8000`. In Docker, nginx reverse-proxies both services on port 8080.

---

## 2. Tech Stack

### Backend (`/app`)
- **Python** 3.11 (per Dockerfile)
- **FastAPI** 0.109.0 with Uvicorn ASGI server
- **Pydantic** v2 for request/response validation; `pydantic-settings` for configuration
- **Database**: Supabase (hosted PostgreSQL) via `supabase-py` client — no ORM; direct table queries through Supabase REST API with Row-Level Security (RLS)
- **Auth**: Supabase Auth (sign-up, sign-in, token refresh) + JWT verification via `python-jose`; passwords hashed with `passlib[bcrypt]`
- **ML/AI**: TensorFlow, scikit-learn, numpy, pandas for adaptive learning models (`app/ml/`)
- **Rate limiting**: `slowapi`
- **Caching**: Redis (`redis` + `hiredis`) — configured but optional
- **Monitoring**: Sentry SDK (optional, via `SENTRY_DSN`)
- **Other**: `httpx`, `python-dateutil`, `python-dotenv`, `python-json-logger`

### Frontend (`/ui`)
- **React** 19.2.0 with TypeScript 5.9
- **Routing**: `react-router-dom` v7
- **State management**: React Context API (`AuthContext`) + local `useState`/`useEffect` — no external state library
- **HTTP client**: Native `fetch` wrapped in a custom typed client (`api/client.ts`) — no axios
- **Build tool**: Vite 7.2
- **Testing**: Vitest 3 with jsdom

### Infrastructure
- **Docker**: Python 3.11-slim (backend), Node 20-slim (frontend), nginx:alpine (reverse proxy)
- **Docker Compose**: 3 services — `api`, `ui`, `proxy` (nginx on port 8080)
- **CI/CD**: 3 GitHub Actions workflows:
  - `node.js.yml` — UI build & test (Node 18/20/22 matrix)
  - `python.yml` — Backend pytest (Python 3.10/3.11 matrix)
  - `deploy-pages.yml` — Deploy UI to GitHub Pages (on push to `ui/` path on `main`)
- **Environment**: `.env` file loaded by `pydantic-settings`; `.env.example` provided; `VITE_API_BASE_URL` for frontend API base

### Testing
- **Backend**: pytest + pytest-asyncio + httpx `AsyncClient` (ASGI transport); pytest-mock for mocking; pytest-cov for coverage
- **Frontend**: Vitest with jsdom environment, `vi` for mocking

---

## 3. Directory Structure

### Root (`/`)
| Directory/File | Purpose |
|---|---|
| `app/` | Python FastAPI backend application |
| `ui/` | React TypeScript frontend application |
| `tests/` | Backend test suite (pytest) |
| `scripts/` | Shell scripts for dev setup, deployment, migrations, linting |
| `nginx/` | Nginx reverse proxy configuration |
| `logs/` | Application log files (gitignored) |
| `Dockerfile` | Backend Docker image |
| `docker-compose.yml` | Multi-service orchestration |
| `Makefile` | Developer convenience commands |
| `requirements.txt` | Backend production dependencies |
| `requirements-dev.txt` | Backend dev/test dependencies |
| `.env.example` | Environment variable template |
| `.github/workflows/` | CI/CD pipeline definitions |

### `/app` — Backend

#### `main.py` — Application entry point
- Creates the `FastAPI` instance with lifespan, CORS, exception handlers
- Mounts the versioned API router at `/api/v1`
- Serves the React SPA from `ui/dist` in production (catch-all route)
- **What belongs**: Only application bootstrap/config. No routes or business logic.

#### `api/` — API layer
- `api/v1/router.py` — Central router that includes all endpoint sub-routers
- `api/v1/endpoints/` — One file per domain:
  - `auth.py` — Registration, login, logout, token refresh, privacy policy
  - `children.py` — Child profile CRUD
  - `modules.py` — Learning module CRUD and listing
  - `progress.py` — Learning progress tracking and reports
  - `recommendations.py` — AI-powered module recommendations
- `api/v1/analytics.py` — Analytics event ingestion
- **What belongs**: Route definitions, request handling, input validation delegation, response mapping. Routes must delegate business logic to services.
- **What must NOT go here**: Direct database queries, complex business logic, ML model calls.

#### `core/` — Core infrastructure
- `config.py` — `Settings` class via `pydantic-settings` (env-based); cached via `@lru_cache`
- `security.py` — JWT creation/verification, password hashing (bcrypt)
- `supabase_client.py` — Singleton Supabase client factory
- `errors.py` — Custom exception hierarchy (`EduStartException` base) and global exception handlers
- **What belongs**: Cross-cutting framework-level concerns. No domain logic.

#### `models/` — Data models
- Pydantic `BaseModel` classes representing database table schemas
- Each file also contains SQL DDL as reference strings (table schemas, RLS policies, indexes)
- Files: `user.py`, `child.py`, `module.py`, `progress.py`, `analytics.py`
- **What belongs**: Database record shapes and schema documentation. These are NOT ORM models — Supabase is used directly.
- **What must NOT go here**: Request/response shapes (those go in `schemas/`), business logic.

#### `schemas/` — Request/Response schemas
- Pydantic models for API input validation and output serialization
- Files: `user.py`, `child.py`, `module.py`, `progress.py`, `analytics.py`, `recommendation.py`
- **What belongs**: API contract definitions — request bodies, response shapes, query parameter types.
- **What must NOT go here**: Database record shapes (those go in `models/`).

#### `services/` — Business logic layer
- Class-based services that encapsulate domain operations
- Each service gets a Supabase client in `__init__` and exposes `async` methods
- Files: `auth_service.py`, `child_service.py`, `module_service.py`, `progress_service.py`, `ai_service.py`
- **What belongs**: All business logic, data transformation, Supabase queries, orchestration.
- **What must NOT go here**: HTTP/request concerns, route decorators.

#### `utils/` — Utility modules
- `logger.py` — Logging setup with console handler and third-party noise suppression
- `validators.py` — Reusable validation functions (email, password strength, age, dates)
- **What belongs**: Pure utility functions reusable across the application.

#### `ml/` — Machine learning subsystem
- `adaptive_model.py` — Adaptive difficulty model
- `recommendation_engine.py` — Content recommendation engine
- `models/` — Directory for saved ML model artifacts
- **What belongs**: ML model definitions, training logic, prediction pipelines.

#### `dependencies.py` — FastAPI dependency injection
- `get_current_user` — Extracts and validates JWT from `Authorization: Bearer` header via Supabase
- `get_current_parent`, `get_current_educator` — Role-based access control dependencies
- `get_pagination_params` — Standard pagination with max limit of 100

### `/ui` — Frontend

#### `src/main.tsx` — React entry point
- Renders `<App />` into the DOM root.

#### `src/App.tsx` — Application shell with routing
- Wraps everything in `<AuthProvider>` then `<BrowserRouter>`
- Defines all routes: public, protected (via `<RequireAuth>`), and educator-only (via `<EducatorRoute>`)

#### `src/api/` — API client layer
- `client.ts` — Core `fetch` wrapper with token management (`tokenStorage`), generic typed `request<T>()`, and `api` object (`get`, `post`, `put`, `delete`)
- `auth.ts` — Auth API functions + TypeScript interfaces (`User`, `TokenResponse`, etc.)
- `modules.ts` — Module CRUD API + transforms (backend `type` → frontend `module_type`)
- `children.ts` — Child profile API
- `progress.ts` — Progress/reports API
- `analytics.ts` — Analytics event API
- `client.test.ts` — Unit tests for tokenStorage and ApiError
- **What belongs**: All HTTP communication. Each domain gets its own file exporting a typed API object.
- **What must NOT go here**: UI components, business logic unrelated to API calls.

#### `src/context/` — React Context providers
- `AuthContext.tsx` — Provides `user`, `isAuthenticated`, `login`, `logout`, `register`, `refreshUser`; includes `RequireAuth` wrapper component
- **What belongs**: Global application state shared across components.

#### `src/components/` — Shared/reusable components
- `Button.tsx` + `Button.css` — Reusable button with variant styling
- `Card.tsx` + `Card.css` — Reusable card container
- `EducatorRoute.tsx` — Route guard for educator role (also exports `ParentRoute`)
- **What belongs**: Domain-agnostic, reusable UI components used across pages.
- **What must NOT go here**: Page-level components, API calls.

#### `src/pages/` — Page components (route-level)
- Top-level pages: `Landing`, `Login`, `Register`, `Dashboard`, `ModuleList`, `LearningModule`, `StudentLogin`, `SelectProfile`, `PrivacyPolicy`
- `pages/teacher/` — Educator-only pages: `TeacherDashboard`, `ModuleEditor`
- `pages/questions/` — Question type components: `MatchQuestion`
- Each page has a co-located `.css` file
- **What belongs**: Full-page components tied to routes. Each page handles its own data fetching and local state.

#### `src/assets/` — Static assets (images, fonts, etc.)

---

## 4. Architecture & Design Patterns

### Backend Architecture
- **Pattern**: Modular layered architecture (not app-factory; single `FastAPI` instance in `main.py`)
- **Layering** (strict top-down dependency):
  ```
  Endpoints (api/v1/endpoints/) → Services (services/) → Supabase Client (core/)
       ↓                              ↓                        ↓
  Schemas (schemas/)            Models (models/)          Config (core/config.py)
  ```
- Routes handle HTTP concerns (status codes, response models) and delegate to service classes
- Services contain all business logic and database access via Supabase client
- Models define data shapes; schemas define API contracts — they are deliberately separate

### API Style
- **REST/JSON** under `/api/v1` prefix
- Versioned API (`v1`) with sub-routers per domain
- Consistent JSON error format: `{ "error": { "code": "...", "message": "..." } }`
- Auth: Supabase-issued JWT Bearer tokens in `Authorization` header
- Pagination: `skip`/`limit` query parameters (max 100)

### Frontend Architecture
- **Pattern**: Page-based React SPA with Context-driven auth state
- Routing via `react-router-dom` v7 with declarative route definitions in `App.tsx`
- State: `AuthContext` for global auth; local `useState`/`useEffect` per page for data
- No centralized store (no Redux, Zustand, etc.)
- Data fetching: Imperative `useEffect` → `api.*()` calls → `setState` (no React Query/SWR)

### Dependency Direction
- Frontend → Backend: UI calls `/api/v1/*` endpoints via the `api` client
- Backend layers: Endpoints → Services → Supabase (unidirectional; no circular dependencies)
- Schemas and models are leaf nodes — they do not import from services or endpoints

### Architectural Constraints
- Backend SPA serving: In production, `main.py` serves `ui/dist` via catch-all route — API routes are mounted BEFORE the SPA catch-all
- Supabase RLS: Database tables have Row-Level Security policies — backend queries must respect them
- Auth flow: Supabase handles user creation and token issuance; backend verifies tokens via `supabase.auth.get_user(token)`

---

## 5. Code Conventions

### Backend (Python)
- **Naming**: `snake_case` for files, functions, variables; `PascalCase` for classes
- **File naming**: One module per domain concept (e.g., `auth_service.py`, `module.py`)
- **Error handling**: Custom exception hierarchy in `core/errors.py`; endpoints catch `ValueError` for user errors and generic `Exception` for server errors; structured JSON responses
- **Logging**: Python `logging` module with per-module loggers (`logging.getLogger(__name__)`); format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Config**: All config via environment variables loaded through `pydantic-settings` `Settings` class in `core/config.py`; accessed via module-level `settings` singleton
- **Type hints**: Used consistently on function signatures and return types
- **Async**: All endpoint and service methods are `async def`

### Frontend (TypeScript)
- **Naming**: `PascalCase` for components/files; `camelCase` for functions/variables; `SCREAMING_SNAKE_CASE` for constants
- **File naming**: Component files match component name (e.g., `Dashboard.tsx`); API files are lowercase domain names (e.g., `auth.ts`)
- **CSS**: Co-located CSS files per page/component (e.g., `Dashboard.css` alongside `Dashboard.tsx`)
- **Exports**: Named exports (not default) for pages and components; object exports for API modules (`authApi`, `modulesApi`)
- **Type definitions**: TypeScript interfaces defined in the API layer files, co-located with their API functions
- **Error handling**: `ApiError` class in `client.ts`; caught in components via try/catch

---

## 6. Testing Strategy

### Backend (`/tests`)
- **Framework**: pytest + pytest-asyncio
- **Structure**: Mirrors `app/api/v1/endpoints/` — one test file per endpoint module:
  - `tests/test_main.py` — Health check and root endpoint tests
  - `tests/api/v1/test_auth.py` — Auth endpoint tests
  - `tests/api/v1/test_children.py` — Children endpoint tests
  - `tests/api/v1/test_modules.py` — Module endpoint tests
  - `tests/api/v1/test_progress.py` — Progress endpoint tests
  - `tests/api/v1/test_recommendations.py` — Recommendation endpoint tests
- **Fixtures**: `conftest.py` provides `mock_user`, `mock_supabase`, `override_get_current_user`, `client` (sync), `async_client` (async)
- **Mocking**: FastAPI dependency overrides (`app.dependency_overrides`) for auth; `unittest.mock.patch` for Supabase client
- **Test client**: `httpx.AsyncClient` with `ASGITransport` for async tests; `fastapi.testclient.TestClient` for sync tests
- **CI**: Runs `pytest -v` on Python 3.10 and 3.11

### Frontend (`/ui`)
- **Framework**: Vitest 3 with jsdom environment
- **Structure**: Test files co-located with source (e.g., `api/client.test.ts`)
- **Coverage**: Tests exist for API client utilities (`tokenStorage`, `ApiError`)
- **CI**: Runs `npm test` on Node 18, 20, and 22

---

## 7. Agent Rules (CRITICAL)

### Backend Rules
- **New routes** MUST be added as an endpoint file in `app/api/v1/endpoints/` and registered in `app/api/v1/router.py` with an appropriate prefix and tag
- **Business logic** MUST reside in `app/services/`. Endpoint functions must only handle HTTP concerns (parsing, status codes, response mapping) and delegate to service methods
- **Database access** MUST go through the Supabase client obtained via `get_supabase_client()`. Do NOT use raw SQL or SQLAlchemy sessions — the ORM dependencies in `requirements.txt` are unused legacy entries
- **New models** go in `app/models/` (database shapes); new API contracts go in `app/schemas/` (request/response shapes). Do NOT mix these
- **Configuration** MUST be added as fields in `app/core/config.py` `Settings` class and documented in `.env.example`
- **Error handling** MUST use the custom exception hierarchy in `app/core/errors.py` for domain errors; endpoints catch and convert to HTTP responses
- **Auth-protected routes** MUST use `Depends(get_current_user)`, `Depends(get_current_parent)`, or `Depends(get_current_educator)` from `app/dependencies.py`
- **All service/endpoint methods** MUST be `async def`

### Frontend Rules
- **New pages** MUST be added in `ui/src/pages/` and registered as a `<Route>` in `App.tsx`
- **Educator-only pages** MUST be nested inside the `/teacher/*` route wrapped by `<EducatorRoute>`
- **Protected pages** MUST be wrapped with `<RequireAuth>` in `App.tsx`
- **API calls** MUST go through the typed API client in `ui/src/api/client.ts` — never use raw `fetch` directly in components
- **New API domains** MUST get their own file in `ui/src/api/` exporting a typed API object (following the pattern of `authApi`, `modulesApi`, etc.)
- **State management**: Use `AuthContext` for auth state. For other global state, create new contexts in `ui/src/context/`. Do NOT introduce Redux or other state libraries without explicit justification
- **CSS**: Co-locate CSS files with their component/page. Use vanilla CSS — no CSS-in-JS, no Tailwind
- **TypeScript interfaces** for API responses MUST be defined in the corresponding `ui/src/api/*.ts` file

### Global Rules
- **Do NOT break the layering**: Endpoints → Services → Database. No shortcuts (e.g., no direct Supabase calls from endpoint files)
- **Do NOT modify SQL migration files** in `scripts/` unless adding a new migration
- **Always update or add tests** when changing business logic in services or API behavior
- **Do NOT introduce new dependencies** (Python or npm) unless explicitly justified — the stack is intentionally minimal
- **Environment variables** must be added to both `app/core/config.py` (backend) and `.env.example`; frontend env vars must use `VITE_` prefix
- **Do NOT hardcode URLs, secrets, or credentials** — all must come from configuration
- **API versioning**: All new endpoints must be under `/api/v1`. Do NOT create `/api/v2` without explicit decision
- **Do NOT modify `main.py`** SPA serving logic unless changing deployment strategy
- **Keep the models/schemas separation**: Models = database record shapes; Schemas = API request/response shapes
