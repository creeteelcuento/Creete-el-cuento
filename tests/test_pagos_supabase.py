import unittest
from datetime import date
from types import SimpleNamespace

from src.pagos_supabase import cargar_pagos, crear_membresias, guardar_pago


class ArchivoPrueba:
    name = "transferencia.pdf"

    def getvalue(self):
        return b"contenido de prueba"


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
        fila = {**self.datos, "id": "uuid-pago", "created_at": "2026-11-12T10:00:00"}
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

    def download(self, ruta):
        return self.archivos[ruta]


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


class PagosSupabaseTest(unittest.TestCase):
    def setUp(self):
        self.cliente = ClientePrueba()

    def test_carga_usa_vencimiento_guardado_y_normaliza_campos(self):
        self.cliente.filas = [{
            "id": "uuid-1",
            "participante_id": 7,
            "monto": 25000,
            "metodo_pago": "PayPal",
            "fecha_pago": "2026-11-10",
            "duracion_meses": 6,
            "fecha_vencimiento": "2027-05-09",
            "comprobante_url": None,
        }]

        pagos = cargar_pagos(self.cliente)

        self.assertEqual(pagos[0]["participante_id"], 7)
        self.assertEqual(pagos[0]["fecha"], date(2026, 11, 10))
        self.assertEqual(pagos[0]["vencimiento"], date(2027, 5, 9))
        self.assertIsNone(pagos[0]["comprobante_url"])

    def test_normaliza_esquema_anterior_con_campos_acentuados(self):
        self.cliente.filas = [{
            "identificación": "uuid-legacy",
            "id_de_participante": 7,
            "monto": 25000,
            "método_pago": "Transferencia",
            "fecha_pago": "2026-11-10",
            "duración_meses": 6,
            "fecha_vencimiento": "2027-05-09",
            "comprobante_url": None,
            "creado_en": "2026-11-10T10:00:00",
        }]

        pago = cargar_pagos(self.cliente)[0]

        self.assertEqual(pago["id"], "uuid-legacy")
        self.assertEqual(pago["participante_id"], 7)
        self.assertEqual(pago["metodo"], "Transferencia")
        self.assertEqual(pago["meses"], 6)
        self.assertEqual(pago["creado_en"], "2026-11-10T10:00:00")

    def test_membresia_usa_el_pago_mas_reciente(self):
        self.cliente.filas = [
            {
                "id": "nuevo",
                "participante_id": 7,
                "monto": 25000,
                "metodo_pago": "PayPal",
                "fecha_pago": "2026-11-12",
                "duracion_meses": 6,
                "fecha_vencimiento": "2027-05-12",
                "created_at": "2026-11-12T10:00:00",
            },
            {
                "id": "anterior",
                "participante_id": 7,
                "monto": 25000,
                "metodo_pago": "PayPal",
                "fecha_pago": "2026-01-12",
                "duracion_meses": 6,
                "fecha_vencimiento": "2026-07-12",
                "created_at": "2026-01-12T10:00:00",
            },
        ]
        pagos = cargar_pagos(self.cliente)

        membresias = crear_membresias(pagos)

        self.assertEqual(membresias[7]["inicio"], date(2026, 11, 12))
        self.assertEqual(membresias[7]["vencimiento"], date(2027, 5, 12))

    def test_guarda_comprobante_y_fila_en_supabase(self):
        pago = guardar_pago(
            self.cliente, "comprobantes-pagos", 7, 25000, "Transferencia",
            date(2026, 11, 12), 6, ArchivoPrueba(), date(2026, 11, 12),
        )

        self.assertEqual(pago["participante_id"], 7)
        self.assertEqual(pago["vencimiento"], date(2027, 5, 12))
        self.assertEqual(pago["comprobante_url"].split("/")[0], "7")
        self.assertEqual(self.cliente.almacenamiento.archivos[pago["comprobante_url"]], b"contenido de prueba")
        self.assertEqual(self.cliente.filas[0]["metodo_pago"], "Transferencia")
        self.assertEqual(self.cliente.filas[0]["duracion_meses"], 6)
        self.assertEqual(self.cliente.filas[0]["participante_id"], 7)
        self.assertEqual(self.cliente.filas[0]["estado"], "al_dia")

    def test_rechaza_transferencia_sin_comprobante(self):
        with self.assertRaisesRegex(ValueError, "requieren un comprobante"):
            guardar_pago(
                self.cliente, "comprobantes-pagos", 7, 25000, "Transferencia",
                date(2026, 11, 12), 6, None, date(2026, 11, 12),
            )

    def test_paypal_permite_guardar_sin_comprobante(self):
        pago = guardar_pago(
            self.cliente, "comprobantes-pagos", 7, 25000, "PayPal",
            date(2026, 11, 12), 6, None, date(2026, 11, 12),
        )

        self.assertIsNone(pago["comprobante_url"])
        self.assertIsNone(self.cliente.filas[0]["comprobante_url"])

    def test_limpia_archivo_si_falla_el_insert(self):
        self.cliente.error_insercion = True

        with self.assertRaisesRegex(RuntimeError, "error de base de datos"):
            guardar_pago(
                self.cliente, "comprobantes-pagos", 7, 25000, "Transferencia",
                date(2026, 11, 12), 6, ArchivoPrueba(), date(2026, 11, 12),
            )

        self.assertEqual(self.cliente.almacenamiento.archivos, {})


if __name__ == "__main__":
    unittest.main()
