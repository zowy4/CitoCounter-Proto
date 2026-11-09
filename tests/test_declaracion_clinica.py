"""
Pruebas unitarias para la Declaración de Exención Clínica (Fase 9.1).
"""

import unittest
from src.declaracion_clinica import obtener_declaracion_exencion, TEXTO_EXENCION_CLINICA

class TestDeclaracionClinica(unittest.TestCase):
    """Casos de prueba para la exención clínica."""

    def test_obtener_declaracion(self):
        """Verifica que la declaración contenga los avisos obligatorios de no diagnóstico."""
        dec = obtener_declaracion_exencion()
        self.assertEqual(dec["proyecto"], "CitoCounter-Proto")
        self.assertIn("NO es un dispositivo médico", dec["advertencia_legal"])
        self.assertIn("Investigación", dec["uso_autorizado"])

    def test_texto_exencion_presente(self):
        """Verifica que el texto de exención esté definido y no esté vacío."""
        self.assertTrue(len(TEXTO_EXENCION_CLINICA) > 50)
        self.assertIn("exclusivamente por personal médico", TEXTO_EXENCION_CLINICA)

if __name__ == "__main__":
    unittest.main()
