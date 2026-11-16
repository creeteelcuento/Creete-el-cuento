from __future__ import annotations

_ESTADOS_CON_ACCESO_ACTIVO = {"Pagado", "Por vencer", "Becado (exento)"}


def estado_participante(estado_guardado: str, estado_pago: str) -> str:
    if estado_pago in _ESTADOS_CON_ACCESO_ACTIVO:
        return "Activa"
    return estado_guardado
