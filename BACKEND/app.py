from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from rutas.area import router as area_router
from rutas.usuario import router as usuario_router
from rutas.tramite_externo import router as tramite_externo_router
from rutas.tramite_interno import router as tramite_interno_router
from rutas.seguimiento_tramite import router as seguimiento_tramite_router
from rutas.derivacion import router as derivacion_router
from rutas.documento_generado import router as documento_generado_router 
from pydantic import BaseModel
from typing import Dict, Optional, List, Tuple
from embeddings import create_embeddings, save_vectorstore, load_vectorstore, prepare_docs_from_db
from db import fetch_all_data, get_connection
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain_ollama import OllamaLLM
import unicodedata
import re
import dateparser

# --------- AGREGADO PARA MANEJO DE PDF ---------
import os
import PyPDF2

from servicios.tramite_externo import obtener_tramite_externo
from servicios.tramite_interno import obtener_tramite_interno

def obtener_ruta_pdf_por_id(pdf_id):
    tramite = obtener_tramite_externo(pdf_id)
    if tramite and tramite.get("archivo") and os.path.exists(tramite["archivo"]):
        return tramite["archivo"]
    tramite = obtener_tramite_interno(pdf_id)
    if tramite and tramite.get("archivo") and os.path.exists(tramite["archivo"]):
        return tramite["archivo"]
    return None

def extraer_texto_pdf(ruta_pdf):
    texto = ""
    with open(ruta_pdf, "rb") as f:
        lector = PyPDF2.PdfReader(f)
        for page in lector.pages:
            texto += page.extract_text() or ""
    return texto

def pregunta_es_sobre_pdf(pregunta):
    pregunta = pregunta.lower()
    claves_pdf = [
        "pdf", "documento", "adjunto", "archivo", "de que trata", "de qué trata", "resumen", "contenido", "explica", "según el pdf", "segun el pdf"
    ]
    return any(clave in pregunta for clave in claves_pdf)

def obtener_metadatos_pdf(pdf_id):
    from servicios.area import obtener_area_por_id

    # Primero busca en internos
    tramite = obtener_tramite_interno(pdf_id)
    if tramite:
        from servicios.usuario import obtener_usuario_por_id
        usuario = obtener_usuario_por_id(tramite["remitente_id"])
        nombre_remitente = usuario["nombre"] if usuario else "Desconocido"
        tramite["tipo_origen"] = "interno"
        tramite["nombre_remitente"] = nombre_remitente
        area_id = usuario["area_id"] if usuario and "area_id" in usuario else None
        nombre_area = None
        if area_id:
            area = obtener_area_por_id(area_id)
            nombre_area = area["nombre"] if area else "Desconocida"
        tramite["nombre_area"] = nombre_area
        return tramite

    # Ahora busca en externos
    tramite = obtener_tramite_externo(pdf_id)
    if tramite:
        tramite["tipo_origen"] = "externo"
        tramite["nombre_remitente"] = tramite.get("remitente")
        return tramite

    return {}

def construir_contexto_pdf(metadatos, texto_pdf):
    contexto = ""
    if metadatos:
        partes = []
        if metadatos.get("tipo_origen") == "externo":
            partes.append("Tipo de documento: Externo")
        elif metadatos.get("tipo_origen") == "interno":
            partes.append("Tipo de documento: Interno")
        if metadatos.get("asunto"):
            partes.append(f"Asunto: {metadatos['asunto']}")
        if metadatos.get("nombre_remitente"):
            partes.append(f"Remitente: {metadatos['nombre_remitente']}")
        if metadatos.get("fecha_registro") or metadatos.get("fecha_envio"):
            partes.append(f"Fecha: {metadatos.get('fecha_registro') or metadatos.get('fecha_envio')}")
        contexto += "\n".join(partes)
    contexto += "\nContenido extraído del PDF:\n" + texto_pdf[:6000]
    return contexto
# --------- FIN AGREGADO PARA MANEJO DE PDF ---------

app = FastAPI()

app.mount("/archivos_tramites", StaticFiles(directory="archivos_tramites"), name="archivos_tramites")
app.mount("/respuestas_tramites", StaticFiles(directory="respuestas_tramites"), name="respuestas_tramites")

# Configuración CORS para React-Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(area_router)
app.include_router(usuario_router)
app.include_router(tramite_externo_router)
app.include_router(tramite_interno_router)
app.include_router(seguimiento_tramite_router)
app.include_router(derivacion_router)
app.include_router(documento_generado_router)

# Carga y configuración del modelo
vectorstore = load_vectorstore()
retriever = None
qa_chain = None
llm_chain = None
llm = OllamaLLM(model="llama2", base_url="http://localhost:11434")

# Plantilla para generar prompts
template = """Eres un asistente que responde en español basado en el siguiente contexto:
{context}

Pregunta: {question}
Respuesta en español:"""
prompt = PromptTemplate(input_variables=["context", "question"], template=template)

# Modelo de datos para las preguntas
class QueryRequest(BaseModel):
    pregunta: str
    usar_bd: bool = False
    chat_history: Optional[List[Tuple[str, str]]] = None
    usuario_id: Optional[int] = None
    usuario: Optional[Dict] = None
    pdf_id: Optional[int] = None  # <-- AGREGADO

def quitar_tildes(texto: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

@app.on_event("startup")
def startup_event():
    global vectorstore, retriever, qa_chain, llm_chain
    if vectorstore:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever, combine_docs_chain_kwargs={"prompt": prompt})
    llm_chain = LLMChain(llm=llm, prompt=prompt)

# Endpoint para reentrenar embeddings
@app.post("/reentrenar")
def reentrenar_embeddings():
    global vectorstore, retriever, qa_chain
    try:
        data = fetch_all_data()
        docs = prepare_docs_from_db(data)
        vectorstore = create_embeddings(docs)
        save_vectorstore(vectorstore)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever, combine_docs_chain_kwargs={"prompt": prompt})
        return {"mensaje": "Embeddings actualizados y modelo reentrenado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reentrenando embeddings: {e}")

def obtener_total(tabla: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {tabla};")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total

def consulta_sql(sql: str, params: tuple = ()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return resultado

def es_mesa_partes(usuario):
    """Devuelve True si el usuario es mesa de partes o admin"""
    return usuario.get("rol") in ["admin", "mesa_partes"]

def contar_estados_tramites(tipo_tramite, area_id=None, usuario_id=None, estado=None):
    """
    Cuenta trámites según tipo, área, usuario y estado.
    tipo_tramite: 'interno' o 'externo'
    """
    try:
        if tipo_tramite not in ["interno", "externo"]:
            return 0
            
        tabla = "tramites_internos" if tipo_tramite == "interno" else "tramites_externos"
        condiciones = []
        parametros = []
        
        # Filtro por área
        if area_id:
            if tipo_tramite == "interno":
                condiciones.append("area_destino_id = %s")
            else:  # externo
                condiciones.append("area_actual_id = %s")
            parametros.append(area_id)
        
        # Filtro por usuario
        if usuario_id:
            if tipo_tramite == "interno":
                condiciones.append("remitente_id = %s")
            else:  # externo
                condiciones.append("usuario_registro_id = %s")
            parametros.append(usuario_id)
        
        # Filtro por estado específico
        if estado:
            condiciones.append("estado = %s")
            parametros.append(estado)
        
        # Construir la consulta SQL
        sql = f"SELECT COUNT(*) FROM {tabla}"
        if condiciones:
            sql += " WHERE " + " AND ".join(condiciones)
        
        resultado = consulta_sql(sql, tuple(parametros)) if parametros else consulta_sql(sql)
        return resultado[0][0] if resultado else 0
        
    except Exception as e:
        print(f"Error al contar estados: {str(e)}")
        return 0

@app.post("/chat")
def chat(req: QueryRequest):
    try:
        pregunta = req.pregunta.strip()
        if not pregunta:
            raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
        pregunta_lower = quitar_tildes(pregunta.lower())
        usuario_id = req.usuario_id
        usuario = req.usuario or {}
        area_id = usuario.get("area_id")
        rol = usuario.get("rol", "").lower()

        # --------- RESPUESTAS INTELIGENTES SOBRE PDF Y METADATOS ---------
        if hasattr(req, "pdf_id") and req.pdf_id and pregunta_es_sobre_pdf(pregunta):
            ruta_pdf = obtener_ruta_pdf_por_id(req.pdf_id)
            if not ruta_pdf:
                return {"respuesta": "No se encontró el PDF seleccionado."}
            texto_pdf = extraer_texto_pdf(ruta_pdf)
            metadatos = obtener_metadatos_pdf(req.pdf_id)
            contexto = construir_contexto_pdf(metadatos, texto_pdf)

            # --- BLOQUE AGREGADO: RESPUESTA DIRECTA A "¿QUIÉN ENVIÓ ESTE DOCUMENTO?" ---
            if (
                "quien envio" in pregunta_lower or
                "quién envió" in pregunta_lower or
                "quien lo envio" in pregunta_lower or
                "quién lo envió" in pregunta_lower
            ):
                tipo = metadatos.get("tipo_origen")
                remitente = metadatos.get("nombre_remitente", "Desconocido")
                if tipo == "externo":
                    respuesta = f"El documento fue enviado por {remitente} (trámite externo)."
                elif tipo == "interno":
                    area = metadatos.get("nombre_area", "Desconocida")
                    respuesta = f"El documento fue enviado por {remitente} (trámite interno) del área {area}."
                else:
                    respuesta = "No se pudo determinar quién envió el documento."
                return {"respuesta": respuesta, "chat_history": req.chat_history or []}

            # --- FIN BLOQUE AGREGADO ---
            
            # Prompt personalizado para resumen o tema
            if "de que trata" in pregunta_lower or "de qué trata" in pregunta_lower or "resumen" in pregunta_lower:
                prompt_resumen = (
                    "Analiza el siguiente contexto del documento y responde de forma natural en español, "
                    "comenzando con: 'El documento trata de ...'. Si puedes, agrega un resumen en una o dos frases.\n"
                    f"{contexto}\n\nPregunta: {pregunta}\nRespuesta en español:"
                )
                respuesta_pdf = llm(prompt_resumen)
                return {"respuesta": respuesta_pdf.strip(), "chat_history": req.chat_history or []}
            else:
                # Para otras preguntas, como "fecha", etc
                prompt_otros = (
                    "Responde en español usando SOLO la información del contexto y el contenido del documento.\n"
                    f"{contexto}\n\nPregunta: {pregunta}\nRespuesta en español:"
                )
                respuesta_pdf = llm(prompt_otros)
                return {"respuesta": respuesta_pdf.strip(), "chat_history": req.chat_history or []}
        # --------- FIN RESPUESTAS PDF ---------
        
        # --- CONSULTAS PERSONALES ---
        if "mi nombre" in pregunta_lower:
            nombre = usuario.get("nombre", "No se pudo obtener tu nombre.")
            return {"respuesta": f"Tu nombre es: {nombre}", "chat_history": req.chat_history or []}
        if "mi area" in pregunta_lower or "mi área" in pregunta_lower:
            from servicios.area import obtener_area
            area = obtener_area(area_id) if area_id else None
            area_nombre = area["nombre"] if area else "No se encontró tu área."
            return {"respuesta": f"Tu área es: {area_nombre}", "chat_history": req.chat_history or []}
        if "mi rol" in pregunta_lower:
            return {"respuesta": f"Tu rol es: {usuario.get('rol', 'No disponible')}", "chat_history": req.chat_history or []}
        if "mi correo" in pregunta_lower or "mi email" in pregunta_lower:
            return {"respuesta": f"Tu correo es: {usuario.get('email', 'No disponible')}", "chat_history": req.chat_history or []}

        # --- CONSULTAS DE ESTADOS DE TRÁMITES ---
        if req.usar_bd:
            # Consultas para trámites internos
            if any(palabra in pregunta_lower for palabra in ["estado", "estados"]) and "interno" in pregunta_lower:
                if es_mesa_partes(usuario):
                    # Mesa de partes ve todos los estados
                    estados = ['pendiente', 'recibido', 'atendido', 'derivado', 'archivado']
                    conteos = {estado: contar_estados_tramites("interno", estado=estado) for estado in estados}
                    respuesta = "Estados de trámites internos en todo el sistema:\n" + "\n".join(
                        [f"- {estado.capitalize()}: {conteos[estado]}" for estado in estados])
                else:
                    # Usuario normal ve solo los de su área
                    estados = ['pendiente', 'recibido', 'atendido', 'derivado', 'archivado']
                    conteos = {estado: contar_estados_tramites("interno", area_id=area_id, estado=estado) for estado in estados}
                    respuesta = f"Estados de trámites internos en tu área:\n" + "\n".join(
                        [f"- {estado.capitalize()}: {conteos[estado]}" for estado in estados])
                return {"respuesta": respuesta, "chat_history": req.chat_history or []}

            # Consultas para trámites externos
            if any(palabra in pregunta_lower for palabra in ["estado", "estados"]) and "externo" in pregunta_lower:
                if es_mesa_partes(usuario):
                    # Mesa de partes ve todos los estados
                    estados = ['pendiente', 'atendido', 'denegado', 'derivado', 'archivado']
                    conteos = {estado: contar_estados_tramites("externo", estado=estado) for estado in estados}
                    respuesta = "Estados de trámites externos en todo el sistema:\n" + "\n".join(
                        [f"- {estado.capitalize()}: {conteos[estado]}" for estado in estados])
                else:
                    # Usuario normal ve solo los de su área
                    estados = ['pendiente', 'atendido', 'denegado', 'derivado', 'archivado']
                    conteos = {estado: contar_estados_tramites("externo", area_id=area_id, estado=estado) for estado in estados}
                    respuesta = f"Estados de trámites externos en tu área:\n" + "\n".join(
                        [f"- {estado.capitalize()}: {conteos[estado]}" for estado in estados])
                return {"respuesta": respuesta, "chat_history": req.chat_history or []}

            # Consultas específicas por estado
            for estado in ['pendiente', 'recibido', 'atendido', 'denegado', 'derivado', 'archivado']:
                if estado in pregunta_lower:
                    if "interno" in pregunta_lower:
                        if es_mesa_partes(usuario):
                            total = contar_estados_tramites("interno", estado=estado)
                            respuesta = f"Hay {total} trámites internos en estado '{estado}' en todo el sistema."
                        else:
                            total = contar_estados_tramites("interno", area_id=area_id, estado=estado)
                            respuesta = f"Hay {total} trámites internos en estado '{estado}' en tu área."
                        return {"respuesta": respuesta, "chat_history": req.chat_history or []}
                    elif "externo" in pregunta_lower:
                        if es_mesa_partes(usuario):
                            total = contar_estados_tramites("externo", estado=estado)
                            respuesta = f"Hay {total} trámites externos en estado '{estado}' en todo el sistema."
                        else:
                            total = contar_estados_tramites("externo", area_id=area_id, estado=estado)
                            respuesta = f"Hay {total} trámites externos en estado '{estado}' en tu área."
                        return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        # --- CONSULTAS GLOBALES/ADMIN/MESA DE PARTES ---
        if req.usar_bd and es_mesa_partes(usuario):
            # Usuarios/áreas solo para admin y mesa de partes
            if "cuantos usuarios" in pregunta_lower or "total de usuarios" in pregunta_lower:
                sql = "SELECT COUNT(*) FROM usuarios;"
                resultado = consulta_sql(sql)
                total = resultado[0][0] if resultado else 0
                return {"respuesta": f"El total de usuarios registrados es {total}.", "chat_history": req.chat_history or []}
            if "cuantos areas" in pregunta_lower or "total de areas" in pregunta_lower:
                sql = "SELECT COUNT(*) FROM areas;"
                resultado = consulta_sql(sql)
                total = resultado[0][0] if resultado else 0
                return {"respuesta": f"El total de áreas registradas es {total}.", "chat_history": req.chat_history or []}
            if "usuarios en el sistema" in pregunta_lower or "lista de usuarios" in pregunta_lower:
                sql = "SELECT nombre, username, rol FROM usuarios;"
                resultado = consulta_sql(sql)
                if resultado:
                    lista = "\n".join([f"- {n} ({u}), rol: {r}" for n, u, r in resultado])
                    return {"respuesta": f"Usuarios registrados:\n{lista}", "chat_history": req.chat_history or []}
                return {"respuesta": "No hay usuarios registrados.", "chat_history": req.chat_history or []}
            # Mesa de partes puede ver TODOS los trámites internos y externos:
            if "tramites internos" in pregunta_lower and not any(palabra in pregunta_lower for palabra in ["estado", "estados"]):
                sql = "SELECT COUNT(*) FROM tramites_internos;"
                resultado = consulta_sql(sql)
                total = resultado[0][0] if resultado else 0
                return {"respuesta": f"En total hay {total} trámites internos registrados.", "chat_history": req.chat_history or []}
            if "tramites externos" in pregunta_lower and not any(palabra in pregunta_lower for palabra in ["estado", "estados"]):
                sql = "SELECT COUNT(*) FROM tramites_externos;"
                resultado = consulta_sql(sql)
                total = resultado[0][0] if resultado else 0
                return {"respuesta": f"En total hay {total} trámites externos registrados.", "chat_history": req.chat_history or []}

        # --- CONSULTAS RESTRINGIDAS a su área para otros roles ---
        if req.usar_bd and not es_mesa_partes(usuario):
            # Trámites internos en su área (como jefe, auxiliar, etc.)
            if "tramites internos" in pregunta_lower and not any(palabra in pregunta_lower for palabra in ["estado", "estados"]):
                sql = "SELECT COUNT(*) FROM tramites_internos WHERE area_destino_id = %s;"
                resultado = consulta_sql(sql, (area_id,))
                total = resultado[0][0] if resultado else 0
                return {"respuesta": f"En tu área hay {total} trámites internos derivados a tu área.", "chat_history": req.chat_history or []}
            if "tramites externos" in pregunta_lower and not any(palabra in pregunta_lower for palabra in ["estado", "estados"]):
                sql = "SELECT COUNT(*) FROM tramites_externos WHERE area_actual_id = %s;"
                resultado = consulta_sql(sql, (area_id,))
                total = resultado[0][0] if resultado else 0
                return {"respuesta": f"En tu área hay {total} trámites externos actualmente.", "chat_history": req.chat_history or []}
            # No puede ver usuarios ni áreas, responde acceso denegado
            if "usuarios" in pregunta_lower or "areas" in pregunta_lower:
                return {"respuesta": "No tienes autorización para consultar usuarios o áreas. Solo mesa de partes o admin puede hacerlo.", "chat_history": req.chat_history or []}

        # --- CONSULTAS SIEMPRE PERSONALES (para todos los roles) ---
        if req.usar_bd and (
            "mis tramites internos" in pregunta_lower or "mis trámites internos" in pregunta_lower
        ) and not any(palabra in pregunta_lower for palabra in ["estado", "estados"]):
            if not usuario_id:
                return {"respuesta": "No se pudo identificar el usuario actual."}
            sql = "SELECT COUNT(*) FROM tramites_internos WHERE remitente_id = %s;"
            resultado = consulta_sql(sql, (usuario_id,))
            total = resultado[0][0] if resultado else 0
            return {"respuesta": f"Tienes {total} trámites internos registrados.", "chat_history": req.chat_history or []}
        if req.usar_bd and (
            "mis tramites externos" in pregunta_lower or "mis trámites externos" in pregunta_lower
        ) and not any(palabra in pregunta_lower for palabra in ["estado", "estados"]):
            if not usuario_id:
                return {"respuesta": "No se pudo identificar el usuario actual."}
            sql = "SELECT COUNT(*) FROM tramites_externos WHERE usuario_registro_id = %s;"
            resultado = consulta_sql(sql, (usuario_id,))
            total = resultado[0][0] if resultado else 0
            return {"respuesta": f"Tienes {total} trámites externos registrados.", "chat_history": req.chat_history or []}
        if req.usar_bd and (
            "mis documentos generados" in pregunta_lower or "que documentos he generado" in pregunta_lower
        ):
            if not usuario_id:
                return {"respuesta": "No se pudo identificar el usuario actual."}
            sql = "SELECT COUNT(*) FROM documentos_generados WHERE usuario_generador_id = %s;"
            resultado = consulta_sql(sql, (usuario_id,))
            total = resultado[0][0] if resultado else 0
            return {"respuesta": f"Has generado {total} documentos.", "chat_history": req.chat_history or []}

        # --- DEFAULT: LLM / QA semántico ---
        if not req.usar_bd:
            respuesta = llm_chain.run({"context": "", "question": pregunta})
        else:
            if not qa_chain:
                raise HTTPException(status_code=400, detail="Modelo no entrenado. Ejecuta /reentrenar primero.")
            chat_hist = req.chat_history or []
            resultado = qa_chain({"question": pregunta, "chat_history": chat_hist})
            respuesta = resultado["answer"]

        chat_hist = req.chat_history or []
        chat_hist.append((pregunta, respuesta))
        return {"respuesta": respuesta, "chat_history": chat_hist}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    