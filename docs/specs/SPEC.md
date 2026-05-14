# SPEC.md

## 1. TECHNOLOGY STACK
- **Runtime:** Python 3.11.6
- **Web framework:** FastAPI 0.115.6
- **ASGI server:** Uvicorn 0.34.0
- **Data validation & serialization:** Pydantic 2.10.4 (with EmailStr via email-validator 2.2.0)
- **Firestore client:** google-cloud-firestore 2.19.0
- **Firebase Admin SDK:** firebase-admin 6.5.0 (for Firestore initialization and authentication)
- **Container base image:** python:3.11-slim-bookworm
- **CI/CD:** GitHub Actions using google-github-actions/deploy-cloudrun@v2
- **Deployment target:** Google Cloud Run (fully managed, serverless)
- **Local development:** docker-compose 3.8

## 2. DATA CONTRACTS
All models are defined using Pydantic and are located in `backend/models.py`. Field names are in Spanish exactly as specified. Firestore document structure mirrors the Pydantic response model.

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ClienteBase(BaseModel):
    rut: str = Field(..., description="RUT chileno con formato XX.XXX.XXX-X", example="12.345.678-9")
    nombres: str = Field(..., min_length=1, max_length=100, example="Juan")
    apellidos: str = Field(..., min_length=1, max_length=100, example="Pérez")
    correo: EmailStr = Field(..., example="juan@example.com")
    telefono: str = Field(..., min_length=9, max_length=15, example="+56912345678")

class ClienteCreate(ClienteBase):
    """Modelo para creación de cliente. No incluye id ni timestamps."""
    pass

class ClienteUpdate(BaseModel):
    """Modelo para actualización parcial. Todos los campos son opcionales."""
    rut: Optional[str] = Field(None, example="12.345.678-9")
    nombres: Optional[str] = Field(None, example="Juan")
    apellidos: Optional[str] = Field(None, example="Pérez")
    correo: Optional[EmailStr] = Field(None, example="nuevo@example.com")
    telefono: Optional[str] = Field(None, example="+56987654321")

class ClienteResponse(ClienteBase):
    """Modelo de respuesta. Incluye id y timestamps generados por el servidor."""
    id: str = Field(..., example="abc123def456")
    created_at: datetime
    updated_at: datetime

# Firestore document shape (JSON):
# {
#   "id": "auto‑generated",
#   "rut": "12.345.678-9",
#   "nombres": "Juan",
#   "apellidos": "Pérez",
#   "correo": "juan@example.com",
#   "telefono": "+56912345678",
#   "created_at": "2025-01-01T12:00:00Z",
#   "updated_at": "2025-01-01T12:00:00Z"
# }
```

## 3. API ENDPOINTS
Base path: `/clientes`

### 3.1 Crear cliente
```
POST /clientes
Request body: ClienteCreate
Response:     ClienteResponse (201 Created)
Errors:       409 Conflict (email ya registrado)
              422 Unprocessable Entity (validación de RUT o formato de datos)
```

### 3.2 Listar todos los clientes
```
GET /clientes
Query params: skip (int, default 0), limit (int, default 100)
Response:     List[ClienteResponse] (200 OK)
```

### 3.3 Obtener cliente por ID
```
GET /clientes/{cliente_id}
Path param:   cliente_id (str)
Response:     ClienteResponse (200 OK)
Errors:       404 Not Found
```

### 3.4 Actualizar cliente
```
PUT /clientes/{cliente_id}
Path param:   cliente_id (str)
Request body: ClienteUpdate
Response:     ClienteResponse (200 OK)
Errors:       404 Not Found
              422 Unprocessable Entity
              409 Conflict (si se intenta cambiar email a uno ya existente)
```

### 3.5 Eliminar cliente
```
DELETE /clientes/{cliente_id}
Path param:   cliente_id (str)
Response:     204 No Content
Errors:       404 Not Found
```

All endpoints return JSON with the exact field names defined in `ClienteResponse`. Error responses follow the standard FastAPI format: `{"detail": "mensaje"}`.

## 4. FILE STRUCTURE
Complete project tree with one-line descriptions.

```
.
├── docker-compose.yml          # Servicio backend + posible instancia de Firestore emulator
├── start.sh                    # Script de entrada para el contenedor: ejecuta uvicorn
├── .env.example                # Plantilla con variables de entorno requeridas
├── .gitignore                  # Excluye .env, __pycache__, venv, etc.
├── README.md                   # Instrucciones de despliegue y ejecución
└── backend/
    ├── Dockerfile              # Imagen Docker para Cloud Run (python:3.11-slim)
    ├── main.py                 # Punto de entrada de FastAPI, crea app e incluye router
    ├── requirements.txt        # Dependencias Python congeladas
    ├── models.py               # Modelos Pydantic: ClienteBase, ClienteCreate, ClienteUpdate, ClienteResponse
    ├── validators.py           # Función validate_rut: valida formato y dígito verificador del RUT chileno
    ├── db.py                   # Inicialización del cliente Firestore: función get_db()
    ├── services.py             # Clase ClienteService: lógica CRUD con validaciones y acceso a Firestore
    └── routers/
        └── cliente.py          # APIRouter con los endpoints CRUD de /clientes
```

### PORT TABLE
| Service | Listening Port | Path        |
|---------|----------------|-------------|
| backend | 8080           | backend/    |

- **Dockerfile EXPOSE:** `EXPOSE 8080`
- **Uvicorn command:** `uvicorn main:app --host 0.0.0.0 --port 8080`

### SHARED MODULES
No shared modules exist; this is a single microservice.

## 5. ENVIRONMENT VARIABLES
All must be defined in the execution environment. An `.env.example` file is provided with placeholders.

| Variable                        | Type   | Description                                                    | Example value            |
|---------------------------------|--------|----------------------------------------------------------------|--------------------------|
| GCP_PROJECT                     | string | ID del proyecto de GCP donde reside Firestore                  | my-gcp-project           |
| FIRESTORE_COLLECTION            | string | Nombre de la colección en Firestore                           | clientes                 |
| GOOGLE_APPLICATION_CREDENTIALS  | string | (Opcional) Ruta al archivo JSON de cuenta de servicio. Solo para desarrollo local; en Cloud Run se omite y se usa la cuenta de servicio por defecto. | /secrets/sa_key.json     |
| APP_PORT                        | int    | Puerto en el que escucha Uvicorn (opcional, por defecto 8080) | 8080                     |

**Nota:** En Cloud Run, `GCP_PROJECT` se puede obtener automáticamente; si no se define, se infiere del contexto de ejecución, pero se recomienda definirlo explícitamente.

## 6. IMPORT CONTRACTS
Every foundation file exports exactly the following symbols.

### `backend/models.py`
```
from backend.models import ClienteBase, ClienteCreate, ClienteUpdate, ClienteResponse
```

### `backend/validators.py`
```
from backend.validators import validate_rut
# signature: validate_rut(rut: str) -> bool
# Returns True if RUT is syntactically valid and the check digit matches.
```

### `backend/db.py`
```
from backend.db import get_db
# signature: get_db() -> google.cloud.firestore.Client
# Initializes and returns a thread‑safe Firestore client using the GOOGLE_APPLICATION_CREDENTIALS env var or the default service account.
```

### `backend/services.py`
```
from backend.services import ClienteService
# ClienteService(db: google.cloud.firestore.Client)
# Methods:
#   async create(data: ClienteCreate) -> ClienteResponse
#   async get_by_id(cliente_id: str) -> ClienteResponse
#   async list_all(skip: int, limit: int) -> List[ClienteResponse]
#   async update(cliente_id: str, data: ClienteUpdate) -> ClienteResponse
#   async delete(cliente_id: str) -> None
# Internally validates RUT and email uniqueness before write operations.
```

### `backend/routers/cliente.py`
```
from backend.routers.cliente import router
# APIRouter instance with all endpoints mounted at prefix="/clientes"
```

### `backend/main.py`
```
from backend.main import app
# FastAPI application instance. Includes router and root health endpoint.
```

## 7. FRONTEND STATE & COMPONENT CONTRACTS
Not applicable — this project has no frontend. The API is consumed directly by external clients.

## 8. FILE EXTENSION CONVENTION
- **Backend files:** All Python files use the `.py` extension. No JavaScript or TypeScript files exist in the repository.
- **Project language:** Python 3.11 (only).
- **Entry point:** `backend/main.py` is executed by Uvicorn as specified in `start.sh`. There is no `index.html` or frontend build artefact. The script that starts the server is `uvicorn main:app --host 0.0.0.0 --port 8080`, located in the `backend/` directory and invoked from the container’s `WORKDIR /app/backend`.