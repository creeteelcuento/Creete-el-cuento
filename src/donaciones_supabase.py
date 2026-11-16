"""Persistencia de donaciones y sus comprobantes en Supabase."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import PurePosixPath
from typing import Any

if __package__:
    from .pagos_supabase import preparar_comprobante
else:
    from pagos_supabase import preparar_comprobante


def _fecha(valor: Any) -> date:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor)[:10])


def normalizar_donacion(row: dict[str, Any]) -> dict[str, Any]:
    url = row.get("comprobante_url")
    return {
        "id": row["id"],
        "donante": row["nombre_donante"],
        "monto": float(row["monto"]),
        "fecha": _fecha(row["fecha_donacion"]),
        "comprobante_url": url,
        "comprobante_nombre": PurePosixPath(str(url)).name if url else None,
        "creado_en": row.get("created_at"),
    }


def cargar_donaciones(cliente: Any) -> list[dict[str, Any]]:
    respuesta = cliente.table("Donaciones").select("*").order("fecha_donacion", desc=True).execute()
    donaciones = [normalizar_donacion(row) for row in (respuesta.data or [])]
    return sorted(
        donaciones,
        key=lambda item: (item["fecha"], str(item.get("creado_en") or ""), str(item["id"])),
        reverse=True,
    )


def guardar_donacion(
    cliente: Any,
    bucket: str,
    donante: str,
    monto: int,
    fecha: date,
    archivo: Any | None,
) -> dict[str, Any]:
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero.")
    if not donante.strip():
        raise ValueError("Indica el nombre del donante.")

    ruta_comprobante = None
    almacenamiento = None
    if archivo is not None:
        if not bucket.strip():
            raise RuntimeError("Configura SUPABASE_PAYMENTS_BUCKET con el nombre del bucket privado.")
        contenido, nombre_archivo, tipo_mime = preparar_comprobante(archivo)
        ruta_comprobante = f"donaciones/{nombre_archivo}"
        almacenamiento = cliente.storage.from_(bucket)
        almacenamiento.upload(
            ruta_comprobante,
            contenido,
            file_options={"content-type": tipo_mime, "upsert": "false"},
        )

    datos = {
        "nombre_donante": donante.strip(),
        "monto": monto,
        "fecha_donacion": fecha.isoformat(),
        "comprobante_url": ruta_comprobante,
    }
    try:
        respuesta = cliente.table("Donaciones").insert(datos).select("*").execute()
        if not respuesta.data:
            raise RuntimeError("Supabase no confirmó el registro de la donación.")
    except Exception as error:
        if almacenamiento is not None and ruta_comprobante is not None:
            try:
                almacenamiento.remove([ruta_comprobante])
            except Exception as cleanup_error:
                raise RuntimeError(
                    f"Falló el registro de la donación ({error}) y no se pudo eliminar "
                    f"el comprobante de Storage ({cleanup_error})."
                ) from error
        raise

    return normalizar_donacion(respuesta.data[0])
