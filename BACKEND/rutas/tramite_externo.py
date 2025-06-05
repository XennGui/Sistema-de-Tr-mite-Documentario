# rutas/tramite_externo.py

from fastapi import APIRouter, HTTPException
from esquemas.tramite_externo import (
    TramiteExternoCrear, TramiteExternoActualizar, TramiteExternoMostrar
)
from servicios.tramite_externo import (
    crear_tramite_externo, obtener_tramites_externos, obtener_tramite_externo,
    actualizar_tramite_externo, eliminar_tramite_externo
)
from typing import List

router = APIRouter(prefix="/tramites-externos", tags=["Trámites Externos"])

@router.post("/", response_model=dict)
def crear(tramite: TramiteExternoCrear):
    tramite_id, fecha_registro = crear_tramite_externo(tramite.dict())
    return {
        "mensaje": "Trámite externo creado exitosamente.",
        "tramite": {
            **tramite.dict(),
            "id": tramite_id,
            "fecha_registro": fecha_registro
        }
    }

@router.get("/", response_model=dict)
def listar():
    tramites = obtener_tramites_externos()
    return {
        "mensaje": "Lista de trámites externos.",
        "total": len(tramites),
        "tramites": tramites
    }

@router.get("/{tramite_id}", response_model=dict)
def obtener(tramite_id: int):
    tramite = obtener_tramite_externo(tramite_id)
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite externo no encontrado")
    return {
        "mensaje": "Trámite externo encontrado.",
        "tramite": tramite
    }

@router.put("/{tramite_id}", response_model=dict)
def actualizar(tramite_id: int, tramite: TramiteExternoActualizar):
    datos = tramite.dict(exclude_unset=True)
    actualizado = actualizar_tramite_externo(tramite_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Trámite externo no encontrado o sin cambios")
    tramite_actual = obtener_tramite_externo(tramite_id)
    return {
        "mensaje": "Trámite externo actualizado exitosamente.",
        "tramite": tramite_actual
    }

@router.delete("/{tramite_id}", response_model=dict)
def eliminar(tramite_id: int):
    eliminado = eliminar_tramite_externo(tramite_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Trámite externo no encontrado")
    return {
        "mensaje": "Trámite externo eliminado exitosamente.",
        "id": tramite_id
    }
