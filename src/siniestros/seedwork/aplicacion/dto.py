"""DTO base de la capa de aplicación."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DTO:
    """Objeto de transferencia inmutable entre capas (no es de dominio)."""
    ...
