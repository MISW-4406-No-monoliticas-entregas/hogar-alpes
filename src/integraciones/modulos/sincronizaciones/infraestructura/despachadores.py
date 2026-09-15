"""Despachadores a Pulsar (adaptadores de salida).

- DespachadorComandos: publica el comando canónico RegistrarSiniestro en
  comandos.siniestros (esquema copiado tal cual del dueño, Siniestros).
- DespachadorEventos: publica el evento de integración SiniestroSincronizado en
  eventos.partners (tópico propio de S9).
"""
from seedwork.infraestructura.pulsar import Despachador
from seedwork.infraestructura.utils import tiempo_actual_ms, generar_uuid
from config.settings import PULSAR_URL, TOPICO_COMANDOS_SINIESTROS, TOPICO_EVENTOS
from modulos.sincronizaciones.dominio.eventos import SiniestroSincronizado
from modulos.sincronizaciones.infraestructura.schema.v1.comandos import (
    ComandoRegistrarSiniestro,
    RegistrarSiniestroPayload,
)
from modulos.sincronizaciones.infraestructura.schema.v1.eventos import (
    EventoSiniestroSincronizado,
    DatosSiniestroSincronizado,
)


class DespachadorComandos(Despachador):
    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def publicar_registrar_siniestro(self, evento: SiniestroSincronizado):
        mensaje = ComandoRegistrarSiniestro(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type="RegistrarSiniestro",
            data=RegistrarSiniestroPayload(
                partner_id=evento.partner_id,
                poliza=evento.poliza,
                monto=evento.monto,
                moneda=evento.moneda,
                calle=evento.calle,
                ciudad=evento.ciudad,
                pais=evento.pais,
            ),
        )
        # Key_Shared: mismo siniestro del partner => misma partición/consumidor.
        clave = f"{evento.partner_id}:{evento.id_externo}"
        self._publicar_mensaje(
            mensaje, TOPICO_COMANDOS_SINIESTROS, ComandoRegistrarSiniestro,
            clave_particion=clave,
        )


class DespachadorEventos(Despachador):
    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def publicar_siniestro_sincronizado(self, evento: SiniestroSincronizado):
        mensaje = EventoSiniestroSincronizado(
            id=generar_uuid(),
            time=tiempo_actual_ms(),
            spec_version="v1",
            type="SiniestroSincronizado",
            data=DatosSiniestroSincronizado(
                id_sincronizacion=str(evento.id_sincronizacion),
                partner_id=evento.partner_id,
                id_externo=evento.id_externo,
                estado="PUBLICADA",
            ),
        )
        self._publicar_mensaje(
            mensaje, TOPICO_EVENTOS, EventoSiniestroSincronizado,
            clave_particion=str(evento.id_sincronizacion),
        )
