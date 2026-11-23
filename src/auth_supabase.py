"""Inicio de sesión de coordinadoras con Supabase Auth."""

from __future__ import annotations

from collections.abc import Callable
import time

from httpx import HTTPError
from supabase import Client, create_client
from supabase_auth.errors import AuthRetryableError


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
    credenciales = {"email": correo.strip(), "password": contrasena}
    for intento in range(2):
        try:
            respuesta = cliente.auth.sign_in_with_password(credenciales)
            break
        except (AuthRetryableError, HTTPError):
            if intento == 1:
                raise
            time.sleep(1)
    if respuesta.session is None:
        raise RuntimeError("Supabase Auth no devolvió una sesión válida.")
    return cliente
