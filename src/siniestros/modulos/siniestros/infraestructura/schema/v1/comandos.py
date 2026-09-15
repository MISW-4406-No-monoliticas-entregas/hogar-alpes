"""Esquema Avro v1 del tópico comandos.siniestros (sobre único por tópico).

Siniestros (S2) es el DUEÑO de este esquema: los productores (S9 y quien venga)
deben publicar exactamente esta forma. Un solo esquema por tópico + namespace en
BACKWARD => el registry rechaza cambios incompatibles.

Los campos del sobre van declarados AQUÍ y no por herencia: `pulsar.schema.Record`
NO hereda los campos de una clase base (su metaclase solo lee el namespace de la
clase concreta). Con la herencia de la E3, `id`, `time`, `spec_version` y `type`
no viajaban, y sin `type` no se puede despachar ni deduplicar por `id`.

El tipo concreto va en `type`; `data` lleva todos los campos posibles de todos
los comandos del tópico, opcionales con default (añadir un campo es aditivo).
"""
from pulsar.schema import Record, String, Float, Long


class DatosComandoSiniestros(Record):
    # RegistrarSiniestro
    partner_id = String(required=False, default="")
    poliza = String(required=False, default="")
    monto = Float(required=False, default=0.0)
    moneda = String(required=False, default="")
    calle = String(required=False, default="")
    ciudad = String(required=False, default="")
    pais = String(required=False, default="")
    # AsignarProveedor / MarcarValidado / RechazarSiniestro
    id_siniestro = String(required=False, default="")
    proveedor_id = String(required=False, default="")
    motivo = String(required=False, default="")


class ComandoSiniestros(Record):
    # Campos del sobre declarados aquí (ver docstring).
    id = String()
    time = Long()
    spec_version = String()
    # "RegistrarSiniestro" | "AsignarProveedor" | "MarcarValidado" | "RechazarSiniestro"
    type = String()
    data = DatosComandoSiniestros()
