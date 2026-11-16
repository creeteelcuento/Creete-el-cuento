"""Persistencia de asignaciones de beca en Supabase."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any


def _fecha(valor: Any) -> date:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor)[:10])


def normalizar_beca(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "participante_id": row["participante_id"],
        "motivo": row["motivo"],
        "asignacion": _fecha(row["asignacion"]),
        "inicio": _fecha(row["inicio"]),
        "termino": _fecha(row["termino"]),
        "estado": row["estado"],
        "motivo_revocacion": row.get("motivo_revocacion"),
        "fecha_revocacion": _fecha(row["fecha_revocacion"]) if row.get("fecha_revocacion") else None,
    }


def cargar_becas(cliente: Any) -> list[dict[str, Any]]:
    respuesta = cliente.table("Becas").select("*").order("id", desc=True).execute()
    return [normalizar_beca(row) for row in (respuesta.data or [])]


def guardar_beca(
    cliente: Any,
    participante_id: Any,
    motivo: str,
    inicio: date,
    termino: date,
    asignacion: date,
) -> dict[str, Any]:
    datos = {
        "participante_id": participante_id,
        "motivo": motivo,
        "asignacion": asignacion.isoformat(),
        "inicio": inicio.isoformat(),
        "termino": termino.isoformat(),
        "estado": "Activa",
    }
    respuesta = cliente.table("Becas").insert(datos).select("*").execute()
    if not respuesta.data:
        raise RuntimeError("Supabase no confirmó la creación de la asignación de beca.")
    return normalizar_beca(respuesta.data[0])


def revocar_beca(
    cliente: Any, beca_id: Any, motivo: str, fecha_revocacion: date
) -> dict[str, Any]:
    datos = {
        "estado": "Revocada",
        "motivo_revocacion": motivo,
        "fecha_revocacion": fecha_revocacion.isoformat(),
    }
    respuesta = cliente.table("Becas").update(datos).eq("id", beca_id).select("*").execute()
    if not respuesta.data:
        raise RuntimeError("Supabase no confirmó la revocación de la beca.")
    return normalizar_beca(respuesta.data[0])
