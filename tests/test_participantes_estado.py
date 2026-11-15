import unittest

from src.participantes_estado import estado_participante


class ParticipantesEstadoTest(unittest.TestCase):
    def test_pago_vigente_convierte_estado_pendiente_en_activa(self):
        self.assertEqual(estado_participante("Pendiente de pago", "Pagado"), "Activa")

    def test_membresia_por_vencer_sigue_activa(self):
        self.assertEqual(estado_participante("Pendiente de pago", "Por vencer"), "Activa")

    def test_beca_exenta_se_muestra_activa(self):
        self.assertEqual(estado_participante("En evaluación de beca", "Becado (exento)"), "Activa")

    def test_sin_pago_vigente_conserva_estado_de_proceso(self):
        self.assertEqual(estado_participante("En validación de perfil", "Pendiente"), "En validación de perfil")


if __name__ == "__main__":
    unittest.main()
