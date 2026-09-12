"""Interfaz del repositorio de sincronizaciones (puerto de salida en el dominio)."""
import uuid
from abc import abstractmethod

from seedwork.dominio.repositorios import Repositorio
from modulos.sincronizaciones.dominio.entidades import Sincronizacion


class RepositorioSincronizaciones(Repositorio):
    @abstractmethod
    def obtener_por_id(self, id: uuid.UUID) -> Sincronizacion | None:
        ...

    @abstractmethod
    def existe(self, partner_id: str, id_externo: str) -> bool:
        """Idempotencia de negocio: ¿ya se recibió ese partner_id + id_externo?"""
        ...

    @abstractmethod
    def agregar(self, sincronizacion: Sincronizacion):
        ...

    @abstractmethod
    def actualizar(self, sincronizacion: Sincronizacion):
        ...
