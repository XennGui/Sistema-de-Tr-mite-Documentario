# esquemas/usuario.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    nombre: str
    area_id: Optional[int] = None
    username: str
    password: str
    email: EmailStr
    rol: Optional[str] = "admin"

class UsuarioCrear(UsuarioBase):
    pass

class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = None
    area_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None

class UsuarioMostrar(BaseModel):
    id: int
    nombre: str
    area_id: Optional[int]
    username: str
    email: EmailStr
    rol: str
    fecha_creacion: datetime

    class Config:
        orm_mode = True
        