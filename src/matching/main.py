"""Punto de entrada: app Flask + consumidores de tópicos de Pulsar."""
import logging
import os
import threading
import time

from api import create_app
from config.settings import CONSUMIR_COMANDOS, CONSUMIR_EVENTOS_SINIESTROS

logger = logging.getLogger(__name__)

app = create_app()


def _arrancar_hilo(nombre: str, objetivo):
    def _bucle():
        while True:
            try:
                objetivo()
            except Exception:
                logger.exception("Consumidor '%s' caído; reintentando en 5s", nombre)
                time.sleep(5)

    hilo = threading.Thread(target=_bucle, daemon=True, name=nombre)
    hilo.start()


if CONSUMIR_COMANDOS:
    from modulos.matching.infraestructura.consumidores import suscribirse_a_comandos
    _arrancar_hilo("comandos.matching", suscribirse_a_comandos)

if CONSUMIR_EVENTOS_SINIESTROS:
    from modulos.matching.infraestructura.consumidor_eventos_siniestros import (
        suscribirse_a_eventos_siniestros,
    )
    _arrancar_hilo("eventos.siniestros (log)", suscribirse_a_eventos_siniestros)


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=puerto)
