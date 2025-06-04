# esquemas/derivacion.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DerivacionBase(BaseModel):
    tramite_id: int
    tramite_type: str = Field(..., pattern="^(externo|interno)$")
    area_origen_id: int
    area_destino_id: int
    usuario_derivacion_id: int
    instrucciones: Optional[str] = None
    fecha_limite: Optional[datetime] = None

class DerivacionCrear(DerivacionBase):
    pass

class DerivacionActualizar(BaseModel):
    area_origen_id: Optional[int] = None
    area_destino_id: Optional[int] = None
    usuario_derivacion_id: Optional[int] = None
    instrucciones: Optional[str] = None
    fecha_limite: Optional[datetime] = None

class DerivacionMostrar(BaseModel):
    id: int
    tramite_id: int
    tramite_type: str
    area_origen_id: int
    area_destino_id: int
    usuario_derivacion_id: int
    fecha_derivacion: datetime
    instrucciones: Optional[str]
    fecha_limite: Optional[datetime]

    class Config:
        from_attributes = True
        