"""Inicio de sesión de coordinadoras con Supabase Auth."""

from __future__ import annotations

from collections.abc import Callable

from supabase import Client, create_client


def iniciar_sesion(
    url: str,
    clave: str,
    correo: str,
    contrasena: str,
    crear_cliente: Callable[[str, str], Client] = create_client,
) -> Client:
    if not url or not clave:
        raise ValueError("Configura SUPABASE_URL y SUPABASE_KEY.")
    if not correo.strip() or not contrasena:
        raise ValueError("Ingresa tu correo y contraseña.")

    cliente = crear_cliente(url, clave)
    respuesta = cliente.auth.sign_in_with_password(
        {"email": correo.strip(), "password": contrasena}
    )
    if respuesta.session is None:
        raise RuntimeError("Supabase Auth no devolvió una sesión válida.")
    return cliente
