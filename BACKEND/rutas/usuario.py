# rutas/usuario.py

from fastapi import APIRouter, HTTPException
from esquemas.usuario import UsuarioCrear, UsuarioActualizar, UsuarioMostrar
from servicios.usuario import (
    crear_usuario, obtener_usuarios, obtener_usuario, actualizar_usuario, eliminar_usuario
)
from typing import List

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Crear usuario
@router.post("/", response_model=dict)
def crear(usuario: UsuarioCrear):
    usuario_id, fecha_creacion = crear_usuario(
        usuario.nombre,
        usuario.area_id,
        usuario.username,
        usuario.password,
        usuario.email,
        usuario.rol
    )
    return {
        "mensaje": "Usuario creado exitosamente.",
        "usuario": {
            "id": usuario_id,
            "nombre": usuario.nombre,
            "area_id": usuario.area_id,
            "username": usuario.username,
            "email": usuario.email,
            "rol": usuario.rol,
            "fecha_creacion": fecha_creacion
        }
    }

# Listar usuarios
@router.get("/", response_model=dict)
def listar():
    usuarios = obtener_usuarios()
    return {
        "mensaje": "Lista de usuarios.",
        "total": len(usuarios),
        "usuarios": usuarios
    }

# Obtener usuario por ID
@router.get("/{usuario_id}", response_model=dict)
def obtener(usuario_id: int):
    usuario = obtener_usuario(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "mensaje": "Usuario encontrado.",
        "usuario": usuario
    }

# Actualizar usuario
@router.put("/{usuario_id}", response_model=dict)
def actualizar(usuario_id: int, usuario: UsuarioActualizar):
    datos = usuario.dict(exclude_unset=True)
    actualizado = actualizar_usuario(usuario_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o sin cambios")
    # Retornar los datos nuevos, mezclando el dict de entrada con el id
    usuario_actual = obtener_usuario(usuario_id)
    return {
        "mensaje": "Usuario actualizado exitosamente.",
        "usuario": usuario_actual
    }

# Eliminar usuario
@router.delete("/{usuario_id}", response_model=dict)
def eliminar(usuario_id: int):
    eliminado = eliminar_usuario(usuario_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "mensaje": "Usuario eliminado exitosamente.",
        "id": usuario_id
    }
