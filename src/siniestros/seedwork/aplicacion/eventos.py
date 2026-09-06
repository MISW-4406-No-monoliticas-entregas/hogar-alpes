"""Mediador de eventos de dominio con señales (PyDispatcher)."""
from pydispatch import dispatcher

from seedwork.dominio.eventos import EventoDominio


def suscribirse_a_evento(tipo_evento, handler):
    """Conecta un handler a un evento de dominio por clase o por nombre."""
    senal = tipo_evento if isinstance(tipo_evento, str) else tipo_evento.__name__
    dispatcher.connect(handler, signal=senal)


def despachar_evento_dominio(evento: EventoDominio):
    """Emite la señal del evento a sus suscriptores."""
    dispatcher.send(signal=type(evento).__name__, evento=evento)
