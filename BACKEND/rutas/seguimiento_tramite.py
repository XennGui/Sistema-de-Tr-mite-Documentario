# rutas/seguimiento_tramite.py

from fastapi import APIRouter, HTTPException
from esquemas.seguimiento_tramite import (
    SeguimientoTramiteCrear, SeguimientoTramiteActualizar, SeguimientoTramiteMostrar
)
from servicios.seguimiento_tramite import (
    crear_seguimiento_tramite, obtener_seguimientos_tramite, obtener_seguimiento_tramite,
    actualizar_seguimiento_tramite, eliminar_seguimiento_tramite
)
from typing import List

router = APIRouter(prefix="/seguimiento-tramites", tags=["Seguimiento de Trámites"])

@router.post("/", response_model=dict)
def crear(seguimiento: SeguimientoTramiteCrear):
    seguimiento_id, fecha_hora = crear_seguimiento_tramite(seguimiento.dict())
    return {
        "mensaje": "Seguimiento creado exitosamente.",
        "seguimiento": {
            **seguimiento.dict(),
            "id": seguimiento_id,
            "fecha_hora": fecha_hora
        }
    }

@router.get("/", response_model=dict)
def listar():
    seguimientos = obtener_seguimientos_tramite()
    return {
        "mensaje": "Lista de seguimientos.",
        "total": len(seguimientos),
        "seguimientos": seguimientos
    }

@router.get("/{seguimiento_id}", response_model=dict)
def obtener(seguimiento_id: int):
    seguimiento = obtener_seguimiento_tramite(seguimiento_id)
    if not seguimiento:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
    return {
        "mensaje": "Seguimiento encontrado.",
        "seguimiento": seguimiento
    }

@router.put("/{seguimiento_id}", response_model=dict)
def actualizar(seguimiento_id: int, seguimiento: SeguimientoTramiteActualizar):
    datos = seguimiento.dict(exclude_unset=True)
    actualizado = actualizar_seguimiento_tramite(seguimiento_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado o sin cambios")
    seguimiento_actual = obtener_seguimiento_tramite(seguimiento_id)
    return {
        "mensaje": "Seguimiento actualizado exitosamente.",
        "seguimiento": seguimiento_actual
    }

@router.delete("/{seguimiento_id}", response_model=dict)
def eliminar(seguimiento_id: int):
    eliminado = eliminar_seguimiento_tramite(seguimiento_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
    return {
        "mensaje": "Seguimiento eliminado exitosamente.",
        "id": seguimiento_id
    }
