"""Punto de entrada: app Flask mas los dos consumidores de Pulsar."""
import logging
import os
import threading
import time

from api import create_app
from config.settings import CONSUMIR_COMANDOS, ESCUCHAR_EVENTOS_SINIESTROS

logger = logging.getLogger(__name__)

app = create_app()


def _bucle(nombre, funcion):
    while True:
        try:
            funcion()
        except Exception:
            logger.exception("Consumidor %s caido; reintentando en 5s", nombre)
            time.sleep(5)


def _arrancar_consumidor_comandos():
    from modulos.reglas.infraestructura.consumidores import suscribirse_a_comandos
    _bucle("comandos.reglas", suscribirse_a_comandos)


def _arrancar_consumidor_eventos_siniestros():
    from modulos.reglas.infraestructura.consumidores import (
        suscribirse_a_eventos_de_siniestros,
    )
    _bucle("eventos.siniestros", suscribirse_a_eventos_de_siniestros)


if CONSUMIR_COMANDOS:
    threading.Thread(target=_arrancar_consumidor_comandos, daemon=True).start()

if ESCUCHAR_EVENTOS_SINIESTROS:
    threading.Thread(target=_arrancar_consumidor_eventos_siniestros, daemon=True).start()


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=puerto)
