"""Publica un ValidarSiniestro en comandos.reglas usando el esquema del servicio.

Uso, desde dentro del contenedor:
    python tools/publicar_comando.py <id_siniestro> <partner_id> <monto> <servicio> <zona>

Ejemplo:
    python tools/publicar_comando.py sin-001 seguros-alpes 500000 plomeria bogota-norte
"""
import sys

from config.settings import PULSAR_URL, TOPICO_COMANDOS
from seedwork.infraestructura.pulsar import obtener_cliente
from seedwork.infraestructura.utils import generar_uuid, tiempo_actual_ms
from modulos.reglas.infraestructura.schema.v1.comandos import (
    ComandoReglas,
    DatosComandoReglas,
)
from pulsar.schema import AvroSchema

id_siniestro, partner_id, monto, servicio, zona = sys.argv[1:6]

productor = obtener_cliente(PULSAR_URL).create_producer(
    TOPICO_COMANDOS, schema=AvroSchema(ComandoReglas)
)
productor.send(
    ComandoReglas(
        id=generar_uuid(),
        time=tiempo_actual_ms(),
        spec_version="v1",
        type="ValidarSiniestro",
        data=DatosComandoReglas(
            id_siniestro=id_siniestro,
            partner_id=partner_id,
            monto=float(monto),
            moneda="COP",
            servicio=servicio,
            zona=zona,
        ),
    ),
    partition_key=id_siniestro,
)
print("publicado", id_siniestro, partner_id, monto, servicio, zona)
