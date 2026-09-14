"""Publica un comando de prueba en `comandos.matching` (para probar S7 a mano).

En esta entrega parcial no hay saga: `comandos.matching` se publica a mano.
Este script usa el mismo esquema Avro que el consumidor real, así que llega
al servicio exactamente como llegaría desde la futura saga.

Uso (dentro del contenedor, que ya tiene pulsar-client/fastavro y el código):
    docker compose exec matching python scripts/publicar_prueba.py \
        asignar <id_siniestro> <servicio> <zona>
    docker compose exec matching python scripts/publicar_prueba.py \
        liberar <id_siniestro> <proveedor_id>
"""
import sys

import pulsar
from pulsar.schema import AvroSchema

from config.settings import PULSAR_URL, TOPICO_COMANDOS
from modulos.matching.infraestructura.schema.v1.comandos import (
    ComandoMatching,
    DatosComandoMatching,
)
from seedwork.infraestructura.utils import generar_uuid, tiempo_actual_ms


def _publicar(tipo: str, datos: DatosComandoMatching):
    cliente = pulsar.Client(PULSAR_URL)
    try:
        productor = cliente.create_producer(TOPICO_COMANDOS, schema=AvroSchema(ComandoMatching))
        mensaje = ComandoMatching(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type=tipo,
            data=datos,
        )
        productor.send(mensaje)
        print(f"Publicado en {TOPICO_COMANDOS}: type={tipo} data={datos}")
    finally:
        cliente.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    accion = sys.argv[1]
    if accion == "asignar":
        _, _, id_siniestro, servicio, zona = sys.argv
        _publicar(
            "AsignarProveedor",
            DatosComandoMatching(id_siniestro=id_siniestro, servicio=servicio, zona=zona),
        )
    elif accion == "liberar":
        _, _, id_siniestro, proveedor_id = sys.argv
        _publicar(
            "LiberarProveedor",
            DatosComandoMatching(id_siniestro=id_siniestro, proveedor_id=proveedor_id),
        )
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
