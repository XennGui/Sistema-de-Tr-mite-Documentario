# esquemas/tramite_externo.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class TramiteExternoBase(BaseModel):
    numero_expediente: str
    codigo_seguridad: str
    remitente: str
    tipo_documento: str
    folios: int
    asunto: str
    contenido: Optional[str] = None
    archivo: Optional[str] = None
    tipo_persona: str = Field(..., pattern="^(natural|juridica)$")
    dni_ruc: str
    email: EmailStr
    telefono: Optional[str] = None
    estado: Optional[str] = Field(default="pendiente", pattern="^(pendiente|atendido|denegado|derivado|archivado)$")
    prioridad: Optional[int] = Field(default=3, ge=1, le=5)
    fecha_vencimiento: Optional[datetime] = None
    usuario_registro_id: Optional[int] = None
    area_actual_id: Optional[int] = None

class TramiteExternoCrear(TramiteExternoBase):
    pass

class TramiteExternoActualizar(BaseModel):
    remitente: Optional[str] = None
    tipo_documento: Optional[str] = None
    folios: Optional[int] = None
    asunto: Optional[str] = None
    contenido: Optional[str] = None
    archivo: Optional[str] = None
    tipo_persona: Optional[str] = Field(default=None, pattern="^(natural|juridica)$")
    dni_ruc: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    estado: Optional[str] = Field(default=None, pattern="^(pendiente|atendido|denegado|derivado|archivado)$")
    prioridad: Optional[int] = Field(default=None, ge=1, le=5)
    fecha_vencimiento: Optional[datetime] = None
    usuario_registro_id: Optional[int] = None
    area_actual_id: Optional[int] = None

class TramiteExternoMostrar(BaseModel):
    id: int
    numero_expediente: str
    codigo_seguridad: str
    remitente: str
    tipo_documento: str
    folios: int
    asunto: str
    contenido: Optional[str]
    archivo: Optional[str]
    tipo_persona: str
    dni_ruc: str
    email: EmailStr
    telefono: Optional[str]
    estado: str
    prioridad: int
    fecha_registro: datetime
    fecha_vencimiento: Optional[datetime]
    usuario_registro_id: Optional[int]
    area_actual_id: Optional[int]

    class Config:
        from_attributes = True  # en vez de orm_mode para Pydantic v2  
