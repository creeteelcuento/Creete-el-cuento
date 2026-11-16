import unittest
from datetime import date
from types import SimpleNamespace

from src.becas_supabase import cargar_becas, guardar_beca, revocar_beca


class ConsultaPrueba:
    def __init__(self, cliente):
        self.cliente = cliente
        self.datos = None
        self.filtro_id = None

    def select(self, _columnas):
        return self

    def order(self, _columna, desc=False):
        return self

    def insert(self, datos):
        self.datos = datos
        return self

    def update(self, datos):
        self.datos = datos
        return self

    def eq(self, _columna, valor):
        self.filtro_id = valor
        return self

    def execute(self):
        if self.datos is None:
            return SimpleNamespace(data=self.cliente.filas)
        if self.filtro_id is not None:
            fila = next((r for r in self.cliente.filas if r["id"] == self.filtro_id), None)
            if fila is None:
                return SimpleNamespace(data=[])
            fila.update(self.datos)
            return SimpleNamespace(data=[fila])
        fila = {
            **self.datos,
            "id": len(self.cliente.filas) + 1,
            "created_at": "2026-11-13T10:00:00",
        }
        self.cliente.filas.append(fila)
        return SimpleNamespace(data=[fila])


class ClientePrueba:
    def __init__(self):
        self.filas = []

    def table(self, _nombre):
        return ConsultaPrueba(self)


class BecasSupabaseTest(unittest.TestCase):
    def setUp(self):
        self.cliente = ClientePrueba()

    def test_guarda_beca_con_motivo_y_vigencia(self):
        beca = guardar_beca(
            self.cliente, 7, "Apoyo socioeconómico",
            date(2026, 11, 13), date(2027, 5, 13), date(2026, 11, 13),
        )

        self.assertEqual(beca["participante_id"], 7)
        self.assertEqual(beca["inicio"], date(2026, 11, 13))
        self.assertEqual(beca["termino"], date(2027, 5, 13))
        self.assertEqual(self.cliente.filas[0]["estado"], "Activa")

    def test_carga_normaliza_fechas_guardadas(self):
        self.cliente.filas = [{
            "id": 3,
            "participante_id": 7,
            "motivo": "Apoyo",
            "asignacion": "2026-11-13",
            "inicio": "2026-11-13",
            "termino": "2027-05-13",
            "estado": "Activa",
            "motivo_revocacion": None,
            "fecha_revocacion": None,
        }]

        beca = cargar_becas(self.cliente)[0]

        self.assertEqual(beca["inicio"], date(2026, 11, 13))
        self.assertIsNone(beca["fecha_revocacion"])

    def test_revoca_y_persiste_motivo_y_fecha(self):
        beca = guardar_beca(
            self.cliente, 7, "Apoyo", date(2026, 11, 13), date(2027, 5, 13),
            date(2026, 11, 13),
        )

        revocada = revocar_beca(
            self.cliente, beca["id"], "Cambio de situación", date(2026, 12, 1)
        )

        self.assertEqual(revocada["estado"], "Revocada")
        self.assertEqual(revocada["motivo_revocacion"], "Cambio de situación")
        self.assertEqual(revocada["fecha_revocacion"], date(2026, 12, 1))


if __name__ == "__main__":
    unittest.main()
