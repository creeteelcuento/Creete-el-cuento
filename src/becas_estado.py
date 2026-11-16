from __future__ import annotations

from datetime import date
from typing import Any


def beca_vigente(participante: dict[str, Any], beca: dict[str, Any] | None, hoy: date) -> bool:
    if beca is None:
        return str(participante.get("rol", "")).strip().casefold() == "becada"
    return beca["estado"] == "Activa" and beca["inicio"] <= hoy <= beca["termino"]


def fechas_pago(
    participante: dict[str, Any],
    beca: dict[str, Any] | None,
    membresia: dict[str, date],
    hoy: date,
) -> tuple[date | None, date | None]:
    if beca is not None and beca_vigente(participante, beca, hoy):
        return beca["inicio"], beca["termino"]
    return membresia.get("inicio"), membresia.get("vencimiento")


def actividades_de_beca(
    actividades: list[dict[str, Any]], beca: dict[str, Any] | None, hoy: date
) -> list[dict[str, Any]]:
    if beca is None:
        return actividades
    hasta = min(beca["termino"], hoy)
    return [actividad for actividad in actividades if beca["inicio"] <= actividad["fecha"] <= hasta]


def becas_para_listado(
    participantes: list[dict[str, Any]], becas: list[dict[str, Any]]
) -> list[tuple[dict[str, Any], dict[str, Any] | None]]:
    ultimas: dict[Any, dict[str, Any]] = {}
    for beca in sorted(becas, key=lambda registro: registro["id"]):
        ultimas[beca["participante_id"]] = beca

    return [
        (participante, beca)
        for participante in participantes
        if (beca := ultimas.get(participante["id"])) is not None
        or str(participante.get("rol", "")).strip().casefold() == "becada"
    ]
