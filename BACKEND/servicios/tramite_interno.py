# servicios/tramite_interno.py

from db import get_connection

def crear_tramite_interno(datos):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tramites_internos (
            numero_referencia, asunto, contenido, folios, archivo,
            remitente_id, area_origen_id, area_destino_id, estado, prioridad,
            fecha_vencimiento
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, fecha_envio;
    """, (
        datos["numero_referencia"], datos["asunto"], datos["contenido"],
        datos.get("folios", 1), datos.get("archivo"),
        datos["remitente_id"], datos["area_origen_id"], datos["area_destino_id"],
        datos.get("estado", "pendiente"), datos.get("prioridad", 3),
        datos.get("fecha_vencimiento")
    ))
    tramite_id, fecha_envio = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return tramite_id, fecha_envio

def obtener_tramites_internos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, numero_referencia, asunto, contenido, folios, archivo,
                remitente_id, area_origen_id, area_destino_id, estado, prioridad,
                fecha_envio, fecha_recepcion, fecha_vencimiento
        FROM tramites_internos;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "numero_referencia": r[1],
            "asunto": r[2],
            "contenido": r[3],
            "folios": r[4],
            "archivo": r[5],
            "remitente_id": r[6],
            "area_origen_id": r[7],
            "area_destino_id": r[8],
            "estado": r[9],
            "prioridad": r[10],
            "fecha_envio": r[11],
            "fecha_recepcion": r[12],
            "fecha_vencimiento": r[13],
        }
        for r in rows
    ]

def obtener_tramite_interno(tramite_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, numero_referencia, asunto, contenido, folios, archivo,
                remitente_id, area_origen_id, area_destino_id, estado, prioridad,
                fecha_envio, fecha_recepcion, fecha_vencimiento
        FROM tramites_internos WHERE id = %s;
    """, (tramite_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {
            "id": r[0],
            "numero_referencia": r[1],
            "asunto": r[2],
            "contenido": r[3],
            "folios": r[4],
            "archivo": r[5],
            "remitente_id": r[6],
            "area_origen_id": r[7],
            "area_destino_id": r[8],
            "estado": r[9],
            "prioridad": r[10],
            "fecha_envio": r[11],
            "fecha_recepcion": r[12],
            "fecha_vencimiento": r[13],
        }
    return None

def actualizar_tramite_interno(tramite_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    campos = []
    valores = []
    for campo in [
        "asunto", "contenido", "folios", "archivo", "remitente_id",
        "area_origen_id", "area_destino_id", "estado", "prioridad",
        "fecha_recepcion", "fecha_vencimiento"
    ]:
        if datos.get(campo) is not None:
            campos.append(f"{campo}=%s")
            valores.append(datos[campo])
    if not campos:
        cur.close()
        conn.close()
        return False
    valores.append(tramite_id)
    consulta = f"UPDATE tramites_internos SET {', '.join(campos)} WHERE id=%s RETURNING id;"
    cur.execute(consulta, tuple(valores))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None

def eliminar_tramite_interno(tramite_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tramites_internos WHERE id=%s RETURNING id;", (tramite_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None

def obtener_tramites_internos_por_area(area_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, numero_referencia, asunto, contenido, folios, archivo,
            remitente_id, area_origen_id, area_destino_id, estado, prioridad,
            fecha_envio, fecha_recepcion, fecha_vencimiento
        FROM tramites_internos
        WHERE area_destino_id = %s
        ORDER BY fecha_envio DESC;
    """, (area_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "numero_referencia": r[1],
            "asunto": r[2],
            "contenido": r[3],
            "folios": r[4],
            "archivo": r[5],
            "remitente_id": r[6],
            "area_origen_id": r[7],
            "area_destino_id": r[8],
            "estado": r[9],
            "prioridad": r[10],
            "fecha_envio": r[11],
            "fecha_recepcion": r[12],
            "fecha_vencimiento": r[13],
        }
        for r in rows
    ]

