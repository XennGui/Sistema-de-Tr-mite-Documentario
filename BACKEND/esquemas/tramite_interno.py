# esquemas/tramite_interno.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TramiteInternoBase(BaseModel):
    numero_referencia: str
    asunto: str
    contenido: str
    folios: Optional[int] = 1
    archivo: Optional[str] = None
    remitente_id: int
    area_origen_id: int
    area_destino_id: int
    estado: Optional[str] = Field(default="pendiente", pattern="^(pendiente|recibido|atendido|derivado|archivado)$")
    prioridad: Optional[int] = Field(default=3, ge=1, le=5)
    fecha_vencimiento: Optional[datetime] = None

class TramiteInternoCrear(TramiteInternoBase):
    pass

class TramiteInternoActualizar(BaseModel):
    asunto: Optional[str] = None
    contenido: Optional[str] = None
    folios: Optional[int] = None
    archivo: Optional[str] = None
    remitente_id: Optional[int] = None
    area_origen_id: Optional[int] = None
    area_destino_id: Optional[int] = None
    estado: Optional[str] = Field(default=None, pattern="^(pendiente|recibido|atendido|derivado|archivado)$")
    prioridad: Optional[int] = Field(default=None, ge=1, le=5)
    fecha_recepcion: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None

class TramiteInternoMostrar(BaseModel):
    id: int
    numero_referencia: str
    asunto: str
    contenido: str
    folios: int
    archivo: Optional[str]
    remitente_id: int
    area_origen_id: int
    area_destino_id: int
    estado: str
    prioridad: int
    fecha_envio: datetime
    fecha_recepcion: Optional[datetime]
    fecha_vencimiento: Optional[datetime]

    class Config:
        from_attributes = True
        