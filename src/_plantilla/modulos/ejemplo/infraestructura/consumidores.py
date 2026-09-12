"""Consumidor del tópico comandos.ejemplo.

Usa el ConsumidorBase del seedwork (Key_Shared + ack tardío + nack) y despacha
por `type` del sobre. Aquí solo se conecta el tipo "CrearEjemplo"; agregar otro
tipo = agregar una entrada al dict `manejadores`.
"""
from config.settings import PULSAR_URL, TOPICO_COMANDOS, SUSCRIPCION
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.infraestructura.consumidores import ConsumidorBase
from modulos.ejemplo.aplicacion.comandos.crear_ejemplo import CrearEjemplo
from modulos.ejemplo.infraestructura.schema.v1.comandos import ComandoEjemplo


def _al_crear_ejemplo(sobre):
    # `sobre.id` es el id del mensaje del broker => idempotencia atómica en el handler.
    ejecutar_comando(CrearEjemplo(nombre=sobre.data.nombre, id_mensaje=sobre.id))


def suscribirse_a_comandos(url_broker: str = PULSAR_URL):
    manejadores = {"CrearEjemplo": _al_crear_ejemplo}
    ConsumidorBase(
        url_broker=url_broker,
        topico=TOPICO_COMANDOS,
        suscripcion=f"{SUSCRIPCION}-comandos",
        schema_sobre=ComandoEjemplo,
        manejadores=manejadores,
    ).iniciar()
