"""
tests/test_selector_motor.py - Pruebas unitarias para el selector y benchmark de motores de inferencia (Fase 2.1).
"""

import unittest
import numpy as np

from src.selector_motor import SelectorMotorInferencia


class TestSelectorMotorInferencia(unittest.TestCase):
    """Casos de prueba para el selector de motores de inferencia."""

    def setUp(self) -> None:
        """Configura una imagen sintética de prueba."""
        self.gray = np.random.randint(50, 200, (256, 256), dtype=np.uint8)
        self.original = np.stack([self.gray]*3, axis=-1)

    def test_seleccion_y_procesamiento_dog(self) -> None:
        """Verifica que el motor DoG funcione correctamente desde el selector."""
        selector = SelectorMotorInferencia(motor_por_defecto="dog")
        self.assertEqual(selector.motor_activo, "dog")

        resultado = selector.procesar(self.gray, self.original)
        self.assertEqual(resultado["motor_usado"], "dog")
        self.assertIn("total_celulas", resultado)
        self.assertIn("latencia_ms", resultado)

    def test_cambio_de_motor(self) -> None:
        """Verifica el cambio dinámico entre motores soportados."""
        selector = SelectorMotorInferencia()
        self.assertTrue(selector.establecer_motor("dl"))
        self.assertEqual(selector.motor_activo, "dl")

        resultado = selector.procesar(self.gray, self.original)
        self.assertEqual(resultado["motor_usado"], "dl")

    def test_benchmark_motores(self) -> None:
        """Verifica que el benchmark devuelva latencia y FPS válidos."""
        selector = SelectorMotorInferencia("dog")
        bm = selector.benchmark(self.gray, self.original, iteraciones=3)
        self.assertEqual(bm["motor"], "dog")
        self.assertGreater(bm["latencia_media_ms"], 0.0)
        self.assertGreater(bm["fps_estimado"], 0.0)


if __name__ == "__main__":
    unittest.main()
