"""Copia (lado productor) del esquema Avro v1 de comandos.siniestros (S2).

S2 es dueño de este esquema; D solo publica el tipo "RechazarSiniestro"
(compensación), pero `data` trae también los campos de los otros tipos del
tópico (con default) porque es un sobre único compartido por RegistrarSiniestro,
AsignarProveedor, MarcarValidado y RechazarSiniestro -- así este productor no
rompe el contrato combinado que ya usan S9 y S2.
"""
from pulsar.schema import Record, String, Float, Long


class DatosComandoSiniestros(Record):
    partner_id = String(required=False, default="")
    poliza = String(required=False, default="")
    monto = Float(required=False, default=0.0)
    moneda = String(required=False, default="")
    calle = String(required=False, default="")
    ciudad = String(required=False, default="")
    pais = String(required=False, default="")
    id_siniestro = String(required=False, default="")
    proveedor_id = String(required=False, default="")
    motivo = String(required=False, default="")


class ComandoSiniestros(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # D publica "RechazarSiniestro"
    data = DatosComandoSiniestros()
