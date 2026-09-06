"""Despachador de eventos de integración a Pulsar."""
from seedwork.infraestructura.pulsar import Despachador
from seedwork.infraestructura.utils import tiempo_actual_ms, generar_uuid
from config.settings import PULSAR_URL, TOPICO_EVENTOS
from modulos.siniestros.dominio.eventos import (
    SiniestroRegistrado,
    ProveedorAsignado,
)
from modulos.siniestros.infraestructura.schema.v1.eventos import (
    EventoSiniestroRegistrado,
    SiniestroRegistradoPayload,
    EventoProveedorAsignado,
    ProveedorAsignadoPayload,
)


class DespachadorEventos(Despachador):
    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def publicar_siniestro_registrado(self, evento: SiniestroRegistrado):
        mensaje = EventoSiniestroRegistrado(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type="SiniestroRegistrado",
            data=SiniestroRegistradoPayload(
                id_siniestro=str(evento.id_siniestro),
                partner_id=evento.partner_id,
                poliza=evento.poliza,
                monto=evento.monto,
                moneda=evento.moneda,
                estado=evento.estado,
            ),
        )
        self._publicar_mensaje(mensaje, TOPICO_EVENTOS, EventoSiniestroRegistrado)

    def publicar_proveedor_asignado(self, evento: ProveedorAsignado):
        mensaje = EventoProveedorAsignado(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type="ProveedorAsignado",
            data=ProveedorAsignadoPayload(
                id_siniestro=str(evento.id_siniestro),
                proveedor_id=evento.proveedor_id,
                estado=evento.estado,
            ),
        )
        self._publicar_mensaje(mensaje, TOPICO_EVENTOS, EventoProveedorAsignado)
