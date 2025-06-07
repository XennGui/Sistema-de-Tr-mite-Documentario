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

        # --- DATOS PERSONALES ---
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
            if "tramites internos" in pregunta_lower:
                sql = "SELECT COUNT(*) FROM tramites_internos;"
                resultado = consulta_sql(sql)
                total = resultado[0][0] if resultado else 0
                return {"respuesta": f"En total hay {total} trámites internos registrados.", "chat_history": req.chat_history or []}
            if "tramites externos" in pregunta_lower:
                sql = "SELECT COUNT(*) FROM tramites_externos;"
                resultado = consulta_sql(sql)
                total = resultado[0][0] if resultado else 0
                return {"respuesta": f"En total hay {total} trámites externos registrados.", "chat_history": req.chat_history or []}

        # --- CONSULTAS RESTRINGIDAS a su área para otros roles ---
        if req.usar_bd and not es_mesa_partes(usuario):
            # Trámites internos en su área (como jefe, auxiliar, etc.)
            if "tramites internos" in pregunta_lower:
                sql = "SELECT COUNT(*) FROM tramites_internos WHERE area_destino_id = %s;"
                resultado = consulta_sql(sql, (area_id,))
                total = resultado[0][0] if resultado else 0
                return {"respuesta": f"En tu área hay {total} trámites internos derivados a tu área.", "chat_history": req.chat_history or []}
            if "tramites externos" in pregunta_lower:
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
        ):
            if not usuario_id:
                return {"respuesta": "No se pudo identificar el usuario actual."}
            sql = "SELECT COUNT(*) FROM tramites_internos WHERE remitente_id = %s;"
            resultado = consulta_sql(sql, (usuario_id,))
            total = resultado[0][0] if resultado else 0
            return {"respuesta": f"Tienes {total} trámites internos registrados.", "chat_history": req.chat_history or []}
        if req.usar_bd and (
            "mis tramites externos" in pregunta_lower or "mis trámites externos" in pregunta_lower
        ):
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
    