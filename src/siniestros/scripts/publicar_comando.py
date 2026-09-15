"""Utilidad de prueba: publica un comando en comandos.siniestros.

Simula al productor (S9) para verificar los checkpoints sin depender de otros
servicios. Correr DENTRO del contenedor (tiene el PYTHONPATH y la red):

    docker compose exec siniestros python scripts/publicar_comando.py registrar
    docker compose exec siniestros python scripts/publicar_comando.py asignar <id_siniestro> <proveedor_id>
    docker compose exec siniestros python scripts/publicar_comando.py validar <id_siniestro>
    docker compose exec siniestros python scripts/publicar_comando.py rechazar <id_siniestro> [motivo]
"""
import sys
import uuid

from config.settings import PULSAR_URL, TOPICO_COMANDOS
from seedwork.infraestructura.pulsar import Despachador
from seedwork.infraestructura.utils import tiempo_actual_ms, generar_uuid
from modulos.siniestros.infraestructura.schema.v1.comandos import (
    ComandoSiniestros,
    DatosComandoSiniestros,
)


class _DespachadorComandos(Despachador):
    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def publicar(self, tipo: str, datos: DatosComandoSiniestros, clave: str):
        sobre = ComandoSiniestros(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type=tipo,
            data=datos,
        )
        self._publicar_mensaje(sobre, TOPICO_COMANDOS, ComandoSiniestros, clave)
        print(f"Publicado {tipo} (id sobre={sobre.id}, partition_key={clave})")


def main():
    accion = sys.argv[1] if len(sys.argv) > 1 else "registrar"
    despachador = _DespachadorComandos(PULSAR_URL)

    if accion == "registrar":
        clave = f"prueba:{uuid.uuid4()}"
        despachador.publicar(
            "RegistrarSiniestro",
            DatosComandoSiniestros(
                partner_id="partner-demo",
                poliza="POL-001",
                monto=1500000.0,
                moneda="COP",
                calle="Calle 100 # 8-60",
                ciudad="Bogotá",
                pais="CO",
            ),
            clave,
        )
    elif accion == "asignar":
        id_siniestro, proveedor = sys.argv[2], sys.argv[3]
        despachador.publicar(
            "AsignarProveedor",
            DatosComandoSiniestros(id_siniestro=id_siniestro, proveedor_id=proveedor),
            id_siniestro,
        )
    elif accion == "validar":
        id_siniestro = sys.argv[2]
        despachador.publicar(
            "MarcarValidado",
            DatosComandoSiniestros(id_siniestro=id_siniestro),
            id_siniestro,
        )
    elif accion == "rechazar":
        id_siniestro = sys.argv[2]
        motivo = sys.argv[3] if len(sys.argv) > 3 else "documentacion_incompleta"
        despachador.publicar(
            "RechazarSiniestro",
            DatosComandoSiniestros(id_siniestro=id_siniestro, motivo=motivo),
            id_siniestro,
        )
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
