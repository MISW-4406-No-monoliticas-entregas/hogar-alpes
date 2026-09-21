"""Despachador de las compensaciones hacia comandos.siniestros y
comandos.matching (adaptador de salida).

Ambos tópicos son de otros servicios (S2 y S7); se publica usando la copia
del esquema de cada dueño (schema/v1/), nunca importando su código.
"""
from seedwork.infraestructura.pulsar import Despachador
from seedwork.infraestructura.utils import tiempo_actual_ms, generar_uuid
from config.settings import (
    PULSAR_URL,
    TOPICO_COMANDOS_SINIESTROS,
    TOPICO_COMANDOS_MATCHING,
)
from modulos.orquestador.infraestructura.schema.v1.comandos_siniestros import (
    ComandoSiniestros,
    DatosComandoSiniestros,
)
from modulos.orquestador.infraestructura.schema.v1.comandos_matching import (
    ComandoMatching,
    DatosComandoMatching,
)


class DespachadorCompensaciones(Despachador):
    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def publicar_rechazar_siniestro(self, siniestro_id: str, motivo: str):
        mensaje = ComandoSiniestros(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type="RechazarSiniestro",
            data=DatosComandoSiniestros(id_siniestro=siniestro_id, motivo=motivo),
        )
        # clave_particion = id del siniestro => Key_Shared enruta por siniestro.
        self._publicar_mensaje(
            mensaje, TOPICO_COMANDOS_SINIESTROS, ComandoSiniestros,
            clave_particion=siniestro_id,
        )

    def publicar_liberar_proveedor(self, siniestro_id: str, proveedor_id: str):
        mensaje = ComandoMatching(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type="LiberarProveedor",
            data=DatosComandoMatching(id_siniestro=siniestro_id, proveedor_id=proveedor_id),
        )
        self._publicar_mensaje(mensaje, TOPICO_COMANDOS_MATCHING, ComandoMatching)
