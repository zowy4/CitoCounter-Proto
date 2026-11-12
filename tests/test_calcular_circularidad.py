import unittest
import numpy as np
import cv2
from src.analysis import calcular_circularidad

class TestCalcularCircularidad(unittest.TestCase):
    def test_circularidad_circulo_perfecto(self):
        # Crear imagen con un círculo de radio mayor para mejor aproximación de píxeles
        img = np.zeros((200, 200), dtype=np.uint8)
        cv2.circle(img, (100, 100), 50, 255, -1)
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.assertTrue(len(contours) > 0)
        circ = calcular_circularidad(contours[0])
        self.assertGreater(circ, 0.85)

    def test_circularidad_contorno_vacio(self):
        contorno_vacio = np.array([], dtype=np.int32).reshape(0, 1, 2)
        circ = calcular_circularidad(contorno_vacio)
        self.assertEqual(circ, 0.0)

if __name__ == '__main__':
    unittest.main()
