# Demo MS 2

Microservicio demo para gestión de clientes (CRUD). Construido con Python 3.11 / FastAPI, Firestore como base de datos y desplegable en Google Cloud Run. El proyecto sirve como plantilla para futuros microservicios serverless.

## Funcionalidades

- CRUD completo sobre la entidad `Cliente` (rut, nombres, apellidos, correo, teléfono).
- Validación de RUT chileno (formato y dígito verificador).
- Verificación de unicidad de correo electrónico.
- Health check endpoint para monitoreo.
- Contenedorizado con Docker y orquestado localmente con Docker Compose.

## Prerrequisitos

- Docker y Docker Compose instalados.
- Proyecto en Google Cloud con Firestore habilitado (modo nativo).
- (Opcional) Cuenta de servicio de GCP con permisos sobre Firestore para desarrollo local.

## Estructura del proyecto

```
.
├── docker-compose.yml
├── .env.example
├── .gitignore
├── run.sh
├── README.md
└── backend/
    ├── Dockerfile
    ├── main.py
    ├── models.py
    ├── validators.py
    ├── db.py
    ├── services.py
    ├── requirements.txt
    └── routers/
        └── cliente.py
```

## Inicio rápido (local)

1. Clonar el repositorio y posicionarse en la raíz.
2. Copiar `.env.example` a `.env` y editar las variables:
   ```bash
   cp .env.example .env
   # Ajustar GCP_PROJECT y opcionalmente GOOGLE_APPLICATION_CREDENTIALS
   ```
3. Ejecutar el script de arranque:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   O, manualmente:
   ```bash
   docker-compose up --build -d
   ```
4. Verificar que el servicio está corriendo:
   ```bash
   curl http://localhost:8080/health
   ```

## Variables de entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|--------|
| `GCP_PROJECT` | ID del proyecto de Google Cloud | `my-project` |
| `FIRESTORE_COLLECTION` | Nombre de la colección en Firestore (default: `clientes`) | `clientes` |
| `GOOGLE_APPLICATION_CREDENTIALS` | (Opcional) Ruta al JSON de la cuenta de servicio | `/secrets/key.json` |
| `APP_PORT` | Puerto de escucha (default: `8080`) | `8080` |

## Endpoints de la API

Todos los endpoints están bajo el prefijo `/clientes`.

### Crear cliente
`POST /clientes`  
**Body:** JSON con `rut`, `nombres`, `apellidos`, `correo`, `telefono`.  
**Respuesta:** `201 Created` con los datos completos (incluyendo `id`, `created_at`, `updated_at`).  
**Errores:** `409` si el correo ya existe, `422` si el RUT es inválido o los datos no pasan validación.

### Listar clientes
`GET /clientes`  
**Query params:** `skip` (default `0`), `limit` (default `100`).  
**Respuesta:** `200 OK` con array de objetos cliente.

### Obtener cliente por ID
`GET /clientes/{cliente_id}`  
**Respuesta:** `200 OK` con el objeto cliente.  
**Error:** `404` si no existe.

### Actualizar cliente
`PUT /clientes/{cliente_id}`  
**Body:** JSON con los campos a modificar (todos opcionales).  
**Respuesta:** `200 OK` con los datos actualizados.  
**Errores:** `404`, `409` (correo duplicado), `422` (RUT inválido).

### Eliminar cliente
`DELETE /clientes/{cliente_id}`  
**Respuesta:** `204 No Content`.  
**Error:** `404`.

### Health check
`GET /health`  
**Respuesta:** `200 OK` con `{"status":"healthy","service":"demo-ms-2","version":"1.0.0"}`.

## Despliegue en Cloud Run

1. Construir y subir la imagen:  
   ```bash
   gcloud builds submit --tag gcr.io/$GCP_PROJECT/demo-ms-2 backend/
   ```
2. Desplegar:  
   ```bash
   gcloud run deploy demo-ms-2 --image gcr.io/$GCP_PROJECT/demo-ms-2 \
       --platform managed --region us-central1 --allow-unauthenticated
   ```

Para CI/CD con GitHub Actions se puede usar `google-github-actions/deploy-cloudrun@v2`.

## Tecnologías

- Python 3.11, FastAPI, Uvicorn
- Firestore (Google Cloud Firestore)
- Docker, Google Cloud Run
- Pydantic, email-validator
