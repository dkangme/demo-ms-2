from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class ClienteBase(BaseModel):
    rut: str = Field(
        ...,
        description="RUT chileno con formato XX.XXX.XXX-X",
        example="12.345.678-9",
    )
    nombres: str = Field(
        ..., min_length=1, max_length=100, example="Juan"
    )
    apellidos: str = Field(
        ..., min_length=1, max_length=100, example="Pérez"
    )
    correo: EmailStr = Field(..., example="juan@example.com")
    telefono: str = Field(
        ..., min_length=9, max_length=15, example="+56912345678"
    )


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
