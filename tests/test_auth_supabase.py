import unittest
from types import SimpleNamespace
from unittest.mock import patch

from httpx import ReadError, Request
from src.auth_supabase import iniciar_sesion


class AuthFalso:
    def __init__(self, session):
        self.session = session
        self.credenciales = None

    def sign_in_with_password(self, credenciales):
        self.credenciales = credenciales
        return SimpleNamespace(session=self.session)


class ClienteFalso:
    def __init__(self, session):
        self.auth = AuthFalso(session)


class SupabaseAuthTest(unittest.TestCase):
    def test_inicia_sesion_y_normaliza_el_correo(self):
        cliente = ClienteFalso(session=object())
        llamadas = []

        def crear_cliente(url, clave):
            llamadas.append((url, clave))
            return cliente

        resultado = iniciar_sesion(
            "https://example.supabase.co",
            "publishable-test",
            "  user@example.test ",
            "test-password",
            crear_cliente,
        )

        self.assertIs(resultado, cliente)
        self.assertEqual(llamadas, [("https://example.supabase.co", "publishable-test")])
        self.assertEqual(
            cliente.auth.credenciales,
            {"email": "user@example.test", "password": "test-password"},
        )

    def test_rechaza_credenciales_vacias_sin_crear_cliente(self):
        def crear_cliente(url, clave):
            self.fail(f"No debe crear un cliente con credenciales vacías: {url}, {clave}.")

        with self.assertRaisesRegex(ValueError, "correo y contraseña"):
            iniciar_sesion(
                "https://example.supabase.co", "publishable-test", " ", "", crear_cliente
            )

    def test_rechaza_respuesta_sin_sesion(self):
        cliente = ClienteFalso(session=None)

        def crear_cliente(url, clave):
            self.assertEqual((url, clave), ("https://example.supabase.co", "publishable-test"))
            return cliente

        with self.assertRaisesRegex(RuntimeError, "sesión válida"):
            iniciar_sesion(
                "https://example.supabase.co",
                "publishable-test",
                "user@example.test",
                "test-password",
                crear_cliente,
            )

    def test_reintenta_una_falla_transitoria_de_http(self):
        class AuthConReintento:
            def __init__(self):
                self.llamadas = 0

            def sign_in_with_password(self, credenciales):
                self.llamadas += 1
                if self.llamadas == 1:
                    raise ReadError("transient", request=Request("POST", "https://example.test"))
                return SimpleNamespace(session=object())

        auth = AuthConReintento()
        cliente = SimpleNamespace(auth=auth)

        with patch("src.auth_supabase.time.sleep", return_value=None):
            resultado = iniciar_sesion(
                "https://example.supabase.co",
                "publishable-test",
                "user@example.test",
                "test-password",
                lambda url, clave: cliente,
            )

        self.assertIs(resultado, cliente)
        self.assertEqual(auth.llamadas, 2)


if __name__ == "__main__":
    unittest.main()
