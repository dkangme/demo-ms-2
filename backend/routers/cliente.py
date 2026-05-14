"""
FastAPI router for /clientes endpoints.
Provides full CRUD operations with dependency injection of ClienteService.
"""

import os
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List

from models import ClienteCreate, ClienteUpdate, ClienteResponse
from services import ClienteService
from db import get_db

router = APIRouter(prefix="/clientes", tags=["clientes"])


def _get_service() -> ClienteService:
    """Dependency that provides a fully initialized ClienteService."""
    db = get_db()
    collection = os.environ.get("FIRESTORE_COLLECTION")
    if not collection:
        raise EnvironmentError("FIRESTORE_COLLECTION environment variable is required")
    return ClienteService(db, collection)


@router.post("/", response_model=ClienteResponse, status_code=201)
async def crear_cliente(
    data: ClienteCreate,
    service: ClienteService = Depends(_get_service),
):
    """Creates a new client."""
    return await service.create(data)


@router.get("/", response_model=List[ClienteResponse])
async def listar_clientes(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    service: ClienteService = Depends(_get_service),
):
    """Lists all clients with pagination."""
    return await service.list_all(skip, limit)


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obtener_cliente(
    cliente_id: str,
    service: ClienteService = Depends(_get_service),
):
    """Returns a single client by its ID."""
    return await service.get_by_id(cliente_id)


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def actualizar_cliente(
    cliente_id: str,
    data: ClienteUpdate,
    service: ClienteService = Depends(_get_service),
):
    """Partially updates an existing client."""
    return await service.update(cliente_id, data)


@router.delete("/{cliente_id}", status_code=204)
async def eliminar_cliente(
    cliente_id: str,
    service: ClienteService = Depends(_get_service),
):
    """Deletes a client. Returns 204 on success."""
    await service.delete(cliente_id)
