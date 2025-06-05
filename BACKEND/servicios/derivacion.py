# servicios/derivacion.py

from db import get_connection

def crear_derivacion(datos):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO derivaciones (
            tramite_id, tramite_type, area_origen_id, area_destino_id,
            usuario_derivacion_id, instrucciones, fecha_limite
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, fecha_derivacion;
    """, (
        datos["tramite_id"], datos["tramite_type"], datos["area_origen_id"],
        datos["area_destino_id"], datos["usuario_derivacion_id"],
        datos.get("instrucciones"), datos.get("fecha_limite")
    ))
    derivacion_id, fecha_derivacion = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return derivacion_id, fecha_derivacion

def obtener_derivaciones():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tramite_id, tramite_type, area_origen_id, area_destino_id,
                usuario_derivacion_id, fecha_derivacion, instrucciones, fecha_limite
        FROM derivaciones;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "tramite_id": r[1],
            "tramite_type": r[2],
            "area_origen_id": r[3],
            "area_destino_id": r[4],
            "usuario_derivacion_id": r[5],
            "fecha_derivacion": r[6],
            "instrucciones": r[7],
            "fecha_limite": r[8]
        }
        for r in rows
    ]

def obtener_derivacion(derivacion_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tramite_id, tramite_type, area_origen_id, area_destino_id,
                usuario_derivacion_id, fecha_derivacion, instrucciones, fecha_limite
        FROM derivaciones WHERE id = %s;
    """, (derivacion_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {
            "id": r[0],
            "tramite_id": r[1],
            "tramite_type": r[2],
            "area_origen_id": r[3],
            "area_destino_id": r[4],
            "usuario_derivacion_id": r[5],
            "fecha_derivacion": r[6],
            "instrucciones": r[7],
            "fecha_limite": r[8]
        }
    return None

def actualizar_derivacion(derivacion_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    campos = []
    valores = []
    for campo in [
        "area_origen_id", "area_destino_id", "usuario_derivacion_id",
        "instrucciones", "fecha_limite"
    ]:
        if datos.get(campo) is not None:
            campos.append(f"{campo}=%s")
            valores.append(datos[campo])
    if not campos:
        cur.close()
        conn.close()
        return False
    valores.append(derivacion_id)
    consulta = f"UPDATE derivaciones SET {', '.join(campos)} WHERE id=%s RETURNING id;"
    cur.execute(consulta, tuple(valores))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None

def eliminar_derivacion(derivacion_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM derivaciones WHERE id=%s RETURNING id;", (derivacion_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None
