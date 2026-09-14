"""Consumidor del tópico comandos.siniestros — LA entrada de producción de S2.

Usa el ConsumidorBase del seedwork (Key_Shared + ack después del commit + nack
en error) y despacha por el campo `type` del sobre. Agregar un tipo de comando
nuevo = una entrada más en el dict `manejadores`.

Idempotencia: cada handler pasa el id del sobre al comando (`id_mensaje`); el
handler de aplicación lo registra en `mensajes_procesados` dentro de la misma
transacción del negocio. Si el productor no llenó `sobre.id` (esquema viejo sin
campos de sobre), se usa el message_id del broker, que también es estable entre
reentregas.
"""
import logging

from config.settings import PULSAR_URL, TOPICO_COMANDOS, SUSCRIPCION
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.infraestructura.consumidores import ConsumidorBase
from modulos.siniestros.aplicacion.comandos.registrar_siniestro import RegistrarSiniestro
from modulos.siniestros.aplicacion.comandos.asignar_proveedor import AsignarProveedor
from modulos.siniestros.aplicacion.comandos.marcar_validado import MarcarValidado
from modulos.siniestros.aplicacion.comandos.rechazar_siniestro import RechazarSiniestro
from modulos.siniestros.infraestructura.schema.v1.comandos import ComandoSiniestros

logger = logging.getLogger(__name__)


def _id_mensaje(sobre, mensaje) -> str:
    return sobre.id or str(mensaje.message_id())


def _al_registrar_siniestro(sobre, mensaje):
    datos = sobre.data
    ejecutar_comando(
        RegistrarSiniestro(
            partner_id=datos.partner_id,
            poliza=datos.poliza,
            monto=datos.monto,
            moneda=datos.moneda,
            calle=datos.calle,
            ciudad=datos.ciudad,
            pais=datos.pais or "CO",
            id_mensaje=_id_mensaje(sobre, mensaje),
        )
    )


def _al_asignar_proveedor(sobre, mensaje):
    ejecutar_comando(
        AsignarProveedor(
            id_siniestro=sobre.data.id_siniestro,
            proveedor_id=sobre.data.proveedor_id,
            id_mensaje=_id_mensaje(sobre, mensaje),
        )
    )


def _al_marcar_validado(sobre, mensaje):
    ejecutar_comando(
        MarcarValidado(
            id_siniestro=sobre.data.id_siniestro,
            id_mensaje=_id_mensaje(sobre, mensaje),
        )
    )


def _al_rechazar_siniestro(sobre, mensaje):
    ejecutar_comando(
        RechazarSiniestro(
            id_siniestro=sobre.data.id_siniestro,
            motivo=sobre.data.motivo or "no_especificado",
            id_mensaje=_id_mensaje(sobre, mensaje),
        )
    )


def _al_mensaje_sin_type(sobre, mensaje):
    # Compatibilidad con el esquema de la E3 (sin campos de sobre por el bug de
    # herencia de pulsar.schema): esos mensajes llegan con type=None. El único
    # productor conocido de ese esquema (S9) publica RegistrarSiniestro, así que
    # se asume ese tipo, con advertencia ruidosa para que la desalineación no
    # pase desapercibida. Ver README (sección de coordinación con S9).
    logger.warning(
        "Mensaje sin 'type' en el sobre (esquema viejo sin campos de sobre); "
        "se asume RegistrarSiniestro. El productor debe migrar al esquema con "
        "sobre declarado."
    )
    _al_registrar_siniestro(sobre, mensaje)


def suscribirse_a_comandos(url_broker: str = PULSAR_URL):
    manejadores = {
        "RegistrarSiniestro": _al_registrar_siniestro,
        "AsignarProveedor": _al_asignar_proveedor,
        "MarcarValidado": _al_marcar_validado,
        "RechazarSiniestro": _al_rechazar_siniestro,
        None: _al_mensaje_sin_type,
    }
    ConsumidorBase(
        url_broker=url_broker,
        topico=TOPICO_COMANDOS,
        suscripcion=f"{SUSCRIPCION}-comandos",  # suscripción propia del servicio
        schema_sobre=ComandoSiniestros,
        manejadores=manejadores,
    ).iniciar()
