# modelos/usuario.py

class Usuario:
    def __init__(self, id, nombre, area_id, username, password, email, rol, fecha_creacion):
        self.id = id
        self.nombre = nombre
        self.area_id = area_id
        self.username = username
        self.password = password
        self.email = email
        self.rol = rol
        self.fecha_creacion = fecha_creacion
        