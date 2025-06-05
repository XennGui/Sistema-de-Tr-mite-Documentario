# servicios/usuario.py

from db import get_connection

def crear_usuario(nombre, area_id, username, password, email, rol):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO usuarios (nombre, area_id, username, password, email, rol) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, fecha_creacion;",
        (nombre, area_id, username, password, email, rol)
    )
    usuario_id, fecha_creacion = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return usuario_id, fecha_creacion

def obtener_usuarios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, area_id, username, email, rol, fecha_creacion FROM usuarios;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "nombre": r[1],
            "area_id": r[2],
            "username": r[3],
            "email": r[4],
            "rol": r[5],
            "fecha_creacion": r[6]
        }
        for r in rows
    ]

def obtener_usuario(usuario_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, area_id, username, email, rol, fecha_creacion FROM usuarios WHERE id = %s;", (usuario_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {
            "id": r[0],
            "nombre": r[1],
            "area_id": r[2],
            "username": r[3],
            "email": r[4],
            "rol": r[5],
            "fecha_creacion": r[6]
        }
    return None

def actualizar_usuario(usuario_id, datos):
    conn = get_connection()
    cur = conn.cursor()
    #solo actualiza los campos que no son None
    campos = []
    valores = []
    for campo in ["nombre", "area_id", "username", "password", "email", "rol"]:
        if datos.get(campo) is not None:
            campos.append(f"{campo}=%s")
            valores.append(datos[campo])
    if not campos:
        cur.close()
        conn.close()
        return False
    valores.append(usuario_id)
    consulta = f"UPDATE usuarios SET {', '.join(campos)} WHERE id=%s RETURNING id;"
    cur.execute(consulta, tuple(valores))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None

def eliminar_usuario(usuario_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=%s RETURNING id;", (usuario_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result is not None
