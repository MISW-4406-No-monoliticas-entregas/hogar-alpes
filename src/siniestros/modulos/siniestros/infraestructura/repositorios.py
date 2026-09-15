"""Repositorios de siniestros con SQLAlchemy.

`RepositorioSiniestrosEventStore` es el repositorio ACTIVO (event sourcing):
implementa el mismo puerto `RepositorioSiniestros` del dominio, pero en vez de
guardar el estado del agregado persiste sus eventos en `eventos_siniestro` y
lo reconstruye reaplicándolos en orden.

`RepositorioSiniestrosSQLAlchemy` (CRUD de la E3) se conserva como referencia,
pero ya no lo usa ningún handler.
"""
import uuid

from sqlalchemy.exc import IntegrityError

from modulos.siniestros.dominio.repositorios import RepositorioSiniestros
from modulos.siniestros.dominio.entidades import Siniestro
from modulos.siniestros.dominio.excepciones import ConflictoDeConcurrencia
from modulos.siniestros.infraestructura.dto import SiniestroDTO, EventoSiniestroDTO
from modulos.siniestros.infraestructura.mapeadores import MapeadorSiniestroDTO
from modulos.siniestros.infraestructura.mapeadores_eventos import (
    evento_a_dict,
    dict_a_evento,
)


class RepositorioSiniestrosEventStore(RepositorioSiniestros):
    """Event sourcing sobre la tabla eventos_siniestro."""

    def __init__(self, session):
        self.session = session

    def obtener_por_id(self, id: uuid.UUID) -> Siniestro | None:
        filas = (
            self.session.query(EventoSiniestroDTO)
            .filter_by(siniestro_id=str(id))
            .order_by(EventoSiniestroDTO.version)
            .all()
        )
        if not filas:
            return None
        siniestro = Siniestro(id=id if isinstance(id, uuid.UUID) else uuid.UUID(str(id)))
        for fila in filas:
            # Replay: reproduce el efecto de cada evento sin revalidar reglas
            # (ya se validaron cuando el evento se emitió por primera vez).
            siniestro.aplicar(dict_a_evento(fila.tipo, fila.datos))
        siniestro._version_almacenada = filas[-1].version
        return siniestro

    def agregar(self, siniestro: Siniestro):
        self._insertar_eventos_nuevos(siniestro, version_base=0)

    def actualizar(self, siniestro: Siniestro):
        version_base = getattr(siniestro, "_version_almacenada", 0)
        self._insertar_eventos_nuevos(siniestro, version_base=version_base)

    def _insertar_eventos_nuevos(self, siniestro: Siniestro, version_base: int):
        """Inserta solo los eventos aún no persistidos (siniestro.eventos).

        La UoW los recolecta y limpia al hacer commit, así que todo lo que hay
        en `siniestro.eventos` en este punto es nuevo.
        """
        version = version_base
        for evento in siniestro.eventos:
            version += 1
            self.session.add(
                EventoSiniestroDTO(
                    id=str(evento.id),
                    siniestro_id=str(siniestro.id),
                    tipo=type(evento).__name__,
                    version=version,
                    fecha=evento.fecha_evento,
                    datos=evento_a_dict(evento),
                )
            )
        try:
            # flush inmediato: el choque del constraint (siniestro_id, version)
            # debe salir aquí como conflicto de concurrencia, no como un error
            # opaco en el commit de la UoW.
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictoDeConcurrencia(siniestro.id, version) from exc


class RepositorioSiniestrosSQLAlchemy(RepositorioSiniestros):
    """CRUD de la E3 (tabla siniestros). Sustituido por el event store."""

    def __init__(self, session):
        self.session = session
        self.mapeador = MapeadorSiniestroDTO()

    def obtener_por_id(self, id: uuid.UUID) -> Siniestro | None:
        dto = self.session.get(SiniestroDTO, str(id))
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def agregar(self, siniestro: Siniestro):
        self.session.add(self.mapeador.entidad_a_dto(siniestro))

    def actualizar(self, siniestro: Siniestro):
        nuevo = self.mapeador.entidad_a_dto(siniestro)
        self.session.merge(nuevo)
