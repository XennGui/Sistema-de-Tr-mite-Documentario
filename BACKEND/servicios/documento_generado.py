# servicios/documento_generado.py

from db import get_connection

def crear_documento_generado(datos):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO documentos_generados (
            tramite_id, tramite_type, tipo_documento, contenido, archivo,
            usuario_generador_id, firmado, fecha_firma
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, fecha_creacion;
    """, (
        datos["tramite_id"], datos["tramite_type"], datos["tipo_documento"],
        datos["contenido"], datos["archivo"], datos["usuario_generador_id"],
        datos.get("firmado", False), datos.get("fecha_firma")
    ))
    documento_id, fecha_creacion = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return documento_id, fecha_creacion

def obtener_documentos_generados():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tramite_id, tramite_type, tipo_documento, contenido, archivo,
                usuario_generador_id, fecha_creacion, firmado, fecha_firma
        FROM documentos_generados;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "tramite_id": r[1],
            "tramite_type": r[2],
            "tipo_documento": r[3],
            "contenido": r[4],
            "archivo": r[5],
            "usuario_generador_id": r[6],
            "fecha_creacion": r[7],
            "firmado": r[8],
            "fecha_firma": r[9]
        }
        for r in rows
    ]

def obtener_documento_generado(documento_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tramite_id, tramite_type, tipo_documento, contenido, archivo,
                usuario_generador_id, fecha_creacion, firmado, fecha_firma
        FROM documentos_generados WHERE id = %s;
    """, (documento_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {
            "id": r[0],
            "tramite_id": r[1],
            "tramite_type": r[2],
            "tipo_documento": r[3],
            "contenido": r[4],
            "archivo": r[5],
            "usuario_generador_id": r[6],
            "fecha_creacion": r[7],
            "firmado": r[8],
            "fecha_firma": r[9]
        }
    return None

def actualizar_documento_generado(documento_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    campos = []
    valores = []
    for campo in [
        "tipo_documento", "contenido", "archivo", "firmado", "fecha_firma"
    ]:
        if datos.get(campo) is not None:
            campos.append(f"{campo}=%s")
            valores.append(datos[campo])
    if not campos:
        cur.close()
        conn.close()
        return False
    valores.append(documento_id)
    consulta = f"UPDATE documentos_generados SET {', '.join(campos)} WHERE id=%s RETURNING id;"
    cur.execute(consulta, tuple(valores))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None

def eliminar_documento_generado(documento_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM documentos_generados WHERE id=%s RETURNING id;", (documento_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None
