# rutas/derivacion.py
# Rutas:
#   - POST    /derivaciones/          : Crear derivación
#   - GET     /derivaciones/          : Listar derivaciones
#   - GET     /derivaciones/{id}      : Obtener derivación por ID
#   - PUT     /derivaciones/{id}      : Actualizar derivación
#   - DELETE  /derivaciones/{id}      : Eliminar derivación

from fastapi import APIRouter, HTTPException
from esquemas.derivacion import (
    DerivacionCrear, DerivacionActualizar, DerivacionMostrar
)
from servicios.derivacion import (
    crear_derivacion, obtener_derivaciones, obtener_derivacion,
    actualizar_derivacion, eliminar_derivacion
)

router = APIRouter(prefix="/derivaciones", tags=["Derivaciones"])

@router.post("/", response_model=dict)
def crear(derivacion: DerivacionCrear):
    derivacion_id, fecha_derivacion = crear_derivacion(derivacion.dict())
    return {
        "mensaje": "Derivación creada exitosamente.",
        "derivacion": {
            **derivacion.dict(),
            "id": derivacion_id,
            "fecha_derivacion": fecha_derivacion
        }
    }

@router.get("/", response_model=dict)
def listar():
    derivaciones = obtener_derivaciones()
    return {
        "mensaje": "Lista de derivaciones.",
        "total": len(derivaciones),
        "derivaciones": derivaciones
    }

@router.get("/{derivacion_id}", response_model=dict)
def obtener(derivacion_id: int):
    derivacion = obtener_derivacion(derivacion_id)
    if not derivacion:
        raise HTTPException(status_code=404, detail="Derivación no encontrada")
    return {
        "mensaje": "Derivación encontrada.",
        "derivacion": derivacion
    }

@router.put("/{derivacion_id}", response_model=dict)
def actualizar(derivacion_id: int, derivacion: DerivacionActualizar):
    datos = derivacion.dict(exclude_unset=True)
    actualizado = actualizar_derivacion(derivacion_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Derivación no encontrada o sin cambios")
    derivacion_actual = obtener_derivacion(derivacion_id)
    return {
        "mensaje": "Derivación actualizada exitosamente.",
        "derivacion": derivacion_actual
    }

@router.delete("/{derivacion_id}", response_model=dict)
def eliminar(derivacion_id: int):
    eliminado = eliminar_derivacion(derivacion_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Derivación no encontrada")
    return {
        "mensaje": "Derivación eliminada exitosamente.",
        "id": derivacion_id
    }
