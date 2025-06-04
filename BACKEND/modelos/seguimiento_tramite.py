# modelos/seguimiento_tramite.py

class SeguimientoTramite:
    def __init__(
        self, id, tramite_id, tramite_type, accion, descripcion,
        usuario_id, area_id, adjunto, observaciones, fecha_hora
    ):
        self.id = id
        self.tramite_id = tramite_id
        self.tramite_type = tramite_type
        self.accion = accion
        self.descripcion = descripcion
        self.usuario_id = usuario_id
        self.area_id = area_id
        self.adjunto = adjunto
        self.observaciones = observaciones
        self.fecha_hora = fecha_hora
        