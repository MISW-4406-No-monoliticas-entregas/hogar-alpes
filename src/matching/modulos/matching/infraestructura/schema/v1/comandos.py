"""Esquema Avro v1 del tópico comandos.matching (sobre único por tópico).

Un solo esquema + namespace en BACKWARD => el registry rechaza un cambio
incompatible. `type` distingue AsignarProveedor de LiberarProveedor; `data`
lleva todos los campos posibles de ambos, opcionales con default.
"""
from pulsar.schema import Record, String, Long


class DatosComandoMatching(Record):
    id_siniestro = String(required=False, default="")
    servicio = String(required=False, default="")
    zona = String(required=False, default="")
    proveedor_id = String(required=False, default="")  # solo LiberarProveedor


class ComandoMatching(Record):
    # Campos del sobre declarados aquí porque pulsar.schema NO hereda de la base.
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # "AsignarProveedor" | "LiberarProveedor"
    data = DatosComandoMatching()
