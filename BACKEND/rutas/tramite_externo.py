# rutas/tramite_externo.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Body
from esquemas.tramite_externo import (
    TramiteExternoCrear, TramiteExternoActualizar, TramiteExternoMostrar
)
from servicios.tramite_externo import (
    crear_tramite_externo, obtener_tramites_externos, obtener_tramite_externo,
    actualizar_tramite_externo, eliminar_tramite_externo, buscar_tramite_externo_por_expediente_y_codigo
)
from servicios.seguimiento_tramite import obtener_seguimiento_de_tramite_externo
from servicios.derivacion import registrar_derivacion
from servicios.seguimiento_tramite import crear_seguimiento_tramite
from typing import List
import os
import random
import string
from datetime import datetime
import pytz

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(prefix="/tramites-externos", tags=["Trámites Externos"])

MESA_PARTES_CORREO = "xen.luna.07@gmail.com"
MESA_PARTES_CLAVE = "hvqicgclgwzsbyoo"

def enviar_correo_a_mesa(tramite):
    asunto = f"📢 Nuevo trámite externo registrado: {tramite['numero_expediente']}"
    cuerpo = f"""
📄 *Nuevo trámite externo registrado en la plataforma municipal de Yau* 📄

🔹 *Detalles del trámite:*
-----------------------------------
🗂️ Nº expediente      : {tramite['numero_expediente']}
👤 Remitente         : {tramite['remitente']}
📑 Tipo de documento : {tramite['tipo_documento']}
📄 Folios            : {tramite['folios']}
📝 Asunto            : {tramite['asunto']}
🔐 Código de seguridad: {tramite['codigo_seguridad']}
🕒 Fecha y Hora      : {tramite['fecha_registro']}
📧 Correo remitente  : {tramite['email']}
📞 Teléfono          : {tramite['telefono'] or '-'}

⚠️ Por favor, no responda a este correo, ya que es un mensaje automático generado por la plataforma municipal.

🤝 Atentamente,
Sistema de Trámites Externos
"""

    msg = MIMEMultipart()
    msg["From"] = MESA_PARTES_CORREO
    msg["To"] = MESA_PARTES_CORREO
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(MESA_PARTES_CORREO, MESA_PARTES_CLAVE)
            server.sendmail(MESA_PARTES_CORREO, MESA_PARTES_CORREO, msg.as_string())
    except Exception as e:
        print("Error enviando correo:", e)

def generar_codigo_seguridad(longitud=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=longitud))

def generar_numero_expediente():
    tz = pytz.timezone("America/Lima")
    fecha = datetime.now(tz).strftime("%Y%m%d")
    nro = ''.join(random.choices(string.digits, k=5))
    return f"{fecha}-{nro}"

@router.post("/", response_model=dict)
async def crear_tramite(
    remitente: str = Form(...),
    tipo_documento: str = Form(...),
    folios: int = Form(...),
    asunto: str = Form(...),
    contenido: str = Form(""),
    archivo: UploadFile = File(None),
    tipo_persona: str = Form(...),
    dni_ruc: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(""),
):
    archivo_nombre = None
    if archivo:
        os.makedirs("archivos_tramites", exist_ok=True)
        nombre_base = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.filename}"
        ruta_relativa = f"archivos_tramites/{nombre_base}"
        with open(ruta_relativa, "wb") as f:
            contenido_pdf = await archivo.read()
            f.write(contenido_pdf)
        archivo_nombre = ruta_relativa

    tz = pytz.timezone("America/Lima")
    fecha_actual = datetime.now(tz)
    numero_expediente = generar_numero_expediente()
    codigo_seguridad = generar_codigo_seguridad()

    datos = {
        "numero_expediente": numero_expediente,
        "codigo_seguridad": codigo_seguridad,
        "remitente": remitente,
        "tipo_documento": tipo_documento,
        "folios": folios,
        "asunto": asunto,
        "contenido": contenido,
        "archivo": archivo_nombre,
        "tipo_persona": tipo_persona,
        "dni_ruc": dni_ruc,
        "email": email,
        "telefono": telefono,
        "estado": "pendiente",
        "prioridad": 3,
        "fecha_vencimiento": None,
        "usuario_registro_id": None,
        "area_actual_id": None
    }
    tramite_id, fecha_registro = crear_tramite_externo(datos)

    if isinstance(fecha_registro, datetime):
        fecha_registro_lima = fecha_registro.astimezone(tz)
    else:
        fecha_registro_lima = fecha_actual

    fecha_registro_str = fecha_registro_lima.strftime("%Y-%m-%dT%H:%M:%S") #formato ISO

    tramite = {
        **datos,
        "id": tramite_id,
        "fecha_registro": fecha_registro_str
    }

    try:
        enviar_correo_a_mesa({
            **tramite,
            "fecha_registro": fecha_registro_str
        })
    except Exception as e:
        print(f"Error al enviar correo a mesa de partes: {e}")

    return {
        "mensaje": "Su documento se ha registrado exitosamente",
        "tramite": tramite
    }

@router.get("/", response_model=dict)
def listar(
    rol: str = Query(..., description="Rol del usuario logueado"),
    area_id: int = Query(None, description="Área del usuario logueado (si no es admin ni mesa_partes)")
):
    """
    Devuelve trámites según el rol:
    - admin y mesa_partes: todos los trámites
    - otro rol: solo trámites de su área
    """
    from servicios.tramite_externo import obtener_tramites_externos_por_area
    if rol in ("admin", "mesa_partes"):
        tramites = obtener_tramites_externos()
    else:
        if area_id is None:
            return {"mensaje": "Falta área", "total": 0, "tramites": []}
        tramites = obtener_tramites_externos_por_area(area_id)
    for t in tramites:
        if t["fecha_registro"] and not isinstance(t["fecha_registro"], str):
            t["fecha_registro"] = t["fecha_registro"].isoformat()
    return {
        "mensaje": "Lista de trámites externos.",
        "total": len(tramites),
        "tramites": tramites
    }

@router.get("/buscar", response_model=dict)
def buscar_tramite(
    numero_expediente: str = Query(...),
    codigo_seguridad: str = Query(...)
):
    tramite = buscar_tramite_externo_por_expediente_y_codigo(numero_expediente, codigo_seguridad)
    if not tramite:
        raise HTTPException(status_code=404, detail="No se encontró el trámite con esos datos.")

    movimientos = obtener_seguimiento_de_tramite_externo(tramite["id"])
    pdf_respuesta = None
    for mov in reversed(movimientos): 
        if mov["accion"] == "contestado" and mov["adjunto"]:
            pdf_respuesta = mov["adjunto"]
            break

    return {
        "mensaje": "Trámite encontrado.",
        "tramite": tramite,
        "pdf_respuesta": pdf_respuesta
    }

@router.get("/{tramite_id}/seguimiento", response_model=dict)
def seguimiento_tramite(tramite_id: int):
    movimientos = obtener_seguimiento_de_tramite_externo(tramite_id)
    return {
        "mensaje": "Seguimiento del trámite.",
        "seguimiento": movimientos
    }

@router.get("/{tramite_id}", response_model=dict)
def obtener(tramite_id: int):
    tramite = obtener_tramite_externo(tramite_id)
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite externo no encontrado")
    if tramite and tramite["fecha_registro"] and not isinstance(tramite["fecha_registro"], str):
        tramite["fecha_registro"] = tramite["fecha_registro"].isoformat()
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
    if tramite_actual and tramite_actual["fecha_registro"] and not isinstance(tramite_actual["fecha_registro"], str):
        tramite_actual["fecha_registro"] = tramite_actual["fecha_registro"].isoformat()
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

@router.post("/{tramite_id}/contestar", response_model=dict)
async def contestar_tramite_externo(
    tramite_id: int,
    respuesta: str = Form(""),
    pdf_respuesta: UploadFile = File(None)
):
    archivo_nombre = None
    if pdf_respuesta:
        os.makedirs("respuestas_tramites", exist_ok=True)
        nombre_base = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{pdf_respuesta.filename}"
        ruta = os.path.join("respuestas_tramites", nombre_base)
        with open(ruta, "wb") as f:
            contenido_pdf = await pdf_respuesta.read()
            f.write(contenido_pdf)
        archivo_nombre = ruta

    from servicios.seguimiento_tramite import crear_seguimiento_tramite
    crear_seguimiento_tramite({
        "tramite_id": tramite_id,
        "tramite_type": "externo",
        "accion": "contestado",
        "descripcion": respuesta or "Respuesta adjunta.",
        "usuario_id": 1, 
        "area_id": None,
        "adjunto": archivo_nombre,
        "observaciones": None
    })
    actualizar_tramite_externo(tramite_id, {"estado": "atendido"})

    return {
        "mensaje": "Respuesta enviada exitosamente.",
        "respuesta": respuesta,
        "pdf_respuesta": archivo_nombre
    }

@router.post("/{tramite_id}/derivar", response_model=dict)
def derivar_tramite_externo(
    tramite_id: int,
    body: dict = Body(...)
):
    area_destino_id = body.get("area_id")
    observaciones = body.get("observaciones")  # Opcional

    if not area_destino_id:
        raise HTTPException(status_code=400, detail="Debe proporcionar el área destino (area_id).")

    tramite = obtener_tramite_externo(tramite_id)
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite externo no encontrado.")

    area_origen_id = tramite.get("area_actual_id")
    usuario_id = 1  

    if area_origen_id is None:
        area_origen_id = area_destino_id  

    registrar_derivacion({
        "tramite_id": tramite_id,
        "tramite_type": "externo",
        "area_origen_id": area_origen_id,
        "area_destino_id": area_destino_id,
        "usuario_derivacion_id": usuario_id,
        "instrucciones": observaciones,
        "fecha_limite": None
    })

    crear_seguimiento_tramite({
        "tramite_id": tramite_id,
        "tramite_type": "externo",
        "accion": "derivado",
        "descripcion": f"Derivado al área ID {area_destino_id}",
        "usuario_id": usuario_id,
        "area_id": area_destino_id,
        "adjunto": None,
        "observaciones": observaciones
    })

    actualizar_tramite_externo(tramite_id, {
        "area_actual_id": area_destino_id,
        "estado": "derivado"
    })

    return {
        "mensaje": "Trámite derivado exitosamente.",
        "area_destino_id": area_destino_id
    }
