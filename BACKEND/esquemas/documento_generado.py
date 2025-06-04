# esquemas/documento_generado.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentoGeneradoBase(BaseModel):
    tramite_id: int
    tramite_type: str = Field(..., pattern="^(externo|interno)$")
    tipo_documento: str
    contenido: str
    archivo: str
    usuario_generador_id: int
    firmado: Optional[bool] = False
    fecha_firma: Optional[datetime] = None

class DocumentoGeneradoCrear(DocumentoGeneradoBase):
    pass

class DocumentoGeneradoActualizar(BaseModel):
    tipo_documento: Optional[str] = None
    contenido: Optional[str] = None
    archivo: Optional[str] = None
    firmado: Optional[bool] = None
    fecha_firma: Optional[datetime] = None

class DocumentoGeneradoMostrar(BaseModel):
    id: int
    tramite_id: int
    tramite_type: str
    tipo_documento: str
    contenido: str
    archivo: str
    usuario_generador_id: int
    fecha_creacion: datetime
    firmado: bool
    fecha_firma: Optional[datetime]

    class Config:
        from_attributes = True
        