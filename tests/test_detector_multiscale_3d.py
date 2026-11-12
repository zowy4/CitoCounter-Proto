"""
Pruebas unitarias para detector_multiscale_3d (Banco de Filtros DoG y No-Máximos 3D)
"""

import unittest
import numpy as np
import cv2
from src.dog_filter import detector_multiscale_3d


class TestDetectorMultiscale3D(unittest.TestCase):
    def test_detector_multiscale_3d_imagen_sintetica(self):
        # Crear imagen con núcleos de diferentes tamaños
        img = np.zeros((200, 200), dtype=np.uint8)
        cv2.circle(img, (50, 50), 8, 255, -1)     # Pequeño
        cv2.circle(img, (100, 100), 20, 255, -1)   # Mediano
        cv2.circle(img, (150, 150), 35, 255, -1)   # Grande
        
        resultado = detector_multiscale_3d(img)
        
        self.assertEqual(resultado.shape, (200, 200))
        self.assertEqual(resultado.dtype, np.uint8)
        self.assertGreater(resultado.max(), 0)

    def test_detector_multiscale_3d_imagen_vacia(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        resultado = detector_multiscale_3d(img)
        self.assertEqual(resultado.shape, (100, 100))


if __name__ == '__main__':
    unittest.main()
