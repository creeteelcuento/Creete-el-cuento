import unittest
from datetime import date

from src.becas_estado import (
    actividades_de_beca,
    beca_vigente,
    becas_para_listado,
    fechas_pago,
)


class BecasEstadoTest(unittest.TestCase):
    def test_rol_becada_sin_registro_formal_exime_del_pago(self):
        participante = {"id": 1, "rol": "Becada"}

        self.assertTrue(beca_vigente(participante, None, date(2026, 11, 12)))

    def test_revocacion_explicita_prevalece_sobre_el_rol_becada(self):
        participante = {"id": 1, "rol": "Becada"}
        beca = {
            "estado": "Revocada", "inicio": date(2026, 11, 12),
            "termino": date(2027, 5, 12),
        }

        self.assertFalse(beca_vigente(participante, beca, date(2026, 11, 12)))

    def test_beca_expirada_no_exime_del_pago(self):
        participante = {"id": 1, "rol": "Emprendedora"}
        beca = {
            "estado": "Activa", "inicio": date(2026, 5, 11),
            "termino": date(2026, 11, 11),
        }

        self.assertFalse(beca_vigente(participante, beca, date(2026, 11, 12)))

    def test_beca_futura_no_exime_antes_de_su_inicio(self):
        participante = {"id": 1, "rol": "Emprendedora"}
        beca = {
            "estado": "Activa", "inicio": date(2026, 11, 13),
            "termino": date(2027, 5, 13),
        }

        self.assertFalse(beca_vigente(participante, beca, date(2026, 11, 12)))

    def test_fechas_de_beca_vigente_se_muestran_en_pagos(self):
        participante = {"id": 1, "rol": "Becada"}
        beca = {
            "estado": "Activa", "inicio": date(2026, 11, 1),
            "termino": date(2027, 5, 1),
        }
        membresia = {"inicio": date(2026, 10, 1), "vencimiento": date(2027, 4, 1)}

        self.assertEqual(
            fechas_pago(participante, beca, membresia, date(2026, 11, 13)),
            (date(2026, 11, 1), date(2027, 5, 1)),
        )

    def test_becada_sin_asignacion_formal_no_intenta_leer_fechas(self):
        participante = {"id": 1, "rol": "Becada"}

        self.assertEqual(
            fechas_pago(participante, None, {}, date(2026, 11, 13)),
            (None, None),
        )

    def test_sin_periodo_formal_usa_asistencia_historica(self):
        actividades = [{"id": 1}, {"id": 2}]

        self.assertEqual(
            actividades_de_beca(actividades, None, date(2026, 11, 13)),
            actividades,
        )

    def test_periodo_formal_filtra_actividades_por_vigencia(self):
        actividades = [
            {"id": 1, "fecha": date(2026, 10, 31)},
            {"id": 2, "fecha": date(2026, 11, 1)},
            {"id": 3, "fecha": date(2026, 11, 13)},
            {"id": 4, "fecha": date(2026, 11, 14)},
        ]
        beca = {"inicio": date(2026, 11, 1), "termino": date(2027, 5, 1)}

        resultado = actividades_de_beca(actividades, beca, date(2026, 11, 13))

        self.assertEqual([a["id"] for a in resultado], [2, 3])

    def test_listado_incluye_becadas_por_rol_y_registros_formales(self):
        becada = {"id": 1, "rol": "Becada"}
        emprendedora = {"id": 2, "rol": "Emprendedora"}
        registros = [{
            "id": 1,
            "participante_id": 2,
            "estado": "Activa",
            "inicio": date(2026, 11, 12),
            "termino": date(2027, 5, 12),
        }]

        resultado = becas_para_listado([becada, emprendedora], registros)

        self.assertEqual([(p["id"], b is None) for p, b in resultado], [(1, True), (2, False)])

    def test_el_ultimo_registro_prevalece_y_no_duplica_por_rol(self):
        participante = {"id": 1, "rol": "Becada"}
        registros = [
            {"id": 1, "participante_id": 1, "estado": "Activa"},
            {"id": 2, "participante_id": 1, "estado": "Revocada"},
        ]

        resultado = becas_para_listado([participante], registros)

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0][1]["estado"], "Revocada")


if __name__ == "__main__":
    unittest.main()
