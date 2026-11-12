import unittest
import numpy as np
import cv2
from src.analysis import calcular_solidez

class TestCalcularSolidez(unittest.TestCase):
    def test_solidez_circulo(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        cv2.circle(img, (50, 50), 20, 255, -1)
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.assertTrue(len(contours) > 0)
        solidez = calcular_solidez(contours[0])
        self.assertGreater(solidez, 0.95)

    def test_solidez_contorno_vacio(self):
        contorno_vacio = np.array([], dtype=np.int32).reshape(0, 1, 2)
        solidez = calcular_solidez(contorno_vacio)
        self.assertEqual(solidez, 0.0)

if __name__ == '__main__':
    unittest.main()
