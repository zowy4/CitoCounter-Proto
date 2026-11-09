"""
tests/test_protocolo_microscopio_real.py - Pruebas unitarias para el protocolo de validación en microscopio real (Fase 6.1).
"""

import unittest
import os
import json
from src.protocolo_microscopio_real import ProtocoloMicroscopioReal


class TestProtocoloMicroscopioReal(unittest.TestCase):
    """Casos de prueba para el registro y validación con laminillas físicas."""

    def setUp(self) -> None:
        """Configuración inicial para pruebas con archivo temporal."""
        self.archivo_test = "data/results/test_bitacora_microscopio.json"
        if os.path.exists(self.archivo_test):
            os.remove(self.archivo_test)
        self.protocolo = ProtocoloMicroscopioReal(ruta_bitacora=self.archivo_test)

    def tearDown(self) -> None:
        """Limpieza posterior a las pruebas."""
        if os.path.exists(self.archivo_test):
            os.remove(self.archivo_test)

    def test_registrar_prueba_fisica(self) -> None:
        """Verifica el registro correcto de una prueba con laminilla y cálculo de error."""
        res = self.protocolo.registrar_prueba_fisica(
            laminilla_id="LAM-001",
            aumento="40x",
            tiempo_exposicion_ms=15.0,
            ganancia=2.0,
            conteo_manual=50,
            conteo_sistema=48,
            observaciones="Tinción Papanicolaou estándar"
        )

        self.assertEqual(res["laminilla_id"], "LAM-001")
        self.assertEqual(res["error_absoluto"], 2)
        self.assertAlmostEqual(res["error_relativo_pct"], 4.0)

        resumen = self.protocolo.obtener_resumen()
        self.assertEqual(resumen["total_pruebas"], 1)
        self.assertEqual(resumen["error_relativo_promedio_pct"], 4.0)


if __name__ == "__main__":
    unittest.main()
