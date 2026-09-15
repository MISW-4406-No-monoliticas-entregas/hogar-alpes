"""Interfaces de repositorio del módulo matching (puertos de salida)."""
import uuid
from abc import abstractmethod

from seedwork.dominio.repositorios import Repositorio
from modulos.matching.dominio.entidades import Asignacion, ProveedorHabilitado


class RepositorioAsignaciones(Repositorio):
    @abstractmethod
    def obtener_por_id(self, id: uuid.UUID) -> Asignacion | None:
        ...

    @abstractmethod
    def obtener_asignada_por_siniestro(self, id_siniestro: str) -> Asignacion | None:
        ...

    @abstractmethod
    def agregar(self, asignacion: Asignacion):
        ...

    @abstractmethod
    def actualizar(self, asignacion: Asignacion):
        ...


class RepositorioProveedoresHabilitados(Repositorio):
    @abstractmethod
    def obtener_por_id(self, id: uuid.UUID) -> ProveedorHabilitado | None:
        ...

    @abstractmethod
    def buscar_disponible(self, servicio: str, zona: str) -> ProveedorHabilitado | None:
        ...

    @abstractmethod
    def listar_por_zona_servicio(self, zona: str, servicio: str) -> list[ProveedorHabilitado]:
        ...

    @abstractmethod
    def agregar(self, proveedor: ProveedorHabilitado):
        ...

    @abstractmethod
    def actualizar(self, proveedor: ProveedorHabilitado):
        ...
