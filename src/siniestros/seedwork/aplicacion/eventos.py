"""Mediador de eventos de dominio con señales (patrón del tutorial 5).

Este es el mecanismo que cumple el ítem 4 de la rúbrica: los módulos se
comunican por eventos de dominio SIN acoplarse. El módulo `seguimiento` se
suscribe a SiniestroRegistrado / ProveedorAsignado y reacciona; jamás importa
clases del módulo `siniestros`. La señal se identifica por el nombre del tipo
de evento, de modo que emisor y receptor solo comparten el nombre del evento.

Usa PyDispatcher (pydispatch), la misma librería de señales del tutorial.
"""
from pydispatch import dispatcher

from seedwork.dominio.eventos import EventoDominio


def suscribirse_a_evento(tipo_evento, handler):
    """Conecta un handler a un evento de dominio.

    `tipo_evento` puede ser la clase del evento o su nombre (str). Aceptar el
    nombre es lo que permite que `seguimiento` se suscriba SIN importar las
    clases de `siniestros` (ítem 4): solo comparten el nombre del evento como
    contrato. El handler recibe la instancia y lee sus atributos por duck typing.
    """
    senal = tipo_evento if isinstance(tipo_evento, str) else tipo_evento.__name__
    dispatcher.connect(handler, signal=senal)


def despachar_evento_dominio(evento: EventoDominio):
    """Emite la señal del evento; todos los suscriptores reaccionan.

    Lo invoca la Unidad de Trabajo DESPUÉS de confirmar la transacción, para
    que los suscriptores solo reaccionen ante estado ya persistido.
    """
    dispatcher.send(signal=type(evento).__name__, evento=evento)
