# servicios/seguimiento_tramite.py

from db import get_connection

def crear_seguimiento_tramite(datos):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO seguimiento_tramites (
            tramite_id, tramite_type, accion, descripcion,
            usuario_id, area_id, adjunto, observaciones
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, fecha_hora;
    """, (
        datos["tramite_id"], datos["tramite_type"], datos["accion"], datos["descripcion"],
        datos["usuario_id"], datos.get("area_id"), datos.get("adjunto"), datos.get("observaciones")
    ))
    seguimiento_id, fecha_hora = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return seguimiento_id, fecha_hora

def obtener_seguimientos_tramite():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tramite_id, tramite_type, accion, descripcion,
                usuario_id, area_id, adjunto, observaciones, fecha_hora
        FROM seguimiento_tramites;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "tramite_id": r[1],
            "tramite_type": r[2],
            "accion": r[3],
            "descripcion": r[4],
            "usuario_id": r[5],
            "area_id": r[6],
            "adjunto": r[7],
            "observaciones": r[8],
            "fecha_hora": r[9]
        }
        for r in rows
    ]

def obtener_seguimiento_tramite(seguimiento_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tramite_id, tramite_type, accion, descripcion,
                usuario_id, area_id, adjunto, observaciones, fecha_hora
        FROM seguimiento_tramites WHERE id = %s;
    """, (seguimiento_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {
            "id": r[0],
            "tramite_id": r[1],
            "tramite_type": r[2],
            "accion": r[3],
            "descripcion": r[4],
            "usuario_id": r[5],
            "area_id": r[6],
            "adjunto": r[7],
            "observaciones": r[8],
            "fecha_hora": r[9]
        }
    return None

def actualizar_seguimiento_tramite(seguimiento_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    campos = []
    valores = []
    for campo in ["accion", "descripcion", "area_id", "adjunto", "observaciones"]:
        if datos.get(campo) is not None:
            campos.append(f"{campo}=%s")
            valores.append(datos[campo])
    if not campos:
        cur.close()
        conn.close()
        return False
    valores.append(seguimiento_id)
    consulta = f"UPDATE seguimiento_tramites SET {', '.join(campos)} WHERE id=%s RETURNING id;"
    cur.execute(consulta, tuple(valores))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None

def eliminar_seguimiento_tramite(seguimiento_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM seguimiento_tramites WHERE id=%s RETURNING id;", (seguimiento_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None

def obtener_seguimiento_de_tramite_externo(tramite_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            s.id, s.fecha_hora, s.accion, s.descripcion, s.adjunto, 
            COALESCE(u.nombre, '') as usuario, 
            COALESCE(a.nombre, '') as area,
            s.observaciones
        FROM seguimiento_tramites s
        LEFT JOIN usuarios u ON u.id = s.usuario_id
        LEFT JOIN areas a ON a.id = s.area_id
        WHERE s.tramite_id = %s AND s.tramite_type = 'externo'
        ORDER BY s.fecha_hora ASC;
    """, (tramite_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": row[0],
            "fecha_hora": row[1],
            "accion": row[2],
            "descripcion": row[3],
            "adjunto": row[4],
            "usuario": row[5],
            "area": row[6],
            "observaciones": row[7],
        }
        for row in rows
    ]
