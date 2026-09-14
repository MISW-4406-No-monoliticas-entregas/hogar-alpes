"""Despachador de eventos de integración a Pulsar (adaptador de salida)."""
from seedwork.infraestructura.pulsar import Despachador
from seedwork.infraestructura.utils import tiempo_actual_ms, generar_uuid
from config.settings import PULSAR_URL, TOPICO_EVENTOS
from modulos.matching.dominio.eventos import ProveedorAsignado, SinProveedorDisponible
from modulos.matching.infraestructura.schema.v1.eventos import (
    EventoMatching,
    DatosEventoMatching,
)


class DespachadorEventos(Despachador):
    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def publicar_proveedor_asignado(self, evento: ProveedorAsignado):
        mensaje = EventoMatching(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type="ProveedorAsignado",
            data=DatosEventoMatching(
                id_asignacion=str(evento.id_asignacion),
                id_siniestro=str(evento.id_siniestro),
                proveedor_id=evento.proveedor_id,
                nombre_proveedor=evento.nombre_proveedor,
                servicio=evento.servicio,
                zona=evento.zona,
                estado=evento.estado,
            ),
        )
        # clave_particion = id del siniestro => Key_Shared enruta por siniestro.
        self._publicar_mensaje(
            mensaje, TOPICO_EVENTOS, EventoMatching,
            clave_particion=str(evento.id_siniestro),
        )

    def publicar_sin_proveedor_disponible(self, evento: SinProveedorDisponible):
        mensaje = EventoMatching(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type="SinProveedorDisponible",
            data=DatosEventoMatching(
                id_asignacion=str(evento.id_asignacion),
                id_siniestro=str(evento.id_siniestro),
                servicio=evento.servicio,
                zona=evento.zona,
                estado=evento.estado,
            ),
        )
        self._publicar_mensaje(
            mensaje, TOPICO_EVENTOS, EventoMatching,
            clave_particion=str(evento.id_siniestro),
        )
