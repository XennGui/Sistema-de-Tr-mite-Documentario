# rutas/area.py

from fastapi import APIRouter, HTTPException
from esquemas.area import AreaCrear, AreaActualizar, AreaMostrar
from servicios.area import (
    crear_area, obtener_areas, obtener_area, actualizar_area, eliminar_area
)
from typing import List

router = APIRouter(prefix="/areas", tags=["Áreas"])

# Crear área
@router.post("/", response_model=dict)
def crear(area: AreaCrear):
    area_id = crear_area(area.nombre, area.descripcion)
    return {
        "mensaje": "Área creada exitosamente.",
        "area": {
            "id": area_id,
            "nombre": area.nombre,
            "descripcion": area.descripcion
        }
    }

# Listar áreas
@router.get("/", response_model=dict)
def listar():
    areas = obtener_areas()
    return {
        "mensaje": "Lista de áreas.",
        "total": len(areas),
        "areas": areas
    }

# Obtener área por ID
@router.get("/{area_id}", response_model=dict)
def obtener(area_id: int):
    area = obtener_area(area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")
    return {
        "mensaje": "Área encontrada.",
        "area": area
    }

# Actualizar área
@router.put("/{area_id}", response_model=dict)
def actualizar(area_id: int, area: AreaActualizar):
    actualizado = actualizar_area(area_id, area.nombre, area.descripcion)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Área no encontrada")
    return {
        "mensaje": "Área actualizada exitosamente.",
        "area": {
            "id": area_id,
            "nombre": area.nombre,
            "descripcion": area.descripcion
        }
    }

# Eliminar área
@router.delete("/{area_id}", response_model=dict)
def eliminar(area_id: int):
    eliminado = eliminar_area(area_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Área no encontrada")
    return {
        "mensaje": "Área eliminada exitosamente.",
        "id": area_id
    }