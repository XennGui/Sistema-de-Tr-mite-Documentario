# modelos/tramite_externo.py

class TramiteExterno:
    def __init__(
        self, id, numero_expediente, codigo_seguridad, remitente, tipo_documento,
        folios, asunto, contenido, archivo, tipo_persona, dni_ruc, email,
        telefono, estado, prioridad, fecha_registro, fecha_vencimiento,
        usuario_registro_id, area_actual_id
    ):
        self.id = id
        self.numero_expediente = numero_expediente
        self.codigo_seguridad = codigo_seguridad
        self.remitente = remitente
        self.tipo_documento = tipo_documento
        self.folios = folios
        self.asunto = asunto
        self.contenido = contenido
        self.archivo = archivo
        self.tipo_persona = tipo_persona
        self.dni_ruc = dni_ruc
        self.email = email
        self.telefono = telefono
        self.estado = estado
        self.prioridad = prioridad
        self.fecha_registro = fecha_registro
        self.fecha_vencimiento = fecha_vencimiento
        self.usuario_registro_id = usuario_registro_id
        self.area_actual_id = area_actual_id
