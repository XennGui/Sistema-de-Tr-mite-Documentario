# servicios/area.py

from db import get_connection

def crear_area(nombre, descripcion):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO areas (nombre, descripcion) VALUES (%s, %s) RETURNING id;", (nombre, descripcion))
    area_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return area_id

def obtener_areas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, descripcion FROM areas;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "descripcion": r[2]} for r in rows]

def obtener_area(area_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, descripcion FROM areas WHERE id = %s;", (area_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {"id": r[0], "nombre": r[1], "descripcion": r[2]}
    return None

def obtener_area_por_id(area_id):
    # ejemplo usando SQL, cámbialo según tu lógica y base de datos
    from db import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM areas WHERE id = %s", (area_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"id": row[0], "nombre": row[1]}
    return None

def actualizar_area(area_id, nombre, descripcion):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE areas SET nombre=%s, descripcion=%s WHERE id=%s RETURNING id;", (nombre, descripcion, area_id))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None

def eliminar_area(area_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM areas WHERE id=%s RETURNING id;", (area_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None