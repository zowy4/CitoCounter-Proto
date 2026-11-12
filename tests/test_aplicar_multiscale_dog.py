"""
Pruebas unitarias para aplicar_multiscale_dog (Multi-Scale DoG)
"""

import unittest
import numpy as np
import cv2
from src.dog_filter import aplicar_multiscale_dog


class TestAplicarMultiscaleDog(unittest.TestCase):
    def test_multiscale_dog_imagen_sintetica(self):
        # Crear imagen con círculos de diferentes tamaños (pequeño, mediano, grande)
        img = np.zeros((300, 300), dtype=np.uint8)
        cv2.circle(img, (70, 70), 10, 255, -1)     # Pequeño
        cv2.circle(img, (150, 150), 25, 255, -1)   # Mediano
        cv2.circle(img, (230, 230), 45, 255, -1)   # Grande
        
        dog_multiscale = aplicar_multiscale_dog(img)
        
        self.assertEqual(dog_multiscale.shape, (300, 300))
        self.assertEqual(dog_multiscale.dtype, np.uint8)
        self.assertGreater(dog_multiscale.max(), 0)

    def test_multiscale_dog_escalas_personalizadas(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        cv2.circle(img, (50, 50), 20, 255, -1)
        
        escalas = [(1.0, 3.0), (3.0, 6.0)]
        dog_multiscale = aplicar_multiscale_dog(img, escalas=escalas)
        self.assertEqual(dog_multiscale.shape, (100, 100))


if __name__ == '__main__':
    unittest.main()
