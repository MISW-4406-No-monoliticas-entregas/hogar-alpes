"""Fabrica del agregado Saga."""
from dataclasses import dataclass

from seedwork.dominio.fabricas import Fabrica
from modulos.orquestador.dominio.entidades import Saga


@dataclass
class FabricaSaga(Fabrica):
    def crear_objeto(self, obj, mapeador=None):
        raise NotImplementedError

    def iniciar_saga(self, siniestro_id: str) -> Saga:
        saga = Saga()
        saga.iniciar(siniestro_id)
        return saga

    def iniciar_saga_pendiente(self, partner_id: str, poliza: str, servicio: str,
                               zona: str, monto: float, moneda: str, calle: str,
                               ciudad: str, pais: str) -> Saga:
        saga = Saga()
        saga.iniciar_pendiente(
            partner_id=partner_id,
            poliza=poliza,
            servicio=servicio,
            zona=zona,
            monto=monto,
            moneda=moneda,
            calle=calle,
            ciudad=ciudad,
            pais=pais,
        )
        return saga
