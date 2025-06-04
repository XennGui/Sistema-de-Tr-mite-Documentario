# rutas/documento_generado.py

from fastapi import APIRouter, HTTPException
from esquemas.documento_generado import (
    DocumentoGeneradoCrear, DocumentoGeneradoActualizar, DocumentoGeneradoMostrar
)
from servicios.documento_generado import (
    crear_documento_generado, obtener_documentos_generados, obtener_documento_generado,
    actualizar_documento_generado, eliminar_documento_generado
)

router = APIRouter(prefix="/documentos-generados", tags=["Documentos Generados"])

@router.post("/", response_model=dict)
def crear(documento: DocumentoGeneradoCrear):
    documento_id, fecha_creacion = crear_documento_generado(documento.dict())
    return {
        "mensaje": "Documento generado creado exitosamente.",
        "documento": {
            **documento.dict(),
            "id": documento_id,
            "fecha_creacion": fecha_creacion
        }
    }

@router.get("/", response_model=dict)
def listar():
    documentos = obtener_documentos_generados()
    return {
        "mensaje": "Lista de documentos generados.",
        "total": len(documentos),
        "documentos": documentos
    }

@router.get("/{documento_id}", response_model=dict)
def obtener(documento_id: int):
    documento = obtener_documento_generado(documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento generado no encontrado")
    return {
        "mensaje": "Documento generado encontrado.",
        "documento": documento
    }

@router.put("/{documento_id}", response_model=dict)
def actualizar(documento_id: int, documento: DocumentoGeneradoActualizar):
    datos = documento.dict(exclude_unset=True)
    actualizado = actualizar_documento_generado(documento_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Documento generado no encontrado o sin cambios")
    documento_actual = obtener_documento_generado(documento_id)
    return {
        "mensaje": "Documento generado actualizado exitosamente.",
        "documento": documento_actual
    }

@router.delete("/{documento_id}", response_model=dict)
def eliminar(documento_id: int):
    eliminado = eliminar_documento_generado(documento_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Documento generado no encontrado")
    return {
        "mensaje": "Documento generado eliminado exitosamente.",
        "id": documento_id
    }
