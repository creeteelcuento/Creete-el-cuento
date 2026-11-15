import unittest
from datetime import date
from types import SimpleNamespace

from src.donaciones_supabase import cargar_donaciones, guardar_donacion


class ArchivoPrueba:
    name = "donacion.pdf"

    def getvalue(self):
        return b"comprobante de prueba"


class ConsultaPrueba:
    def __init__(self, cliente):
        self.cliente = cliente
        self.datos = None

    def select(self, _columnas):
        return self

    def order(self, _columna, desc=False):
        return self

    def insert(self, datos):
        self.datos = datos
        return self

    def execute(self):
        if self.datos is None:
            return SimpleNamespace(data=self.cliente.filas)
        if self.cliente.error_insercion:
            raise RuntimeError("error de base de datos")
        fila = {
            **self.datos,
            "id": "uuid-donacion",
            "created_at": "2026-11-13T10:00:00",
        }
        self.cliente.filas.append(fila)
        return SimpleNamespace(data=[fila])


class AlmacenamientoPrueba:
    def __init__(self):
        self.archivos = {}

    def upload(self, ruta, contenido, file_options):
        self.archivos[ruta] = contenido
        self.file_options = file_options

    def remove(self, rutas):
        for ruta in rutas:
            self.archivos.pop(ruta, None)


class ClientePrueba:
    def __init__(self):
        self.filas = []
        self.error_insercion = False
        self.almacenamiento = AlmacenamientoPrueba()

    def table(self, _nombre):
        return ConsultaPrueba(self)

    @property
    def storage(self):
        return self

    def from_(self, _bucket):
        return self.almacenamiento


class DonacionesSupabaseTest(unittest.TestCase):
    def setUp(self):
        self.cliente = ClientePrueba()

    def test_carga_donaciones_y_normaliza_campos_de_supabase(self):
        self.cliente.filas = [{
            "id": "uuid-1",
            "nombre_donante": "Donante de prueba",
            "monto": 50000,
            "fecha_donacion": "2026-11-13",
            "comprobante_url": None,
            "created_at": "2026-11-13T10:00:00",
        }]

        donacion = cargar_donaciones(self.cliente)[0]

        self.assertEqual(donacion["donante"], "Donante de prueba")
        self.assertEqual(donacion["monto"], 50000)
        self.assertEqual(donacion["fecha"], date(2026, 11, 13))

    def test_guarda_donacion_y_comprobante_en_supabase_y_storage(self):
        donacion = guardar_donacion(
            self.cliente, "comprobantes-pagos", "Donante de prueba",
            50000, date(2026, 11, 13), ArchivoPrueba(),
        )

        self.assertEqual(donacion["id"], "uuid-donacion")
        self.assertEqual(donacion["fecha"], date(2026, 11, 13))
        self.assertTrue(donacion["comprobante_url"].startswith("donaciones/"))
        self.assertEqual(
            self.cliente.almacenamiento.archivos[donacion["comprobante_url"]],
            b"comprobante de prueba",
        )
        self.assertEqual(self.cliente.filas[0]["nombre_donante"], "Donante de prueba")

    def test_guarda_donacion_sin_comprobante(self):
        donacion = guardar_donacion(
            self.cliente, "comprobantes-pagos", "Donante de prueba",
            50000, date(2026, 11, 13), None,
        )

        self.assertIsNone(donacion["comprobante_url"])

    def test_limpia_comprobante_si_falla_el_insert(self):
        self.cliente.error_insercion = True

        with self.assertRaisesRegex(RuntimeError, "error de base de datos"):
            guardar_donacion(
                self.cliente, "comprobantes-pagos", "Donante de prueba",
                50000, date(2026, 11, 13), ArchivoPrueba(),
            )

        self.assertEqual(self.cliente.almacenamiento.archivos, {})


if __name__ == "__main__":
    unittest.main()
