"""Fábricas base."""
from abc import ABC, abstractmethod


class Fabrica(ABC):
    @abstractmethod
    def crear_objeto(self, obj, mapeador=None):
        ...
