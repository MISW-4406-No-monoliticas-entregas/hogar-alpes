"""Implementación de la Unidad de Trabajo con SQLAlchemy (adaptador de salida)."""
from seedwork.infraestructura.uow import UnidadDeTrabajo


class UnidadDeTrabajoSQLAlchemy(UnidadDeTrabajo):
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self.session = None
        self._agregados: list = []
        self.repositorios: dict = {}

    def __enter__(self):
        self.session = self._session_factory()
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        if self.session is not None:
            self.session.close()
            self.session = None

    def registrar_agregado(self, agregado):
        """Marca un agregado como tocado para recolectar sus eventos al commit."""
        if agregado not in self._agregados:
            self._agregados.append(agregado)

    def _agregados_tocados(self) -> list:
        return list(self._agregados)

    def _commit(self):
        self.session.commit()

    def rollback(self):
        if self.session is not None:
            self.session.rollback()
        self._agregados = []
