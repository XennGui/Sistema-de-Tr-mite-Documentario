import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "municipio")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "admin")
DB_PORT = os.getenv("DB_PORT", "5436")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def fetch_all_data():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM usuarios;")
    usuarios = cur.fetchall()

    cur.execute("SELECT * FROM areas;")
    areas = cur.fetchall()

    cur.execute("SELECT * FROM tramites_externos;")
    tramites_externos = cur.fetchall()

    cur.execute("SELECT * FROM tramites_internos;")
    tramites_internos = cur.fetchall()

    cur.execute("SELECT * FROM seguimiento_tramites;")
    seguimiento_tramites = cur.fetchall()

    cur.execute("SELECT * FROM derivaciones;")
    derivaciones = cur.fetchall()

    cur.execute("SELECT * FROM documentos_generados;")
    documentos_generados = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "usuarios": usuarios,
        "areas": areas,
        "tramites_externos": tramites_externos,
        "tramites_internos": tramites_internos,
        "seguimiento_tramites": seguimiento_tramites,
        "derivaciones": derivaciones,
        "documentos_generados": documentos_generados
    }
