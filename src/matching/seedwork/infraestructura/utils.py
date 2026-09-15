"""Utilidades de infraestructura."""
import time
import uuid


def tiempo_actual_ms() -> int:
    return int(time.time() * 1000)


def generar_uuid() -> str:
    return str(uuid.uuid4())
