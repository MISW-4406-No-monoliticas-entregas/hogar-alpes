"""Punto de entrada: app Flask mas los tres consumidores de Pulsar."""
import logging
import os
import threading
import time

from api import create_app
from config.settings import (
    CONSUMIR_EVENTOS_SINIESTROS,
    CONSUMIR_EVENTOS_REGLAS,
    CONSUMIR_EVENTOS_MATCHING,
)

logger = logging.getLogger(__name__)

app = create_app()


def _bucle(nombre, funcion):
    while True:
        try:
            funcion()
        except Exception:
            logger.exception("Consumidor %s caido; reintentando en 5s", nombre)
            time.sleep(5)


def _consumidor_eventos_siniestros():
    from modulos.orquestador.infraestructura.consumidores import (
        suscribirse_a_eventos_siniestros,
    )
    _bucle("eventos.siniestros", suscribirse_a_eventos_siniestros)


def _consumidor_eventos_reglas():
    from modulos.orquestador.infraestructura.consumidores import (
        suscribirse_a_eventos_reglas,
    )
    _bucle("eventos.reglas", suscribirse_a_eventos_reglas)


def _consumidor_eventos_matching():
    from modulos.orquestador.infraestructura.consumidores import (
        suscribirse_a_eventos_matching,
    )
    _bucle("eventos.matching", suscribirse_a_eventos_matching)


if CONSUMIR_EVENTOS_SINIESTROS:
    threading.Thread(target=_consumidor_eventos_siniestros, daemon=True).start()

if CONSUMIR_EVENTOS_REGLAS:
    threading.Thread(target=_consumidor_eventos_reglas, daemon=True).start()

if CONSUMIR_EVENTOS_MATCHING:
    threading.Thread(target=_consumidor_eventos_matching, daemon=True).start()


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=puerto)
