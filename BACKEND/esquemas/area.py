# esquemas/area.py

from pydantic import BaseModel
from typing import Optional

class AreaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class AreaCrear(AreaBase):
    pass

class AreaActualizar(AreaBase):
    pass

class AreaMostrar(AreaBase):
    id: int
    class Config:
        orm_mode = True