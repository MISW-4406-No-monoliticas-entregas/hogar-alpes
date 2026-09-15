"""Esquema Avro v1 del tópico comandos.siniestros.

COPIADO TAL CUAL de src/siniestros/.../schema/v1/comandos.py. El dueño del
esquema de un comando es quien lo consume (Siniestros): S9 solo lo produce, así
que debe publicar EXACTAMENTE el esquema que Siniestros registró en
comandos.siniestros — mismo record `ComandoSiniestros`, mismo record anidado
`DatosComandoSiniestros` con TODOS los campos de TODOS los comandos del tópico
(no solo los que usa S9), porque Siniestros usa un sobre único por tópico con
`data` opcional (BACKWARD). Además el sobre (`id`, `time`, `spec_version`,
`type`) va declarado en la clase concreta, no por herencia: `pulsar.schema.Record`
NO hereda campos de la clase base, así que si se declaran solo en `Mensaje` se
pierden al serializar (ver docs/notas/nota-B-esquema-backward.md).

No modificar aquí sin coordinar con el dueño del comando (Siniestros/S2).
"""
from pulsar.schema import Record, String, Float, Long


class DatosComandoSiniestros(Record):
    # RegistrarSiniestro (lo único que S9 produce hoy)
    partner_id = String(required=False, default="")
    poliza = String(required=False, default="")
    monto = Float(required=False, default=0.0)
    moneda = String(required=False, default="")
    calle = String(required=False, default="")
    ciudad = String(required=False, default="")
    pais = String(required=False, default="")
    # AsignarProveedor / MarcarValidado / RechazarSiniestro (S9 no los produce,
    # pero deben existir para que el esquema sea idéntico al de Siniestros).
    id_siniestro = String(required=False, default="")
    proveedor_id = String(required=False, default="")
    motivo = String(required=False, default="")


class ComandoSiniestros(Record):
    # Campos del sobre declarados aquí (ver docstring).
    id = String()
    time = Long()
    spec_version = String()
    type = String()
    data = DatosComandoSiniestros()
