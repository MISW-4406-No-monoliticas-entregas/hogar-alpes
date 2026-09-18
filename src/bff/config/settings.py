"""Configuración por variables de entorno.

Las URL de los servicios las inyecta el docker-compose (nombres de servicio de
la red interna). Los valores por defecto apuntan a los puertos publicados en
local para poder correr el BFF fuera de Docker contra el compose levantado.
"""
import os

# URL base de cada servicio al que el BFF le hace HTTP (única excepción
# autorizada a la regla "no HTTP entre servicios").
INTEGRACIONES_URL = os.getenv("INTEGRACIONES_URL", "http://localhost:8001")  # S9
SINIESTROS_URL = os.getenv("SINIESTROS_URL", "http://localhost:8000")        # S2
REGLAS_URL = os.getenv("REGLAS_URL", "http://localhost:8002")                # S10
MATCHING_URL = os.getenv("MATCHING_URL", "http://localhost:8003")            # S7

# Orquestador de sagas (S4). Sin valor por defecto a propósito: mientras su
# rama no esté integrada, el BFF responde 501 en las consultas de estado de la
# transacción en vez de intentar conectarse a un host que no existe.
ORQUESTADOR_URL = os.getenv("ORQUESTADOR_URL", "")

# Timeouts (segundos). Si un servicio no responde, el BFF devuelve 503/504,
# nunca se queda colgado esperando.
TIMEOUT_CONEXION_SEGUNDOS = float(os.getenv("TIMEOUT_CONEXION_SEGUNDOS", "2"))
TIMEOUT_LECTURA_SEGUNDOS = float(os.getenv("TIMEOUT_LECTURA_SEGUNDOS", "5"))
