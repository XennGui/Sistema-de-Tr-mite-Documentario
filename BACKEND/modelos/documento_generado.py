# modelos/documento_generado.py

class DocumentoGenerado:
    def __init__(
        self, id, tramite_id, tramite_type, tipo_documento, contenido, archivo,
        usuario_generador_id, fecha_creacion, firmado, fecha_firma
    ):
        self.id = id
        self.tramite_id = tramite_id
        self.tramite_type = tramite_type
        self.tipo_documento = tipo_documento
        self.contenido = contenido
        self.archivo = archivo
        self.usuario_generador_id = usuario_generador_id
        self.fecha_creacion = fecha_creacion
        self.firmado = firmado
        self.fecha_firma = fecha_firma
        