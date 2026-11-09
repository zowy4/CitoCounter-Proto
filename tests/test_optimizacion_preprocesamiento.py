"""
Pruebas unitarias para el módulo de optimización de preprocesamiento (CITO-107 / ACT-36).
"""

import unittest
import numpy as np
from src.optimizacion_preprocesamiento import (
    optimizar_preprocesamiento,
    validar_tamano_imagen,
    benchmark_preprocesamiento
)

class OptimizacionPreprocesamientoTests(unittest.TestCase):
    """Casos de prueba para preprocesamiento y conversión vectorial."""

    def test_optimizar_preprocesamiento_gris(self):
        """Verifica el preprocesamiento CLAHE en imagen en escala de grises."""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        resultado = optimizar_preprocesamiento(img)
        self.assertEqual(resultado.shape, (100, 100))
        self.assertEqual(resultado.dtype, np.uint8)

    def test_optimizar_preprocesamiento_color(self):
        """Verifica el preprocesamiento CLAHE en imagen a color BGR."""
        img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        resultado = optimizar_preprocesamiento(img)
        self.assertEqual(resultado.shape, (100, 100))
        self.assertEqual(resultado.dtype, np.uint8)

    def test_validar_tamano_imagen_nula(self):
        """Verifica que se lance ValueError con imagen nula."""
        with self.assertRaises(ValueError):
            validar_tamano_imagen(None)

    def test_benchmark_preprocesamiento(self):
        """Verifica que el benchmark retorne métricas válidas."""
        img = np.random.randint(0, 256, (64, 64), dtype=np.uint8)
        metricas = benchmark_preprocesamiento(img, iteraciones=5)
        self.assertIn("tiempo_promedio_ms", metricas)
        self.assertIn("rendimiento_fps", metricas)
        self.assertGreater(metricas["rendimiento_fps"], 0)

if __name__ == "__main__":
    unittest.main()
