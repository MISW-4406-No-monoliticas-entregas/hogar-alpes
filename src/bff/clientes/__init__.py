"""Instancias de los clientes HTTP, una por servicio, construidas desde settings.

La API importa de aquí (`from clientes import s2`) para que las rutas no
conozcan URLs ni timeouts; las pruebas reemplazan estos objetos.
"""
from config import settings
from clientes.cliente_s9 import ClienteS9
from clientes.cliente_s2 import ClienteS2
from clientes.cliente_s10 import ClienteS10
from clientes.cliente_s7 import ClienteS7
from clientes.cliente_orquestador import ClienteOrquestador

_timeouts = dict(
    timeout_conexion=settings.TIMEOUT_CONEXION_SEGUNDOS,
    timeout_lectura=settings.TIMEOUT_LECTURA_SEGUNDOS,
)

s9 = ClienteS9(settings.INTEGRACIONES_URL, **_timeouts)
s2 = ClienteS2(settings.SINIESTROS_URL, **_timeouts)
s10 = ClienteS10(settings.REGLAS_URL, **_timeouts)
s7 = ClienteS7(settings.MATCHING_URL, **_timeouts)
orquestador = ClienteOrquestador(settings.ORQUESTADOR_URL, **_timeouts)

# Orden en el que se reportan en /salud/dependencias.
todos = (s9, s2, s10, s7, orquestador)
