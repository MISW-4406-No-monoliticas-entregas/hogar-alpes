"""Unidad de Trabajo (puerto).

Decisión de diseño: la UoW define una frontera transaccional y es la ÚNICA que
publica eventos. Al confirmar (commit) recoge los eventos de dominio acumulados
en los agregados y los despacha por el mediador de señales (comunicación
in-process entre módulos). Los eventos de integración a Pulsar se publican desde
los handlers de eventos de dominio del módulo. Esto garantiza que nada se emite
si la transacción falla (ítem 2 y 4 de la rúbrica).
"""
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
        """Persiste y luego despacha los eventos de dominio ya confirmados."""
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
