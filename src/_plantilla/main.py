"""Punto de entrada: app Flask + consumidor del tópico de comandos."""
import logging
import os
import threading
import time

from api import create_app
from config.settings import CONSUMIR_COMANDOS

logger = logging.getLogger(__name__)

app = create_app()


def _arrancar_consumidor_comandos():
    from modulos.ejemplo.infraestructura.consumidores import suscribirse_a_comandos
    while True:
        try:
            suscribirse_a_comandos()
        except Exception:
            logger.exception("Consumidor caído; reintentando en 5s")
            time.sleep(5)


if CONSUMIR_COMANDOS:
    hilo = threading.Thread(target=_arrancar_consumidor_comandos, daemon=True)
    hilo.start()


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=puerto)
