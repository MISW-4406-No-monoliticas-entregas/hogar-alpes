"""Punto de entrada de S9 Integraciones Partners.

S9 solo entra por HTTP (los partners son sistemas externos); no consume del broker.
Publica el comando RegistrarSiniestro y el evento SiniestroSincronizado.
"""
import os

from api import create_app

app = create_app()


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=puerto)
