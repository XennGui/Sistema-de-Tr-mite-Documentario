from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rutas.area import router as area_router
from rutas.usuario import router as usuario_router
from rutas.tramite_externo import router as tramite_externo_router
from pydantic import BaseModel
from typing import Optional, List, Tuple
from embeddings import create_embeddings, save_vectorstore, load_vectorstore, prepare_docs_from_db
from db import fetch_all_data, get_connection
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain_ollama import OllamaLLM
import unicodedata
import re
import dateparser

app = FastAPI()

# Configuración CORS para React (puerto 5173 por defecto en Vite)
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

# Funciones para consultas SQL
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

@app.post("/chat")
def chat(req: QueryRequest):
    try:
        pregunta = req.pregunta.strip()
        if not pregunta:
            raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

        pregunta_lower = quitar_tildes(pregunta.lower())

        # CONSULTAS MUNICIPALES
        if req.usar_bd and (
            "cuantos usuarios" in pregunta_lower or
            "total de usuarios" in pregunta_lower or
            "cantidad de usuarios" in pregunta_lower
        ):
            total = obtener_total("usuarios")
            respuesta = f"En total tienes {total} usuarios registrados."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        if req.usar_bd and (
            "cuantos tramites externos" in pregunta_lower or
            "total de tramites externos" in pregunta_lower or
            "cantidad de tramites externos" in pregunta_lower
        ):
            total = obtener_total("tramites_externos")
            respuesta = f"En total tienes {total} trámites externos registrados."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        if req.usar_bd and (
            "cuantos tramites internos" in pregunta_lower or
            "total de tramites internos" in pregunta_lower or
            "cantidad de tramites internos" in pregunta_lower
        ):
            total = obtener_total("tramites_internos")
            respuesta = f"En total tienes {total} trámites internos registrados."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        if req.usar_bd and (
            "cuantos areas" in pregunta_lower or
            "total de areas" in pregunta_lower or
            "cantidad de areas" in pregunta_lower
        ):
            total = obtener_total("areas")
            respuesta = f"En total tienes {total} áreas registradas."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        if req.usar_bd and (
            "cuantos documentos generados" in pregunta_lower or
            "total de documentos generados" in pregunta_lower or
            "cantidad de documentos generados" in pregunta_lower
        ):
            total = obtener_total("documentos_generados")
            respuesta = f"En total tienes {total} documentos generados en el sistema."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        # Consultar trámites pendientes
        if req.usar_bd and (
            "tramites pendientes" in pregunta_lower
        ):
            sql = "SELECT COUNT(*) FROM tramites_externos WHERE estado = 'pendiente';"
            resultado = consulta_sql(sql)
            total = resultado[0][0] if resultado else 0
            respuesta = f"Hay {total} trámites externos pendientes."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        # Consultar trámites por área
        if req.usar_bd and (
            "tramites por area" in pregunta_lower or "trámites por área" in pregunta_lower
        ):
            sql = """
                SELECT a.nombre, COUNT(te.id)
                FROM tramites_externos te
                LEFT JOIN areas a ON te.area_actual_id = a.id
                GROUP BY a.nombre
                ORDER BY COUNT(te.id) DESC;
            """
            resultado = consulta_sql(sql)
            if resultado:
                respuesta = "Trámites externos por área:\n"
                for area, cantidad in resultado:
                    respuesta += f"- {area}: {cantidad}\n"
            else:
                respuesta = "No se encontraron trámites registrados por área."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        # Consultar seguimiento de un trámite externo por número de expediente
        if req.usar_bd and (
            "seguimiento del tramite" in pregunta_lower or "seguimiento del trámite" in pregunta_lower
        ):
            # Busca el número de expediente en la pregunta (asume formato: SEGUIMIENTO DEL TRAMITE 2024-001)
            match = re.search(r"tramite[s]?\s+([a-zA-Z0-9\-]+)", pregunta_lower)
            if match:
                num_expediente = match.group(1)
                sql = """
                    SELECT st.accion, st.descripcion, st.fecha_hora, u.nombre as usuario, a.nombre as area
                    FROM seguimiento_tramites st
                    LEFT JOIN usuarios u ON st.usuario_id = u.id
                    LEFT JOIN areas a ON st.area_id = a.id
                    LEFT JOIN tramites_externos te ON st.tramite_id = te.id
                    WHERE st.tramite_type = 'externo' AND te.numero_expediente = %s
                    ORDER BY st.fecha_hora ASC;
                """
                resultado = consulta_sql(sql, (num_expediente,))
                if resultado:
                    respuesta = f"Seguimiento del trámite externo {num_expediente}:\n"
                    for accion, descripcion, fecha, usuario, area in resultado:
                        respuesta += f"- [{fecha}] {accion} por {usuario} en {area}. Detalle: {descripcion}\n"
                else:
                    respuesta = f"No se encontró seguimiento para el trámite externo {num_expediente}."
            else:
                respuesta = "No se encontró el número de expediente en la pregunta."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        # Consultar trámites atendidos en un rango de fechas
        if req.usar_bd and (
            "tramites atendidos" in pregunta_lower and ("entre" in pregunta_lower or "desde" in pregunta_lower)
        ):
            fechas = re.findall(r"\d{4}-\d{2}-\d{2}", pregunta)
            if len(fechas) >= 2:
                fecha_ini, fecha_fin = fechas[0], fechas[1]
                sql = """
                    SELECT COUNT(*) FROM tramites_externos
                    WHERE estado = 'atendido' AND fecha_registro >= %s AND fecha_registro <= %s;
                """
                resultado = consulta_sql(sql, (fecha_ini, fecha_fin))
                total = resultado[0][0] if resultado else 0
                respuesta = f"Se han atendido {total} trámites externos entre {fecha_ini} y {fecha_fin}."
            else:
                respuesta = "No se encontraron dos fechas válidas en la pregunta."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        # Consultar trámites de un remitente (por DNI/RUC)
        if req.usar_bd and (
            ("tramites de" in pregunta_lower or "trámites de" in pregunta_lower) and ("dni" in pregunta_lower or "ruc" in pregunta_lower)
        ):
            match = re.search(r"(dni|ruc)\s*:?[\s\-]?([0-9]+)", pregunta_lower)
            if match:
                dni_ruc = match.group(2)
                sql = """
                    SELECT numero_expediente, asunto, estado, fecha_registro
                    FROM tramites_externos
                    WHERE dni_ruc = %s
                    ORDER BY fecha_registro DESC;
                """
                resultado = consulta_sql(sql, (dni_ruc,))
                if resultado:
                    respuesta = f"Trámites del remitente con {match.group(1).upper()} {dni_ruc}:\n"
                    for exp, asunto, estado, fecha in resultado:
                        respuesta += f"- [{fecha}] Expediente: {exp} | Estado: {estado} | Asunto: {asunto}\n"
                else:
                    respuesta = f"No se hallaron trámites para el {match.group(1).upper()} {dni_ruc}."
            else:
                respuesta = "No se encontró un DNI o RUC válido en la pregunta."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        # Consultar documentos generados por usuario
        if req.usar_bd and (
            ("documentos generados por usuario" in pregunta_lower or "documentos firmados por usuario" in pregunta_lower)
        ):
            match = re.search(r"usuario[s]?\s+([a-zA-ZáéíóúÁÉÍÓÚ0-9\s\-]+)", pregunta_lower)
            if match:
                usuario_nombre = match.group(1).strip()
                sql = """
                    SELECT dg.tipo_documento, dg.fecha_creacion, dg.firmado
                    FROM documentos_generados dg
                    JOIN usuarios u ON dg.usuario_generador_id = u.id
                    WHERE LOWER(u.nombre) LIKE %s
                    ORDER BY dg.fecha_creacion DESC;
                """
                resultado = consulta_sql(sql, (f"%{usuario_nombre.lower()}%",))
                if resultado:
                    respuesta = f"Documentos generados por {usuario_nombre}:\n"
                    for tipo, fecha, firmado in resultado:
                        firmado_txt = "Sí" if firmado else "No"
                        respuesta += f"- [{fecha}] Tipo: {tipo} | Firmado: {firmado_txt}\n"
                else:
                    respuesta = f"No se hallaron documentos generados por {usuario_nombre}."
            else:
                respuesta = "No se encontró el nombre del usuario en la pregunta."
            return {"respuesta": respuesta, "chat_history": req.chat_history or []}

        # Si no es una consulta directa a BD, usa el LLM (con o sin recuperación semántica)
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
