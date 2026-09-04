"""Fábricas base.

Decisión de diseño: usamos fábricas para encapsular la creación de agregados y
la traducción entre representaciones (dominio <-> DTO) aplicando validaciones.
Concentran la lógica de construcción y mantienen los constructores limpios.
"""
from abc import ABC, abstractmethod


class Fabrica(ABC):
    @abstractmethod
    def crear_objeto(self, obj, mapeador=None):
        ...
