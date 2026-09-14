"""Despachador de eventos de integración a Pulsar (sobre único por tópico)."""
from seedwork.infraestructura.pulsar import Despachador
from seedwork.infraestructura.utils import tiempo_actual_ms, generar_uuid
from config.settings import PULSAR_URL, TOPICO_EVENTOS
from modulos.siniestros.dominio.eventos import (
    SiniestroRegistrado,
    ProveedorAsignado,
    SiniestroValidado,
    SiniestroRechazado,
)
from modulos.siniestros.infraestructura.schema.v1.eventos import (
    EventoSiniestros,
    DatosSiniestro,
)


class DespachadorEventos(Despachador):
    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def _publicar(self, tipo: str, id_siniestro: str, datos: DatosSiniestro):
        mensaje = EventoSiniestros(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type=tipo,
            data=datos,
        )
        # partition_key = id del siniestro: orden por entidad bajo Key_Shared.
        self._publicar_mensaje(
            mensaje, TOPICO_EVENTOS, EventoSiniestros, clave_particion=id_siniestro
        )

    def publicar_siniestro_registrado(self, evento: SiniestroRegistrado):
        self._publicar(
            "SiniestroRegistrado",
            str(evento.id_siniestro),
            DatosSiniestro(
                id_siniestro=str(evento.id_siniestro),
                partner_id=evento.partner_id,
                poliza=evento.poliza,
                monto=evento.monto,
                moneda=evento.moneda,
                estado=evento.estado,
            ),
        )

    def publicar_proveedor_asignado(self, evento: ProveedorAsignado):
        self._publicar(
            "ProveedorAsignado",
            str(evento.id_siniestro),
            DatosSiniestro(
                id_siniestro=str(evento.id_siniestro),
                proveedor_id=evento.proveedor_id,
                estado=evento.estado,
            ),
        )

    def publicar_siniestro_validado(self, evento: SiniestroValidado):
        self._publicar(
            "SiniestroValidado",
            str(evento.id_siniestro),
            DatosSiniestro(
                id_siniestro=str(evento.id_siniestro),
                estado=evento.estado,
            ),
        )

    def publicar_siniestro_rechazado(self, evento: SiniestroRechazado):
        self._publicar(
            "SiniestroRechazado",
            str(evento.id_siniestro),
            DatosSiniestro(
                id_siniestro=str(evento.id_siniestro),
                motivo=evento.motivo,
                estado=evento.estado,
            ),
        )
