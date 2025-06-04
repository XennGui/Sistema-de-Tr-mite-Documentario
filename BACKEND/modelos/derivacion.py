# modelos/derivacion.py

class Derivacion:
    def __init__(
        self, id, tramite_id, tramite_type, area_origen_id, area_destino_id,
        usuario_derivacion_id, fecha_derivacion, instrucciones, fecha_limite
    ):
        self.id = id
        self.tramite_id = tramite_id
        self.tramite_type = tramite_type
        self.area_origen_id = area_origen_id
        self.area_destino_id = area_destino_id
        self.usuario_derivacion_id = usuario_derivacion_id
        self.fecha_derivacion = fecha_derivacion
        self.instrucciones = instrucciones
        self.fecha_limite = fecha_limite
        