"""Copia (lado productor) del esquema Avro v1 de comandos.matching (S7).

D es también el dueño de S7 en otro servicio, pero se copia igual el
esquema en vez de importar código entre servicios (ningún servicio depende
de otro en tiempo de build, ni siquiera cuando el dueño es la misma persona).
"""
from pulsar.schema import Record, String, Long


class DatosComandoMatching(Record):
    id_siniestro = String(required=False, default="")
    servicio = String(required=False, default="")
    zona = String(required=False, default="")
    proveedor_id = String(required=False, default="")


class ComandoMatching(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # D publica "LiberarProveedor"
    data = DatosComandoMatching()
