# RUTA: rutas/tramite_interno.py

from fastapi import APIRouter, HTTPException, Query
from esquemas.tramite_interno import (
    TramiteInternoCrear, TramiteInternoActualizar
)
from servicios.tramite_interno import (
    crear_tramite_interno, obtener_tramites_internos, obtener_tramite_interno,
    actualizar_tramite_interno, eliminar_tramite_interno,
    obtener_tramites_internos_por_area
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
def listar(
    rol: str = Query(..., description="Rol del usuario logueado"),
    area_id: int = Query(None, description="Área del usuario logueado (si no es admin ni mesa_partes)")
):
    """
    Devuelve trámites internos según el rol:
    - admin y mesa_partes: todos los trámites internos
    - otro rol: solo trámites internos de su área de destino
    """
    if rol in ("admin", "mesa_partes"):
        tramites = obtener_tramites_internos()
    else:
        if area_id is None:
            return {"mensaje": "Falta área", "total": 0, "tramites": []}
        tramites = obtener_tramites_internos_por_area(area_id)
    # Asegura formato ISO para fechas
    for t in tramites:
        if t["fecha_envio"] and not isinstance(t["fecha_envio"], str):
            t["fecha_envio"] = t["fecha_envio"].isoformat()
        if t["fecha_recepcion"] and not isinstance(t["fecha_recepcion"], str):
            t["fecha_recepcion"] = t["fecha_recepcion"].isoformat()
        if t["fecha_vencimiento"] and not isinstance(t["fecha_vencimiento"], str):
            t["fecha_vencimiento"] = t["fecha_vencimiento"].isoformat()
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
