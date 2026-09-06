"""Unidad de Trabajo (puerto)."""
from abc import ABC, abstractmethod

from seedwork.aplicacion.eventos import despachar_evento_dominio


class UnidadDeTrabajo(ABC):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def _obtener_eventos(self):
        """Recolecta y vacía los eventos de dominio de los agregados tocados."""
        eventos = []
        for agregado in self._agregados_tocados():
            eventos.extend(agregado.eventos)
            agregado.limpiar_eventos()
        return eventos

    def commit(self):
        """Persiste y luego despacha los eventos de dominio."""
        eventos = self._obtener_eventos()
        self._commit()
        for evento in eventos:
            despachar_evento_dominio(evento)

    @abstractmethod
    def _commit(self):
        ...

    @abstractmethod
    def rollback(self):
        ...

    @abstractmethod
    def registrar_agregado(self, agregado):
        ...

    @abstractmethod
    def _agregados_tocados(self) -> list:
        ...
