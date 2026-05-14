"""
FastAPI application entry point for the Demo MS 2 microservice.
Includes a root health endpoint and mounts the clientes CRUD router.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.cliente import router as clientes_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI(
    title="Demo MS 2",
    description="Microservicio CRUD de Cliente (RUT, nombres, apellidos, correo, teléfono)",
    version="1.0.0",
)

# CORS (permissive for demo; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include clientes router
app.include_router(clientes_router)


@app.get("/health")
async def health_check():
    """Health endpoint for Kubernetes / Cloud Run probes."""
    return {
        "status": "healthy",
        "service": "demo-ms-2",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Simple root welcome message."""
    return {"message": "Demo MS 2 API is running"}
