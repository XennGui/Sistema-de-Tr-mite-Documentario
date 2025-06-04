# esquemas/seguimiento_tramite.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SeguimientoTramiteBase(BaseModel):
    tramite_id: int
    tramite_type: str = Field(..., pattern="^(externo|interno)$")
    accion: str
    descripcion: str
    usuario_id: int
    area_id: Optional[int] = None
    adjunto: Optional[str] = None
    observaciones: Optional[str] = None

class SeguimientoTramiteCrear(SeguimientoTramiteBase):
    pass

class SeguimientoTramiteActualizar(BaseModel):
    accion: Optional[str] = None
    descripcion: Optional[str] = None
    area_id: Optional[int] = None
    adjunto: Optional[str] = None
    observaciones: Optional[str] = None

class SeguimientoTramiteMostrar(BaseModel):
    id: int
    tramite_id: int
    tramite_type: str
    accion: str
    descripcion: str
    usuario_id: int
    area_id: Optional[int]
    adjunto: Optional[str]
    observaciones: Optional[str]
    fecha_hora: datetime

    class Config:
        from_attributes = True
        