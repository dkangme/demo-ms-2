# DEVELOPMENT PLAN: Demo MS 2

## 1. ARCHITECTURE OVERVIEW
The system is a single backend microservice providing a CRUD API for `Cliente` entities (RUT chileno, nombres, apellidos, correo, teléfono). It uses FastAPI, Python 3.11, Firestore as NoSQL database, and runs on Google Cloud Run with Docker containerization. All code follows the SPEC.md contracts exactly: models, validators, Firestore client, service layer, and routers. No frontend exists. The development is split into a foundation layer (models, validators, db), the core service (business logic, endpoints, Dockerfile), and infrastructure (docker-compose, startup, environment). External CI/CD files are not part of this plan as they are not included in SPEC.md §4 file structure.

**Components:**
- **backend/models.py**: Pydantic models (`ClienteBase`, `ClienteCreate`, `ClienteUpdate`, `ClienteResponse`).
- **backend/validators.py**: `validate_rut` function for RUT validation.
- **backend/db.py**: `get_db` function to initialize Firestore client using environment variables.
- **backend/services.py**: `ClienteService` class implementing CRUD with business rules.
- **backend/routers/cliente.py**: FastAPI APIRouter with POST/GET/PUT/DELETE endpoints.
- **backend/main.py**: FastAPI application creation, router inclusion, health endpoint.
- **backend/Dockerfile**: Multi‑stage build, non‑root user, exposes port 8080.
- **start.sh**: Container entry script running Uvicorn.
- **Infrastructure files**: docker-compose.yml, .env.example, .gitignore, README.md.

## 2. ACCEPTANCE CRITERIA
1. All endpoints defined in SPEC.md §3 respond correctly: POST returns 201, GET returns 200, PUT returns 200, DELETE returns 204, with appropriate error codes.
2. RUT validation correctly accepts valid formats and rejects invalid ones (check digit mismatch).
3. Email uniqueness is enforced across all create/update operations (409 on conflict).
4. Firestore operations are performed without errors; documents contain all fields defined in `ClienteResponse`.
5. Docker container starts successfully, health endpoint responds with `{"status":"healthy","service":"demo-ms-2","version":"1.0.0"}`, and all CRUD endpoints work via `docker-compose up`.

## TEAM SCOPE
The project is executed by a single full‑stack developer (handling backend) and a DevOps engineer for infrastructure. The full‑stack developer covers Items 1‑2; DevOps covers Item 3.

## 3. EXECUTABLE ITEMS

### ITEM 1: Foundation — Data models, RUT validation, and Firestore client initialization
**Goal:** Provide the shared Python modules that Item 2 (the service) will import: Pydantic models for Cliente, the RUT validator, and a Firestore connection factory.

**Files to create:**
- backend/models.py (create) — `ClienteBase`, `ClienteCreate`, `ClienteUpdate`, `ClienteResponse` with field descriptions, examples, and Firestore timestamp handling.
- backend/validators.py (create) — `validate_rut(rut: str) -> bool` function implementing format normalization, body/digit extraction, and check digit verification.
- backend/db.py (create) — `get_db() -> google.cloud.firestore.Client` that reads `GCP_PROJECT` and optional `GOOGLE_APPLICATION_CREDENTIALS` from environment, raises `EnvironmentError` if missing, returns a Firestore client.

**Dependencies:** None

**Validation:**
- Run `python -c "from backend.models import ClienteBase; print(ClienteBase(rut='12.345.678-9', nombres='Juan', apellidos='Pérez', correo='juan@example.com', telefono='+56912345678'))"`; no import or model errors.
- Run `python -c "from backend.validators import validate_rut; assert validate_rut('12.345.678-9'); assert not validate_rut('12.345.678-0')"` inside container.
- `backend/db.py` is importable (Firestore init will fail without GCP credentials locally, but the logic is testable via mock or emulator).

**Role:** role-fe-be (backend_developer)

---

### ITEM 2: Backend Service — Service layer, API router, application entrypoint, Dockerfile, and dependencies
**Goal:** Implement the complete CRUD business logic, FastAPI endpoints, and containerisation for the microservice.

**Files to create:**
- backend/services.py (create) — `ClienteService` class with async methods: `create`, `get_by_id`, `list_all`, `update`, `delete`. Uses Firestore client from `db.get_db()`, validates RUT and email uniqueness, converts documents to `ClienteResponse`.
- backend/routers/cliente.py (create) — APIRouter with endpoints:
  - `POST /clientes` → `create_cliente`
  - `GET /clientes` → `list_clientes`
  - `GET /clientes/{cliente_id}` → `get_cliente`
  - `PUT /clientes/{cliente_id}` → `update_cliente`
  - `DELETE /clientes/{cliente_id}` → `delete_cliente`
- backend/main.py (create) — FastAPI application instance `app`, includes router, adds root health endpoint `GET /health` returning `{"status":"healthy","service":"demo-ms-2","version":"1.0.0"}`, configures CORS (if needed).
- backend/requirements.txt (create) — pinned versions: `fastapi==0.115.6`, `uvicorn==0.34.0`, `pydantic==2.10.4`, `email-validator==2.2.0`, `google-cloud-firestore==2.19.0`, `firebase-admin==6.5.0`.
- backend/Dockerfile (create) — multi‑stage build: builder stage installs dependencies, runtime stage uses `python:3.11-slim-bookworm`, copies `backend/`, runs `pip install --no-cache-dir -r requirements.txt`, creates non‑root user, `EXPOSE 8080`, `CMD ["sh", "/app/start.sh"]`. Build context is `./backend`; works with `COPY . /app`.
- Infrastructure files for container start: `start.sh` is created here (root level) as the script the Docker image runs. It contains `uvicorn main:app --host 0.0.0.0 --port 8080`.

**Dependencies:** Item 1 (models, validators, db)

**Validation:**
- Build Docker image: `docker build -t demo-ms-2-backend ./backend` (no errors).
- Run container with environment variables set: `docker run --rm -e GCP_PROJECT=test -e FIRESTORE_COLLECTION=clientes -p 8080:8080 demo-ms-2-backend`; health endpoint responds with `{"status":"healthy",...}`.
- Use `curl` to test CRUD endpoints (requires Firestore emulator or real project) — at minimum, confirm the container starts and the health endpoint works.

**Role:** role-fe-be (backend_developer)

---

### ITEM 3: Infrastructure & Deployment — Local orchestration, environment configuration, and documentation
**Goal:** Provide all files necessary to run the entire project locally with a single command, including service orchestration, environment template, and documentation.

**Files to create:**
- docker-compose.yml (create) — defines one service `backend` using `build: ./backend`, maps port 8080:8080, sets environment variables from `.env`, provides a healthcheck calling `http://localhost:8080/health` (or uses curl), and declares `depends_on` with a condition if any external dependencies (none, so omitted).
- .env.example (create) — documents all required variables: `GCP_PROJECT`, `FIRESTORE_COLLECTION`, optional `GOOGLE_APPLICATION_CREDENTIALS`, `APP_PORT` (default 8080).
- .gitignore (create) — excludes `.env`, `__pycache__/`, `*.pyc`, `venv/`, `.idea/`, `dist/`, `*.egg-info/`.
- README.md (create) — includes project description, prerequisites (Docker, Docker Compose), quick start (`cp .env.example .env`, `docker-compose up`), endpoint documentation, and health check instructions.

**Dependencies:** Item 2 (backend image/Dockerfile)

**Validation:**
- Run `docker-compose up` from project root; service starts, health check passes, and `docker-compose exec backend curl http://localhost:8080/health` returns `200`.
- `curl` to any endpoint (e.g., `POST /clientes`) using the exposed port.
- Complete zero‑manual‑steps process: clone → `cp .env.example .env` → edit env vars → `docker-compose up` → service is ready.

**Role:** role-devops (devops_support)