"""Regresiones de la segmentación HSV de CITO-90."""

import unittest

import numpy as np

from src.preprocessing import segmentar_por_hsv


class SegmentacionHsvTests(unittest.TestCase):
    def test_saturation_detecta_region_coloreada_y_descarta_fondo_gris(self):
        imagen = np.full((40, 40, 3), 120, dtype=np.uint8)
        imagen[12:28, 12:28] = (255, 0, 0)

        mascara = segmentar_por_hsv(imagen, umbral_sat=100, metodo="saturation")

        self.assertEqual(mascara[20, 20], 255)
        self.assertEqual(mascara[2, 2], 0)

    def test_value_detecta_region_brillante(self):
        imagen = np.zeros((40, 40, 3), dtype=np.uint8)
        imagen[12:28, 12:28] = (220, 220, 220)

        mascara = segmentar_por_hsv(imagen, umbral_val=100, metodo="value")

        self.assertEqual(mascara[20, 20], 255)
        self.assertEqual(mascara[2, 2], 0)

    def test_rechaza_metodo_hsv_desconocido(self):
        with self.assertRaises(ValueError):
            segmentar_por_hsv(np.zeros((10, 10, 3), dtype=np.uint8), metodo="hue")


if __name__ == "__main__":
    unittest.main()
