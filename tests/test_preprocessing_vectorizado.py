"""
tests/test_preprocessing_vectorizado.py - Pruebas unitarias para el preprocesamiento vectorizado (Fase 2.2).
"""

import unittest
import numpy as np

from src.preprocessing_vectorizado import (
    convertir_a_gris_vectorizado,
    mejorar_contraste_vectorizado,
    preprocesar_lote_vectorizado,
)


class TestPreprocessingVectorizado(unittest.TestCase):
    """Casos de prueba para las funciones vectorizadas de preprocesamiento."""

    def test_convertir_a_gris_vectorizado(self) -> None:
        """Verifica la conversión a grises vectorizada en imágenes BGR."""
        img_bgr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        gray = convertir_a_gris_vectorizado(img_bgr)
        self.assertEqual(gray.shape, (100, 100))
        self.assertEqual(gray.dtype, np.uint8)

    def test_mejorar_contraste_vectorizado(self) -> None:
        """Verifica la aplicación de CLAHE vectorizado."""
        img_gray = np.random.randint(50, 200, (100, 100), dtype=np.uint8)
        mejorada = mejorar_contraste_vectorizado(img_gray)
        self.assertEqual(mejorada.shape, (100, 100))
        self.assertEqual(mejorada.dtype, np.uint8)

    def test_preprocesar_lote_vectorizado(self) -> None:
        """Verifica el procesamiento por lotes vectorizado."""
        lote = np.random.randint(0, 255, (5, 64, 64, 3), dtype=np.uint8)
        lote_procesado = preprocesar_lote_vectorizado(lote)
        self.assertEqual(lote_procesado.shape, (5, 64, 64))
        self.assertEqual(lote_procesado.dtype, np.uint8)


if __name__ == "__main__":
    unittest.main()
