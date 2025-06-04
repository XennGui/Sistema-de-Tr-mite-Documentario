# embeddings.py

# Importaciones necesarias para embeddings, indexación vectorial, documentos y manejo de archivos
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from typing import List
import os
import pickle

# Define la ruta base del archivo actual para construir rutas relativas seguras
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define la ruta donde se guardará el índice vectorial FAISS serializado
VECTORSTORE_PATH = os.path.join(BASE_DIR, "vectorstore", "faiss_index.pkl")

def create_embeddings(docs: List[Document]):
    """
    Crea embeddings (representaciones vectoriales) para una lista de documentos
    usando un modelo preentrenado de Hugging Face y construye un índice FAISS.
    
    Args:
        docs (List[Document]): Lista de documentos con texto y metadatos.
    
    Returns:
        FAISS: Indice vectorial con embeddings y metadatos.
    """
    # Inicializa el modelo de embeddings basado en transformers
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Extrae el texto de cada documento para crear embeddings
    texts = [doc.page_content for doc in docs]
    # Extrae los metadatos de cada documento para asociarlos en el indice
    metadatas = [doc.metadata for doc in docs]

    # Crea un indice FAISS a partir de los textos y el modelo de embeddings
    vectorstore = FAISS.from_texts(texts, embedding_model, metadatas=metadatas)
    
    # Retorna el indice vectorial para futuras busquedas o almacenamiento
    return vectorstore

def save_vectorstore(vectorstore):
    """
    Guarda el indice FAISS serializado en disco usando pickle.
    Crea la carpeta si no existe.
    
    Args:
        vectorstore (FAISS): Indice vectorial a guardar.
    """
    # Crea la carpeta destino si no existe (evita error al guardar)
    os.makedirs(os.path.dirname(VECTORSTORE_PATH), exist_ok=True)
    
    # Abre el archivo en modo escritura binaria y guarda el indice con pickle
    with open(VECTORSTORE_PATH, "wb") as f:
        pickle.dump(vectorstore, f)

def load_vectorstore():
    """
    Carga el indice FAISS serializado desde disco si existe.
    
    Returns:
        FAISS o None: Indice cargado o None si no existe.
    """
    # Verifica que el archivo exista para evitar error de carga
    if not os.path.exists(VECTORSTORE_PATH):
        return None
    
    # Abre el archivo en modo lectura binaria y carga el indice con pickle
    with open(VECTORSTORE_PATH, "rb") as f:
        return pickle.load(f)

def prepare_docs_from_db(data):
    """
    Prepara una lista de documentos formateados a partir de datos obtenidos de la BD.
    Convierte los datos en textos legibles con metadatos para embedding e indexación.
    
    Args:
        data (dict): Diccionario con listas bajo claves de tablas reales del municipio.
    
    Returns:
        List[Document]: Lista de documentos con texto y metadatos.
    """
    docs = []

    # Obtiene las listas de cada tabla, si no existe devuelve lista vacía
    usuarios = data.get("usuarios", [])
    areas = data.get("areas", [])
    tramites_externos = data.get("tramites_externos", [])
    tramites_internos = data.get("tramites_internos", [])
    seguimiento_tramites = data.get("seguimiento_tramites", [])
    derivaciones = data.get("derivaciones", [])
    documentos_generados = data.get("documentos_generados", [])

    # Usuarios
    for u in usuarios:
        texto = (
            f"Usuario ID {u.get('id', '')}: "
            f"Nombre: {u.get('nombre', '')}, "
            f"Email: {u.get('email', '')}, "
            f"Usuario: {u.get('username', '')}, "
            f"Rol: {u.get('rol', '')}, "
            f"Área ID: {u.get('area_id', '')}."
        )
        docs.append(Document(
            page_content=texto,
            metadata={
                'tipo': 'usuario',
                'id': u.get('id'),
                'nombre': u.get('nombre'),
                'email': u.get('email'),
                'username': u.get('username'),
                'rol': u.get('rol'),
                'area_id': u.get('area_id')
            }
        ))

    # Áreas
    for a in areas:
        texto = (
            f"Área ID {a.get('id', '')}: "
            f"Nombre: {a.get('nombre', '')}, "
            f"Descripción: {a.get('descripcion', '')}."
        )
        docs.append(Document(
            page_content=texto,
            metadata={
                'tipo': 'area',
                'id': a.get('id'),
                'nombre': a.get('nombre'),
                'descripcion': a.get('descripcion')
            }
        ))

    # Trámites externos
    for t in tramites_externos:
        texto = (
            f"Trámite Externo ID {t.get('id', '')}: "
            f"Número de expediente: {t.get('numero_expediente', '')}, "
            f"Remitente: {t.get('remitente', '')}, "
            f"Asunto: {t.get('asunto', '')}, "
            f"Tipo documento: {t.get('tipo_documento', '')}, "
            f"Folios: {t.get('folios', '')}, "
            f"Estado: {t.get('estado', '')}, "
            f"Prioridad: {t.get('prioridad', '')}, "
            f"Fecha registro: {t.get('fecha_registro', '')}, "
            f"Área actual ID: {t.get('area_actual_id', '')}."
        )
        docs.append(Document(
            page_content=texto,
            metadata={
                'tipo': 'tramite_externo',
                'id': t.get('id'),
                'numero_expediente': t.get('numero_expediente'),
                'remitente': t.get('remitente'),
                'asunto': t.get('asunto'),
                'tipo_documento': t.get('tipo_documento'),
                'folios': t.get('folios'),
                'estado': t.get('estado'),
                'prioridad': t.get('prioridad'),
                'fecha_registro': str(t.get('fecha_registro')),
                'area_actual_id': t.get('area_actual_id')
            }
        ))

    # Trámites internos
    for t in tramites_internos:
        texto = (
            f"Trámite Interno ID {t.get('id', '')}: "
            f"Número referencia: {t.get('numero_referencia', '')}, "
            f"Asunto: {t.get('asunto', '')}, "
            f"Remitente ID: {t.get('remitente_id', '')}, "
            f"Área origen ID: {t.get('area_origen_id', '')}, "
            f"Área destino ID: {t.get('area_destino_id', '')}, "
            f"Estado: {t.get('estado', '')}, "
            f"Prioridad: {t.get('prioridad', '')}, "
            f"Fecha envío: {t.get('fecha_envio', '')}."
        )
        docs.append(Document(
            page_content=texto,
            metadata={
                'tipo': 'tramite_interno',
                'id': t.get('id'),
                'numero_referencia': t.get('numero_referencia'),
                'asunto': t.get('asunto'),
                'remitente_id': t.get('remitente_id'),
                'area_origen_id': t.get('area_origen_id'),
                'area_destino_id': t.get('area_destino_id'),
                'estado': t.get('estado'),
                'prioridad': t.get('prioridad'),
                'fecha_envio': str(t.get('fecha_envio'))
            }
        ))

    # Seguimiento de trámites
    for s in seguimiento_tramites:
        texto = (
            f"Seguimiento ID {s.get('id', '')}: "
            f"Trámite ID: {s.get('tramite_id', '')}, "
            f"Tipo trámite: {s.get('tramite_type', '')}, "
            f"Acción: {s.get('accion', '')}, "
            f"Usuario ID: {s.get('usuario_id', '')}, "
            f"Área ID: {s.get('area_id', '')}, "
            f"Fecha/hora: {s.get('fecha_hora', '')}."
        )
        docs.append(Document(
            page_content=texto,
            metadata={
                'tipo': 'seguimiento_tramite',
                'id': s.get('id'),
                'tramite_id': s.get('tramite_id'),
                'tramite_type': s.get('tramite_type'),
                'accion': s.get('accion'),
                'usuario_id': s.get('usuario_id'),
                'area_id': s.get('area_id'),
                'fecha_hora': str(s.get('fecha_hora'))
            }
        ))

    # Derivaciones
    for d in derivaciones:
        texto = (
            f"Derivación ID {d.get('id', '')}: "
            f"Trámite ID: {d.get('tramite_id', '')}, "
            f"Tipo trámite: {d.get('tramite_type', '')}, "
            f"Área origen ID: {d.get('area_origen_id', '')}, "
            f"Área destino ID: {d.get('area_destino_id', '')}, "
            f"Usuario derivador ID: {d.get('usuario_derivacion_id', '')}, "
            f"Fecha derivación: {d.get('fecha_derivacion', '')}."
        )
        docs.append(Document(
            page_content=texto,
            metadata={
                'tipo': 'derivacion',
                'id': d.get('id'),
                'tramite_id': d.get('tramite_id'),
                'tramite_type': d.get('tramite_type'),
                'area_origen_id': d.get('area_origen_id'),
                'area_destino_id': d.get('area_destino_id'),
                'usuario_derivacion_id': d.get('usuario_derivacion_id'),
                'fecha_derivacion': str(d.get('fecha_derivacion'))
            }
        ))

    # Documentos generados
    for doc in documentos_generados:
        texto = (
            f"Documento generado ID {doc.get('id', '')}: "
            f"Trámite ID: {doc.get('tramite_id', '')}, "
            f"Tipo trámite: {doc.get('tramite_type', '')}, "
            f"Tipo documento: {doc.get('tipo_documento', '')}, "
            f"Fecha creación: {doc.get('fecha_creacion', '')}, "
            f"Firmado: {doc.get('firmado', '')}."
        )
        docs.append(Document(
            page_content=texto,
            metadata={
                'tipo': 'documento_generado',
                'id': doc.get('id'),
                'tramite_id': doc.get('tramite_id'),
                'tramite_type': doc.get('tramite_type'),
                'tipo_documento': doc.get('tipo_documento'),
                'fecha_creacion': str(doc.get('fecha_creacion')),
                'firmado': doc.get('firmado')
            }
        ))

    # Devuelve la lista completa de documentos listos para embedding
    return docs