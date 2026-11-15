import unittest
from types import SimpleNamespace

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


if __name__ == "__main__":
    unittest.main()
