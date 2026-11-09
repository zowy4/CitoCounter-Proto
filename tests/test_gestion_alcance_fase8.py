"""
Pruebas unitarias para la Gestión y Alcance de la Fase 8 (CITO-101).
"""

import unittest
from src.gestion_alcance_fase8 import obtener_alcance_fase8

class TestGestionAlcanceFase8(unittest.TestCase):
    """Casos de prueba para el módulo de alcance de la Fase 8."""

    def test_obtener_alcance_fase8(self):
        """Verifica que los objetivos y hitos de la Fase 8 estén correctamente estructurados."""
        alcance = obtener_alcance_fase8()
        self.assertEqual(alcance["clave_jira"], "CITO-101")
        self.assertEqual(alcance["estado"], "Finalizado")
        self.assertTrue(len(alcance["objetivos_principales"]) > 0)
        self.assertTrue(len(alcance["hitos_semanales"]) >= 5)

if __name__ == "__main__":
    unittest.main()
