"""Configuración de pruebas.

Fija un DATABASE_URL sin driver externo (SQLite en memoria) SOLO para las
pruebas, de modo que el árbol de imports (que pasa por config.db) no requiera el
driver de PostgreSQL. La aplicación real usa PostgreSQL vía docker-compose; esto
no toca el código de la app, solo el entorno de la prueba.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
