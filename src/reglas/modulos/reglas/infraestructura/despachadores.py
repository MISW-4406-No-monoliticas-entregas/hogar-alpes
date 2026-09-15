"""Despachador de eventos de integracion del modulo reglas."""
from seedwork.infraestructura.pulsar import Despachador
from seedwork.infraestructura.utils import tiempo_actual_ms, generar_uuid
from config.settings import PULSAR_URL, TOPICO_EVENTOS
from modulos.reglas.dominio.eventos import (
    SiniestroAprobadoPorReglas,
    SiniestroRechazadoPorReglas,
)
from modulos.reglas.infraestructura.schema.v1.eventos import (
    EventoReglas,
    DatosEventoReglas,
)


class DespachadorEventos(Despachador):
    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def _publicar(self, evento, tipo: str, resultado: str):
        mensaje = EventoReglas(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type=tipo,
            data=DatosEventoReglas(
                id_validacion=str(evento.id_validacion),
                id_siniestro=evento.id_siniestro,
                partner_id=evento.partner_id,
                monto=evento.monto,
                moneda=evento.moneda,
                servicio=evento.servicio,
                zona=evento.zona,
                resultado=resultado,
                motivo=evento.motivo,
            ),
        )
        self._publicar_mensaje(
            mensaje, TOPICO_EVENTOS, EventoReglas,
            clave_particion=evento.id_siniestro,
        )

    def publicar_siniestro_aprobado(self, evento: SiniestroAprobadoPorReglas):
        self._publicar(evento, "SiniestroAprobadoPorReglas", "APROBADO")

    def publicar_siniestro_rechazado(self, evento: SiniestroRechazadoPorReglas):
        self._publicar(evento, "SiniestroRechazadoPorReglas", "RECHAZADO")
