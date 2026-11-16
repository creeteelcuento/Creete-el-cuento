"""Persistencia de pagos y comprobantes en Supabase."""

from __future__ import annotations

import mimetypes
import re
import uuid
from calendar import monthrange
from datetime import date, datetime
from pathlib import PurePosixPath
from typing import Any


EXTENSIONES_COMPROBANTE = {".png", ".jpg", ".jpeg", ".pdf"}


def _fecha(valor: Any) -> date:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor)[:10])


def sumar_meses(fecha: date, meses: int) -> date:
    mes_total = fecha.month - 1 + meses
    anio, mes = fecha.year + mes_total // 12, mes_total % 12 + 1
    return date(anio, mes, min(fecha.day, monthrange(anio, mes)[1]))


def _valor(row: dict[str, Any], *nombres: str, default: Any = None) -> Any:
    for nombre in nombres:
        if nombre in row:
            return row[nombre]
    return default


def normalizar_pago(row: dict[str, Any]) -> dict[str, Any]:
    fecha_pago = _fecha(row["fecha_pago"])
    duracion = int(_valor(row, "duracion_meses", "duración_meses", default=1) or 1)
    vencimiento = row.get("fecha_vencimiento")
    comprobante_url = row.get("comprobante_url")
    participante_id = _valor(row, "participante_id", "id_de_participante")
    if participante_id is None:
        raise ValueError("El pago no tiene participante asociado.")
    identificacion = _valor(row, "id", "identificación")
    if identificacion is None:
        identificacion = f"{participante_id}:{fecha_pago.isoformat()}"

    return {
        "id": identificacion,
        "participante_id": participante_id,
        "fecha": fecha_pago,
        "monto": float(row["monto"]),
        "metodo": _valor(row, "metodo_pago", "método_pago", default="Sin especificar"),
        "meses": duracion,
        "inicio": _fecha(row.get("fecha_inicio") or fecha_pago),
        "vencimiento": _fecha(vencimiento) if vencimiento else sumar_meses(fecha_pago, duracion),
        "comprobante_url": comprobante_url,
        "comprobante_nombre": PurePosixPath(str(comprobante_url)).name if comprobante_url else None,
        "creado_en": _valor(row, "created_at", "creado_en"),
    }


def cargar_pagos(cliente: Any) -> list[dict[str, Any]]:
    if cliente is None:
        raise RuntimeError("Falta configurar SUPABASE_URL y SUPABASE_KEY.")
    respuesta = cliente.table("Pagos").select("*").execute()
    pagos = [normalizar_pago(row) for row in (respuesta.data or [])]
    return sorted(
        pagos, key=lambda x: (x["fecha"], str(x.get("creado_en") or ""), str(x["id"])), reverse=True
    )


def crear_membresias(pagos: list[dict[str, Any]]) -> dict[Any, dict[str, date]]:
    membresias: dict[Any, dict[str, date]] = {}
    for pago in sorted(
        pagos, key=lambda x: (x["fecha"], str(x.get("creado_en") or ""), str(x["id"])), reverse=True
    ):
        membresias.setdefault(
            pago["participante_id"],
            {"inicio": pago["inicio"], "vencimiento": pago["vencimiento"]},
        )
    return membresias


def preparar_comprobante(archivo: Any) -> tuple[bytes, str, str]:
    nombre = str(getattr(archivo, "name", "")).replace("\\", "/").rsplit("/", 1)[-1]
    extension = PurePosixPath(nombre).suffix.lower()
    if extension not in EXTENSIONES_COMPROBANTE:
        raise ValueError("El comprobante debe ser PNG, JPG, JPEG o PDF.")

    contenido = archivo.getvalue()
    if not contenido:
        raise ValueError("El archivo de comprobante está vacío.")

    base = PurePosixPath(nombre).stem
    seguro = re.sub(r"[^A-Za-z0-9_-]+", "-", base).strip("-_")[:80] or "comprobante"
    ruta = f"{uuid.uuid4().hex}_{seguro}{extension}"
    tipo_mime = mimetypes.guess_type(nombre)[0] or "application/octet-stream"
    return contenido, ruta, tipo_mime


def guardar_pago(
    cliente: Any,
    bucket: str,
    participante_id: Any,
    monto: int,
    metodo: str,
    fecha_pago: date,
    meses: int,
    archivo: Any | None,
    fecha_actual: date,
) -> dict[str, Any]:
    if cliente is None:
        raise RuntimeError("Falta configurar SUPABASE_URL y SUPABASE_KEY.")
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero.")
    if meses <= 0:
        raise ValueError("La duración de la membresía debe ser mayor que cero.")
    if metodo == "Transferencia" and archivo is None:
        raise ValueError("Los pagos por transferencia requieren un comprobante.")

    vencimiento = sumar_meses(fecha_pago, meses)
    dias_restantes = (vencimiento - fecha_actual).days
    estado = "vencido" if dias_restantes < 0 else "por_vencer" if dias_restantes <= 15 else "al_dia"
    ruta_comprobante = None
    almacenamiento = None

    if archivo is not None:
        if not bucket.strip():
            raise RuntimeError("Configura SUPABASE_PAYMENTS_BUCKET con el nombre del bucket privado.")
        contenido, nombre_archivo, tipo_mime = preparar_comprobante(archivo)
        ruta_comprobante = f"{participante_id}/{nombre_archivo}"
        almacenamiento = cliente.storage.from_(bucket)
        almacenamiento.upload(
            ruta_comprobante,
            contenido,
            file_options={"content-type": tipo_mime, "upsert": "false"},
        )

    datos = {
        "participante_id": participante_id,
        "monto": monto,
        "metodo_pago": metodo,
        "fecha_pago": fecha_pago.isoformat(),
        "duracion_meses": meses,
        "fecha_vencimiento": vencimiento.isoformat(),
        "comprobante_url": ruta_comprobante,
        "estado": estado,
    }
    try:
        respuesta = cliente.table("Pagos").insert(datos).execute()
    except Exception as error:
        if almacenamiento is not None and ruta_comprobante is not None:
            try:
                almacenamiento.remove([ruta_comprobante])
            except Exception as cleanup_error:
                raise RuntimeError(
                    f"Falló el registro del pago ({error}) y no se pudo eliminar el comprobante "
                    f"que quedó en Storage ({cleanup_error})."
                ) from error
        raise

    fila = respuesta.data[0] if respuesta.data else datos
    if "id" not in fila and "identificación" not in fila:
        fila = {**fila, "id": f"{participante_id}:{fecha_pago.isoformat()}:{uuid.uuid4().hex}"}
    return normalizar_pago(fila)


def descargar_comprobante(cliente: Any, bucket: str, ruta: str) -> bytes:
    if cliente is None:
        raise RuntimeError("Falta configurar SUPABASE_URL y SUPABASE_KEY.")
    if not bucket.strip():
        raise RuntimeError("Configura SUPABASE_PAYMENTS_BUCKET con el nombre del bucket privado.")
    contenido = cliente.storage.from_(bucket).download(ruta)
    if not contenido:
        raise RuntimeError("Supabase devolvió un comprobante vacío.")
    return contenido
