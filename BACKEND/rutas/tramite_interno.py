# --- RUTA: rutas/tramite_interno.py ---
# rutas/tramite_interno.py
# Endpoints completos para gestión de trámites internos en una municipalidad

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Body, Response
from esquemas.tramite_interno import TramiteInternoCrear, TramiteInternoActualizar
from servicios.tramite_interno import (
    crear_tramite_interno, obtener_tramites_internos, obtener_tramite_interno,
    actualizar_tramite_interno, eliminar_tramite_interno,
    obtener_tramites_internos_por_area
)
from servicios.seguimiento_tramite import (
    obtener_seguimiento_de_tramite_interno, crear_seguimiento_tramite
)
from servicios.derivacion import registrar_derivacion
from servicios.area import obtener_areas
from servicios.usuario import obtener_usuarios
import os
from datetime import datetime

router = APIRouter(prefix="/tramites-internos", tags=["Trámites Internos"])

# ---- CREAR TRÁMITE INTERNO ----
@router.post("/", response_model=dict)
async def crear_tramite_interno_endpoint(
    numero_referencia: str = Form(...),
    asunto: str = Form(...),
    contenido: str = Form(""),
    folios: int = Form(1),
    archivo: UploadFile = File(None),
    remitente_id: int = Form(...),
    area_origen_id: int = Form(...),
    area_destino_id: int = Form(...),
    prioridad: int = Form(3),
    fecha_vencimiento: str = Form(None),
):
    archivo_nombre = None
    if archivo:
        os.makedirs("archivos_tramites_internos", exist_ok=True)
        nombre_base = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.filename}"
        ruta_relativa = f"archivos_tramites_internos/{nombre_base}"
        with open(ruta_relativa, "wb") as f:
            contenido_pdf = await archivo.read()
            f.write(contenido_pdf)
        archivo_nombre = ruta_relativa

    datos = {
        "numero_referencia": numero_referencia,
        "asunto": asunto,
        "contenido": contenido,
        "folios": folios,
        "archivo": archivo_nombre,
        "remitente_id": remitente_id,
        "area_origen_id": area_origen_id,
        "area_destino_id": area_destino_id,
        "estado": "pendiente",
        "prioridad": prioridad,
        "fecha_vencimiento": fecha_vencimiento,
    }
    tramite_id, fecha_envio = crear_tramite_interno(datos)

    # Registrar movimiento inicial en seguimiento
    crear_seguimiento_tramite({
        "tramite_id": tramite_id,
        "tramite_type": "interno",
        "accion": "creado",
        "descripcion": f"Trámite interno creado y enviado a área destino ID {area_destino_id}",
        "usuario_id": remitente_id,
        "area_id": area_origen_id,
        "adjunto": archivo_nombre,
        "observaciones": None
    })

    tramite = {**datos, "id": tramite_id, "fecha_envio": fecha_envio}
    return {
        "mensaje": "Trámite interno creado exitosamente.",
        "tramite": tramite
    }

# ---- LISTAR TRÁMITES INTERNOS ----
@router.get("/", response_model=dict)
def listar(
    rol: str = Query(..., description="Rol del usuario logueado"),
    area_id: int = Query(None, description="Área del usuario logueado (si no es admin ni mesa_partes)")
):
    if rol in ("admin", "mesa_partes"):
        tramites = obtener_tramites_internos()
    else:
        if area_id is None:
            return {"mensaje": "Falta área", "total": 0, "tramites": []}
        tramites = obtener_tramites_internos_por_area(area_id)
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

# ---- OBTENER TRÁMITE INTERNO POR ID ----
@router.get("/{tramite_id}", response_model=dict)
def obtener(tramite_id: int):
    tramite = obtener_tramite_interno(tramite_id)
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite interno no encontrado")
    return {
        "mensaje": "Trámite interno encontrado.",
        "tramite": tramite
    }

# ---- HISTORIAL / SEGUIMIENTO ----
@router.get("/{tramite_id}/seguimiento", response_model=dict)
def seguimiento_tramite(tramite_id: int):
    movimientos = obtener_seguimiento_de_tramite_interno(tramite_id)
    return {
        "mensaje": "Seguimiento del trámite interno.",
        "seguimiento": movimientos
    }

# ---- DERIVAR TRÁMITE INTERNO ----
@router.post("/{tramite_id}/derivar", response_model=dict)
def derivar_tramite_interno(
    tramite_id: int,
    body: dict = Body(...)
):
    area_destino_id = body.get("area_id")
    observaciones = body.get("observaciones")
    usuario_id = body.get("usuario_id")

    if not area_destino_id or not usuario_id:
        raise HTTPException(status_code=400, detail="Debe proporcionar el área destino y usuario_id")

    tramite = obtener_tramite_interno(tramite_id)
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite interno no encontrado.")
    area_origen_id = tramite.get("area_destino_id")

    registrar_derivacion({
        "tramite_id": tramite_id,
        "tramite_type": "interno",
        "area_origen_id": area_origen_id,
        "area_destino_id": area_destino_id,
        "usuario_derivacion_id": usuario_id,
        "instrucciones": observaciones,
        "fecha_limite": None
    })

    crear_seguimiento_tramite({
        "tramite_id": tramite_id,
        "tramite_type": "interno",
        "accion": "derivado",
        "descripcion": f"Derivado al área ID {area_destino_id}",
        "usuario_id": usuario_id,
        "area_id": area_destino_id,
        "adjunto": None,
        "observaciones": observaciones
    })

    actualizar_tramite_interno(tramite_id, {
        "area_destino_id": area_destino_id,
        "estado": "derivado"
    })
    return {
        "mensaje": "Trámite derivado exitosamente.",
        "area_destino_id": area_destino_id
    }

# ---- CONTESTAR / ATENDER TRÁMITE INTERNO ----
@router.post("/{tramite_id}/contestar", response_model=dict)
async def contestar_tramite_interno(
    tramite_id: int,
    usuario_id: int = Form(...),
    respuesta: str = Form(""),
    pdf_respuesta: UploadFile = File(None)
):
    archivo_nombre = None
    if pdf_respuesta:
        os.makedirs("respuestas_tramites_internos", exist_ok=True)
        nombre_base = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{pdf_respuesta.filename}"
        ruta = f"respuestas_tramites_internos/{nombre_base}"
        with open(ruta, "wb") as f:
            contenido_pdf = await pdf_respuesta.read()
            f.write(contenido_pdf)
        archivo_nombre = ruta

    crear_seguimiento_tramite({
        "tramite_id": tramite_id,
        "tramite_type": "interno",
        "accion": "contestado",
        "descripcion": respuesta or "Respuesta adjunta.",
        "usuario_id": usuario_id,
        "area_id": None,
        "adjunto": archivo_nombre,
        "observaciones": None
    })
    actualizar_tramite_interno(tramite_id, {"estado": "atendido"})
    return {
        "mensaje": "Respuesta enviada exitosamente.",
        "respuesta": respuesta,
        "pdf_respuesta": archivo_nombre
    }

# ---- RECIBIR TRÁMITE (marcar como recibido) ----
@router.post("/{tramite_id}/recibir", response_model=dict)
def recibir_tramite_interno(
    tramite_id: int,
    usuario_id: int = Body(...)
):
    tramite = obtener_tramite_interno(tramite_id)
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite interno no encontrado.")
    now = datetime.now()
    actualizar_tramite_interno(tramite_id, {
        "estado": "recibido",
        "fecha_recepcion": now
    })
    crear_seguimiento_tramite({
        "tramite_id": tramite_id,
        "tramite_type": "interno",
        "accion": "recibido",
        "descripcion": "Trámite recibido por el área destino.",
        "usuario_id": usuario_id,
        "area_id": tramite["area_destino_id"],
        "adjunto": None,
        "observaciones": None
    })
    return {
        "mensaje": "Trámite marcado como recibido.",
        "fecha_recepcion": now.isoformat()
    }

# ---- DESCARGA / VISUALIZACIÓN DE PDF (seguro) ----
@router.get("/archivo/{carpeta}/{nombre_archivo}", response_class=Response)
def descargar_pdf(carpeta: str, nombre_archivo: str):
    # carpeta: "archivos_tramites_internos" o "respuestas_tramites_internos"
    directorio = os.path.join(os.getcwd(), carpeta)
    ruta = os.path.join(directorio, nombre_archivo)
    if not os.path.isfile(ruta):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    with open(ruta, "rb") as f:
        contenido = f.read()
    return Response(content=contenido, media_type="application/pdf")

# ---- LISTA DE ÁREAS Y USUARIOS (para selects) ----
@router.get("/areas", response_model=dict)
def listar_areas():
    areas = obtener_areas()
    return {"areas": areas}

@router.get("/usuarios", response_model=dict)
def listar_usuarios():
    usuarios = obtener_usuarios()
    return {"usuarios": usuarios}