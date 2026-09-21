"""Copia (lado productor) del esquema Avro v1 de comandos.reglas (S10).

El orquestador publica "ValidarSiniestro" en este topico. Se copia el esquema
del dueno en vez de importar su codigo: ningun servicio depende de otro en
tiempo de build.
"""
from pulsar.schema import Record, String, Long, Float


class DatosComandoReglas(Record):
    id_siniestro = String(required=False, default="")
    partner_id = String(required=False, default="")
    monto = Float(required=False, default=0.0)
    moneda = String(required=False, default="COP")
    servicio = String(required=False, default="")
    zona = String(required=False, default="")


class ComandoReglas(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()
    data = DatosComandoReglas()
