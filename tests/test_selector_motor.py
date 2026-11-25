"""
Pruebas unitarias para el Selector de Motor de Inferencia (CITO-106 / ACT-35).
"""

import unittest
import numpy as np
from src.selector_motor import SelectorMotorInferencia

class TestSelectorMotor(unittest.TestCase):
    """Casos de prueba para SelectorMotorInferencia."""

    def test_selector_y_benchmark(self):
        """Verifica la selección de motor, procesamiento y benchmark."""
        selector = SelectorMotorInferencia(motor_por_defecto="dog")
        self.assertEqual(selector.motor_activo, "dog")

        self.assertTrue(selector.establecer_motor("dl"))
        self.assertEqual(selector.motor_activo, "dl")

        # Probar con imagen sintética
        gray = np.zeros((100, 100), dtype=np.uint8)
        original = np.zeros((100, 100, 3), dtype=np.uint8)

        res = selector.procesar(gray, original)
        self.assertIn("motor_usado", res)
        self.assertEqual(res["motor_usado"], "dl")

        bench = selector.benchmark(gray, original, iteraciones=3)
        self.assertIn("latencia_media_ms", bench)
        self.assertIn("fps_estimado", bench)

if __name__ == "__main__":
    unittest.main()

