"""Eventos de dominio del modulo orquestador.

Son internos al servicio: la Unidad de Trabajo los despacha despues del commit
y los handlers de aplicacion los traducen en comandos hacia otros servicios
(ver aplicacion/handlers.py). El agregado nunca publica en Pulsar directamente.
"""
import uuid
from dataclasses import dataclass

from seedwork.dominio.eventos import EventoDominio


@dataclass
class CompensacionIniciada(EventoDominio):
    """La saga entró en COMPENSANDO: hay que publicar las compensaciones que
    correspondan. `proveedor_id` viaja solo si la saga alcanzó a reservar uno
    antes del fallo (si no, no hay nada que liberar)."""
    id_saga: uuid.UUID = None
    siniestro_id: str = None
    motivo: str = None
    proveedor_id: str | None = None


@dataclass
class RegistroRequerido(EventoDominio):
    """Paso 1 del camino feliz: hay que pedirle a S2 que registre el siniestro."""
    id_saga: uuid.UUID = None
    partner_id: str = None
    poliza: str = None
    monto: float = 0.0
    moneda: str = "COP"
    calle: str = None
    ciudad: str = None
    pais: str = None


@dataclass
class ValidacionRequerida(EventoDominio):
    """Paso 2: ya hay id_siniestro, hay que pedirle a S10 que valide las reglas."""
    id_saga: uuid.UUID = None
    siniestro_id: str = None
    partner_id: str = None
    monto: float = 0.0
    moneda: str = "COP"
    servicio: str = None
    zona: str = None


@dataclass
class AsignacionRequerida(EventoDominio):
    """Paso 3: las reglas aprobaron, hay que pedirle a S7 un proveedor.

    Lleva tambien la confirmacion hacia S2 (MarcarValidado), porque el agregado
    Siniestro tiene que reflejar que paso la validacion.
    """
    id_saga: uuid.UUID = None
    siniestro_id: str = None
    servicio: str = None
    zona: str = None


@dataclass
class SagaCompletada(EventoDominio):
    """Paso 4: S7 reservo proveedor y la transaccion larga cerro bien."""
    id_saga: uuid.UUID = None
    siniestro_id: str = None
    proveedor_id: str = None
