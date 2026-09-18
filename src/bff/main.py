"""Punto de entrada del BFF (Backend for Frontend).

Solo levanta la app Flask: el BFF no consume tópicos ni tiene base de datos.
"""
import os

from api import create_app

app = create_app()


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=puerto)
