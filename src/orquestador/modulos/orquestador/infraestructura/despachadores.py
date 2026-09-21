"""Despachadores hacia los topicos de comandos de los otros servicios
(adaptadores de salida).

Todos los topicos son de otros servicios (S2, S10, S7); se publica usando la
copia del esquema de cada dueno (schema/v1/), nunca importando su codigo.

  DespachadorCompensaciones (D): RechazarSiniestro y LiberarProveedor.
  DespachadorPasosFelices (C):   RegistrarSiniestro, ValidarSiniestro,
                                 MarcarValidado y AsignarProveedor.
"""
from seedwork.infraestructura.pulsar import Despachador
from seedwork.infraestructura.utils import tiempo_actual_ms, generar_uuid
from config.settings import (
    PULSAR_URL,
    TOPICO_COMANDOS_SINIESTROS,
    TOPICO_COMANDOS_MATCHING,
    TOPICO_COMANDOS_REGLAS,
)
from modulos.orquestador.infraestructura.schema.v1.comandos_siniestros import (
    ComandoSiniestros,
    DatosComandoSiniestros,
)
from modulos.orquestador.infraestructura.schema.v1.comandos_matching import (
    ComandoMatching,
    DatosComandoMatching,
)
from modulos.orquestador.infraestructura.schema.v1.comandos_reglas import (
    ComandoReglas,
    DatosComandoReglas,
)


def _sobre(clase_sobre, tipo: str, datos):
    return clase_sobre(
        id=generar_uuid(),
        time=tiempo_actual_ms(),
        spec_version="v1",
        type=tipo,
        data=datos,
    )


class DespachadorCompensaciones(Despachador):
    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def publicar_rechazar_siniestro(self, siniestro_id: str, motivo: str):
        mensaje = _sobre(
            ComandoSiniestros, "RechazarSiniestro",
            DatosComandoSiniestros(id_siniestro=siniestro_id, motivo=motivo),
        )
        # clave_particion = id del siniestro => Key_Shared enruta por siniestro.
        self._publicar_mensaje(
            mensaje, TOPICO_COMANDOS_SINIESTROS, ComandoSiniestros,
            clave_particion=siniestro_id,
        )

    def publicar_liberar_proveedor(self, siniestro_id: str, proveedor_id: str):
        mensaje = _sobre(
            ComandoMatching, "LiberarProveedor",
            DatosComandoMatching(id_siniestro=siniestro_id, proveedor_id=proveedor_id),
        )
        self._publicar_mensaje(mensaje, TOPICO_COMANDOS_MATCHING, ComandoMatching)


class DespachadorPasosFelices(Despachador):
    """Los tres comandos que el orquestador emite al avanzar la saga."""

    def __init__(self, url_broker: str = PULSAR_URL):
        super().__init__(url_broker)

    def publicar_evento(self, evento, topico: str):
        raise NotImplementedError

    def publicar_registrar_siniestro(self, partner_id: str, poliza: str, monto: float,
                                     moneda: str, calle: str, ciudad: str, pais: str):
        """Paso 1 hacia S2. Sin id_siniestro todavia: lo genera S2.

        La clave de particion es la poliza porque es lo unico estable que se
        conoce en este punto, y mantiene en orden los mensajes de una misma
        poliza.
        """
        mensaje = _sobre(
            ComandoSiniestros, "RegistrarSiniestro",
            DatosComandoSiniestros(
                partner_id=partner_id,
                poliza=poliza,
                monto=monto,
                moneda=moneda,
                calle=calle,
                ciudad=ciudad,
                pais=pais,
            ),
        )
        self._publicar_mensaje(
            mensaje, TOPICO_COMANDOS_SINIESTROS, ComandoSiniestros,
            clave_particion=poliza,
        )

    def publicar_validar_siniestro(self, siniestro_id: str, partner_id: str,
                                   monto: float, moneda: str, servicio: str, zona: str):
        """Paso 2 hacia S10."""
        mensaje = _sobre(
            ComandoReglas, "ValidarSiniestro",
            DatosComandoReglas(
                id_siniestro=siniestro_id,
                partner_id=partner_id,
                monto=monto,
                moneda=moneda,
                servicio=servicio,
                zona=zona,
            ),
        )
        self._publicar_mensaje(
            mensaje, TOPICO_COMANDOS_REGLAS, ComandoReglas,
            clave_particion=siniestro_id,
        )

    def publicar_marcar_validado(self, siniestro_id: str):
        """Le dice a S2 que el siniestro paso la validacion de reglas."""
        mensaje = _sobre(
            ComandoSiniestros, "MarcarValidado",
            DatosComandoSiniestros(id_siniestro=siniestro_id),
        )
        self._publicar_mensaje(
            mensaje, TOPICO_COMANDOS_SINIESTROS, ComandoSiniestros,
            clave_particion=siniestro_id,
        )

    def publicar_asignar_proveedor(self, siniestro_id: str, servicio: str, zona: str):
        """Paso 3 hacia S7."""
        mensaje = _sobre(
            ComandoMatching, "AsignarProveedor",
            DatosComandoMatching(
                id_siniestro=siniestro_id, servicio=servicio, zona=zona
            ),
        )
        self._publicar_mensaje(
            mensaje, TOPICO_COMANDOS_MATCHING, ComandoMatching,
            clave_particion=siniestro_id,
        )

    def publicar_proveedor_asignado_a_siniestros(self, siniestro_id: str,
                                                 proveedor_id: str):
        """Cierra el circulo en S2: el agregado Siniestro anota su proveedor."""
        mensaje = _sobre(
            ComandoSiniestros, "AsignarProveedor",
            DatosComandoSiniestros(
                id_siniestro=siniestro_id, proveedor_id=proveedor_id
            ),
        )
        self._publicar_mensaje(
            mensaje, TOPICO_COMANDOS_SINIESTROS, ComandoSiniestros,
            clave_particion=siniestro_id,
        )
