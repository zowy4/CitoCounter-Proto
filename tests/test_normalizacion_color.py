"""
tests/test_normalizacion_color.py - Pruebas unitarias para la normalización de color e iluminación (Fase 3.2).
"""

import unittest
import numpy as np

from src.normalizacion_color import (
    balance_blancos_gris_mundial,
    normalizar_iluminacion_papanicolaou,
)


class TestNormalizacionColor(unittest.TestCase):
    """Casos de prueba para el balance de blancos y normalización Papanicolaou."""

    def test_balance_blancos(self) -> None:
        """Verifica que el balance de blancos funcione en una imagen BGR sintética."""
        img_bgr = np.random.randint(50, 200, (64, 64, 3), dtype=np.uint8)
        balanceada = balance_blancos_gris_mundial(img_bgr)
        self.assertEqual(balanceada.shape, (64, 64, 3))
        self.assertEqual(balanceada.dtype, np.uint8)

    def test_normalizacion_papanicolaou(self) -> None:
        """Verifica la normalización completa de iluminación y color."""
        img_bgr = np.random.randint(100, 240, (100, 100, 3), dtype=np.uint8)
        bgr_norm, gray_norm = normalizar_iluminacion_papanicolaou(img_bgr)
        self.assertEqual(bgr_norm.shape, (100, 100, 3))
        self.assertEqual(gray_norm.shape, (100, 100))
        self.assertEqual(bgr_norm.dtype, np.uint8)
        self.assertEqual(gray_norm.dtype, np.uint8)


if __name__ == "__main__":
    unittest.main()
