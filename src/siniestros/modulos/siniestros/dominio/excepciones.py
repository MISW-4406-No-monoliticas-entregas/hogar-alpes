"""Excepciones específicas del dominio de siniestros."""
from seedwork.dominio.excepciones import ExcepcionDominio


class SiniestroNoExiste(ExcepcionDominio):
    def __init__(self, id_siniestro):
        super().__init__(f"No existe el siniestro {id_siniestro}")


class ConflictoDeConcurrencia(ExcepcionDominio):
    """Otro proceso escribió una versión más nueva del mismo siniestro.

    La lanza el event store cuando la versión que intenta insertar ya existe
    (constraint único en (siniestro_id, version)). No debe silenciarse: el
    llamador reintenta releyendo el agregado, o falla visible (nack en el
    consumidor => Pulsar reentrega el comando).
    """
    def __init__(self, id_siniestro, version):
        super().__init__(
            f"Conflicto de concurrencia en el siniestro {id_siniestro}: "
            f"la versión {version} ya existe en el event store"
        )
