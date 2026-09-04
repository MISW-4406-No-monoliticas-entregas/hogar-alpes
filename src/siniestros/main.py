"""Punto de entrada del servicio Trabajos Siniestros.

Arranca la app Flask y, en un hilo aparte, el consumidor del tópico de comandos
(comandos.siniestros). Así el comando RegistrarSiniestro entra tanto por HTTP
como por el broker, compartiendo el mismo mediador de comandos.
"""
import logging
import os
import threading

from api import create_app

logger = logging.getLogger(__name__)

app = create_app()


def _arrancar_consumidor_comandos():
    from modulos.siniestros.infraestructura.consumidores import (
        suscribirse_a_comandos,
    )
    while True:
        try:
            suscribirse_a_comandos()
        except Exception:
            logger.exception("Consumidor de comandos caído; reintentando en 5s")
            import time
            time.sleep(5)


if os.getenv("CONSUMIR_COMANDOS", "true").lower() == "true":
    hilo = threading.Thread(target=_arrancar_consumidor_comandos, daemon=True)
    hilo.start()


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=puerto)
