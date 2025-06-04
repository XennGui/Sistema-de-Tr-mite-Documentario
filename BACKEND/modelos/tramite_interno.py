# modelos/tramite_interno.py

class TramiteInterno:
    def __init__(
        self, id, numero_referencia, asunto, contenido, folios, archivo,
        remitente_id, area_origen_id, area_destino_id, estado, prioridad,
        fecha_envio, fecha_recepcion, fecha_vencimiento
    ):
        self.id = id
        self.numero_referencia = numero_referencia
        self.asunto = asunto
        self.contenido = contenido
        self.folios = folios
        self.archivo = archivo
        self.remitente_id = remitente_id
        self.area_origen_id = area_origen_id
        self.area_destino_id = area_destino_id
        self.estado = estado
        self.prioridad = prioridad
        self.fecha_envio = fecha_envio
        self.fecha_recepcion = fecha_recepcion
        self.fecha_vencimiento = fecha_vencimiento
        