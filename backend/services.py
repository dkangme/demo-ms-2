"""
Business logic layer for Cliente CRUD operations.
Contains the ClienteService class with methods for create, read, update, delete,
including RUT validation, email uniqueness checks, and Firestore persistence.
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from google.cloud import firestore

from models import ClienteCreate, ClienteUpdate, ClienteResponse
from validators import validate_rut

logger = logging.getLogger(__name__)


class ClienteService:
    """Service for client CRUD operations against Firestore."""

    def __init__(self, db: firestore.Client, collection: str) -> None:
        self.db = db
        self.collection = db.collection(collection)

    async def create(self, data: ClienteCreate) -> ClienteResponse:
        """Create a new client after validating RUT and email uniqueness."""
        if not validate_rut(data.rut):
            raise HTTPException(status_code=422, detail="RUT inv\u00e1lido")

        # Check email uniqueness
        email_exists = await self._check_email_exists(data.correo)
        if email_exists:
            raise HTTPException(status_code=409, detail="El correo ya est\u00e1 registrado")

        now = datetime.utcnow()
        doc_data = {
            "rut": data.rut,
            "nombres": data.nombres,
            "apellidos": data.apellidos,
            "correo": data.correo,
            "telefono": data.telefono,
            "created_at": now,
            "updated_at": now,
        }

        def _create_sync():
            doc_ref = self.collection.document()
            doc_ref.set(doc_data)
            return doc_ref.id

        doc_id = await asyncio.to_thread(_create_sync)
        doc_data["id"] = doc_id
        return ClienteResponse(**doc_data)

    async def get_by_id(self, cliente_id: str) -> ClienteResponse:
        """Retrieve a single client by its ID."""
        doc = await self._get_doc(cliente_id)
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return self._doc_to_response(doc)

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[ClienteResponse]:
        """List clients with optional pagination."""
        def _list_sync():
            docs = self.collection.offset(skip).limit(limit).stream()
            return [self._doc_to_response(d) for d in docs]
        return await asyncio.to_thread(_list_sync)

    async def update(self, cliente_id: str, data: ClienteUpdate) -> ClienteResponse:
        """Update an existing client partially; validates RUT and email uniqueness."""
        doc = await self._get_doc(cliente_id)
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        existing = doc.to_dict()
        update_data: dict = {}

        # Validate RUT if provided
        if data.rut is not None:
            if not validate_rut(data.rut):
                raise HTTPException(status_code=422, detail="RUT inv\u00e1lido")
            update_data["rut"] = data.rut

        # Handle email uniqueness
        if data.correo is not None and data.correo != existing.get("correo"):
            if await self._check_email_exists(data.correo):
                raise HTTPException(status_code=409, detail="El correo ya est\u00e1 registrado")
            update_data["correo"] = data.correo

        # Update other fields if provided
        for field in ("nombres", "apellidos", "telefono"):
            value = getattr(data, field, None)
            if value is not None:
                update_data[field] = value

        if not update_data:
            # No changes \u2013 return current document
            return self._doc_to_response(doc)

        update_data["updated_at"] = datetime.utcnow()

        def _update_sync():
            doc_ref = self.collection.document(cliente_id)
            doc_ref.update(update_data)

        await asyncio.to_thread(_update_sync)
        # Fetch updated document
        updated_doc = await self._get_doc(cliente_id)
        return self._doc_to_response(updated_doc)

    async def delete(self, cliente_id: str) -> None:
        """Delete a client by ID; raises 404 if not found."""
        doc = await self._get_doc(cliente_id)
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        def _delete_sync():
            doc.reference.delete()

        await asyncio.to_thread(_delete_sync)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _get_doc(self, cliente_id: str) -> firestore.DocumentSnapshot:
        """Retrieve a Firestore document snapshot by ID."""
        def _get():
            return self.collection.document(cliente_id).get()
        return await asyncio.to_thread(_get)

    async def _check_email_exists(self, email: str) -> bool:
        """Return True if a document with the given email already exists."""
        def _query():
            docs = self.collection.where("correo", "==", email).limit(1).stream()
            return any(True for _ in docs)
        return await asyncio.to_thread(_query)

    @staticmethod
    def _doc_to_response(doc_snapshot: firestore.DocumentSnapshot) -> ClienteResponse:
        """Convert a Firestore document snapshot to a ClienteResponse."""
        data = doc_snapshot.to_dict()
        data["id"] = doc_snapshot.id
        return ClienteResponse(**data)
