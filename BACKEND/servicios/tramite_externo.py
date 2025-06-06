# servicios/tramite_externo.py

from db import get_connection

def crear_tramite_externo(datos):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tramites_externos (
            numero_expediente, codigo_seguridad, remitente, tipo_documento, folios, asunto, contenido, archivo,
            tipo_persona, dni_ruc, email, telefono, estado, prioridad, fecha_vencimiento, usuario_registro_id, area_actual_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, fecha_registro;
    """, (
        datos["numero_expediente"], datos["codigo_seguridad"], datos["remitente"], datos["tipo_documento"],
        datos["folios"], datos["asunto"], datos.get("contenido"), datos.get("archivo"),
        datos["tipo_persona"], datos["dni_ruc"], datos["email"], datos.get("telefono"),
        datos.get("estado", "pendiente"), datos.get("prioridad", 3), datos.get("fecha_vencimiento"),
        datos.get("usuario_registro_id"), datos.get("area_actual_id")
    ))
    tramite_id, fecha_registro = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return tramite_id, fecha_registro

def obtener_tramites_externos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, numero_expediente, codigo_seguridad, remitente, tipo_documento, folios, asunto, contenido, archivo,
                tipo_persona, dni_ruc, email, telefono, estado, prioridad, fecha_registro, fecha_vencimiento,
                usuario_registro_id, area_actual_id
        FROM tramites_externos;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "numero_expediente": r[1],
            "codigo_seguridad": r[2],
            "remitente": r[3],
            "tipo_documento": r[4],
            "folios": r[5],
            "asunto": r[6],
            "contenido": r[7],
            "archivo": r[8],
            "tipo_persona": r[9],
            "dni_ruc": r[10],
            "email": r[11],
            "telefono": r[12],
            "estado": r[13],
            "prioridad": r[14],
            "fecha_registro": r[15],
            "fecha_vencimiento": r[16],
            "usuario_registro_id": r[17],
            "area_actual_id": r[18]
        }
        for r in rows
    ]

def obtener_tramite_externo(tramite_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, numero_expediente, codigo_seguridad, remitente, tipo_documento, folios, asunto, contenido, archivo,
                tipo_persona, dni_ruc, email, telefono, estado, prioridad, fecha_registro, fecha_vencimiento,
                usuario_registro_id, area_actual_id
        FROM tramites_externos WHERE id = %s;
    """, (tramite_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {
            "id": r[0],
            "numero_expediente": r[1],
            "codigo_seguridad": r[2],
            "remitente": r[3],
            "tipo_documento": r[4],
            "folios": r[5],
            "asunto": r[6],
            "contenido": r[7],
            "archivo": r[8],
            "tipo_persona": r[9],
            "dni_ruc": r[10],
            "email": r[11],
            "telefono": r[12],
            "estado": r[13],
            "prioridad": r[14],
            "fecha_registro": r[15],
            "fecha_vencimiento": r[16],
            "usuario_registro_id": r[17],
            "area_actual_id": r[18]
        }
    return None

def actualizar_tramite_externo(tramite_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    campos = []
    valores = []
    for campo in [
        "remitente", "tipo_documento", "folios", "asunto", "contenido", "archivo",
        "tipo_persona", "dni_ruc", "email", "telefono", "estado", "prioridad", "fecha_vencimiento",
        "usuario_registro_id", "area_actual_id"
    ]:
        if datos.get(campo) is not None:
            campos.append(f"{campo}=%s")
            valores.append(datos[campo])
    if not campos:
        cur.close()
        conn.close()
        return False
    valores.append(tramite_id)
    consulta = f"UPDATE tramites_externos SET {', '.join(campos)} WHERE id=%s RETURNING id;"
    cur.execute(consulta, tuple(valores))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None

def eliminar_tramite_externo(tramite_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tramites_externos WHERE id=%s RETURNING id;", (tramite_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None

def buscar_tramite_externo_por_expediente_y_codigo(numero_expediente, codigo_seguridad):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, numero_expediente, codigo_seguridad, remitente, tipo_documento, folios, asunto, contenido, archivo,
                tipo_persona, dni_ruc, email, telefono, estado, prioridad, fecha_registro, fecha_vencimiento,
                usuario_registro_id, area_actual_id
        FROM tramites_externos WHERE numero_expediente=%s AND codigo_seguridad=%s;
    """, (numero_expediente, codigo_seguridad))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {
            "id": r[0],
            "numero_expediente": r[1],
            "codigo_seguridad": r[2],
            "remitente": r[3],
            "tipo_documento": r[4],
            "folios": r[5],
            "asunto": r[6],
            "contenido": r[7],
            "archivo": r[8],
            "tipo_persona": r[9],
            "dni_ruc": r[10],
            "email": r[11],
            "telefono": r[12],
            "estado": r[13],
            "prioridad": r[14],
            "fecha_registro": r[15],
            "fecha_vencimiento": r[16],
            "usuario_registro_id": r[17],
            "area_actual_id": r[18]
        }
    return None