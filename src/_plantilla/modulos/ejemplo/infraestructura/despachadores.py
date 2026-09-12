"""Despachador de eventos de integración a Pulsar (adaptador de salida)."""
from seedwork.infraestructura.pulsar import Despachador
from seedwork.infraestructura.utils import tiempo_actual_ms, generar_uuid
from config.settings import PULSAR_URL, TOPICO_EVENTOS
from modulos.ejemplo.dominio.eventos import EjemploCreado
from modulos.ejemplo.infraestructura.schema.v1.eventos import (
    EventoEjemplo,
    DatosEventoEjemplo,
)


class DespachadorEventos(Despachador):
    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def publicar_ejemplo_creado(self, evento: EjemploCreado):
        mensaje = EventoEjemplo(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type="EjemploCreado",
            data=DatosEventoEjemplo(
                id_ejemplo=str(evento.id_ejemplo),
                nombre=evento.nombre,
                estado=evento.estado,
            ),
        )
        # clave_particion = id de la entidad => Key_Shared enruta por entidad.
        self._publicar_mensaje(
            mensaje, TOPICO_EVENTOS, EventoEjemplo,
            clave_particion=str(evento.id_ejemplo),
        )
