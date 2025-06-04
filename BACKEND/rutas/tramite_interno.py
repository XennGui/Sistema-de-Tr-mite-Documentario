# rutas/tramite_interno.py

from fastapi import APIRouter, HTTPException
from esquemas.tramite_interno import (
    TramiteInternoCrear, TramiteInternoActualizar, TramiteInternoMostrar
)
from servicios.tramite_interno import (
    crear_tramite_interno, obtener_tramites_internos, obtener_tramite_interno,
    actualizar_tramite_interno, eliminar_tramite_interno
)
from typing import List

router = APIRouter(prefix="/tramites-internos", tags=["Trámites Internos"])

@router.post("/", response_model=dict)
def crear(tramite: TramiteInternoCrear):
    tramite_id, fecha_envio = crear_tramite_interno(tramite.dict())
    return {
        "mensaje": "Trámite interno creado exitosamente.",
        "tramite": {
            **tramite.dict(),
            "id": tramite_id,
            "fecha_envio": fecha_envio
        }
    }

@router.get("/", response_model=dict)
def listar():
    tramites = obtener_tramites_internos()
    return {
        "mensaje": "Lista de trámites internos.",
        "total": len(tramites),
        "tramites": tramites
    }

@router.get("/{tramite_id}", response_model=dict)
def obtener(tramite_id: int):
    tramite = obtener_tramite_interno(tramite_id)
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite interno no encontrado")
    return {
        "mensaje": "Trámite interno encontrado.",
        "tramite": tramite
    }

@router.put("/{tramite_id}", response_model=dict)
def actualizar(tramite_id: int, tramite: TramiteInternoActualizar):
    datos = tramite.dict(exclude_unset=True)
    actualizado = actualizar_tramite_interno(tramite_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Trámite interno no encontrado o sin cambios")
    tramite_actual = obtener_tramite_interno(tramite_id)
    return {
        "mensaje": "Trámite interno actualizado exitosamente.",
        "tramite": tramite_actual
    }

@router.delete("/{tramite_id}", response_model=dict)
def eliminar(tramite_id: int):
    eliminado = eliminar_tramite_interno(tramite_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Trámite interno no encontrado")
    return {
        "mensaje": "Trámite interno eliminado exitosamente.",
        "id": tramite_id
    }
