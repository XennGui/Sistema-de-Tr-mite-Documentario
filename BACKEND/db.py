import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env (como BD_HOST, BD_USER, etc.)
load_dotenv()

# Obtiene las configuraciones de conexión a la base de datos desde variables de entorno
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "municipio")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "admin")
DB_PORT = os.getenv("DB_PORT", "5436")

# Función para crear y retornar una conexión a la base de datos usando psycopg2
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

# Funcion para obtener todos los datos de tus tablas principales
def fetch_all_data():
    # Obtiene la conexión
    conn = get_connection()
    # Crea un cursor que devuelve resultados como diccionarios en lugar de tuplas
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Ejecuta consulta para obtener todos los usuarios
    cur.execute("SELECT * FROM usuarios;")
    usuarios = cur.fetchall()

    # Ejecuta consulta para obtener todas las áreas
    cur.execute("SELECT * FROM areas;")
    areas = cur.fetchall()

    # Ejecuta consulta para obtener todos los trámites externos
    cur.execute("SELECT * FROM tramites_externos;")
    tramites_externos = cur.fetchall()

    # Ejecuta consulta para obtener todos los trámites internos
    cur.execute("SELECT * FROM tramites_internos;")
    tramites_internos = cur.fetchall()

    # Ejecuta consulta para obtener todo el seguimiento de trámites
    cur.execute("SELECT * FROM seguimiento_tramites;")
    seguimiento_tramites = cur.fetchall()

    # Ejecuta consulta para obtener todas las derivaciones
    cur.execute("SELECT * FROM derivaciones;")
    derivaciones = cur.fetchall()

    # Ejecuta consulta para obtener todos los documentos generados
    cur.execute("SELECT * FROM documentos_generados;")
    documentos_generados = cur.fetchall()

    # Cierra el cursor y la conexión para liberar recursos
    cur.close()
    conn.close()

    # Devuelve un diccionario con los datos obtenidos
    return {
        "usuarios": usuarios,
        "areas": areas,
        "tramites_externos": tramites_externos,
        "tramites_internos": tramites_internos,
        "seguimiento_tramites": seguimiento_tramites,
        "derivaciones": derivaciones,
        "documentos_generados": documentos_generados
    }