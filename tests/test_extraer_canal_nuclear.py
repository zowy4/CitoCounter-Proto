import unittest
import numpy as np
from src.preprocessing import extraer_canal_nuclear


class TestExtraerCanalNuclear(unittest.TestCase):

    def test_extraer_canal_verde(self):
        img_bgr = np.zeros((50, 50, 3), dtype=np.uint8)
        img_bgr[:, :, 0] = 10  # B
        img_bgr[:, :, 1] = 100 # G
        img_bgr[:, :, 2] = 200 # R

        canal_verde = extraer_canal_nuclear(img_bgr, canal='verde')
        self.assertEqual(canal_verde.shape, (50, 50))
        self.assertTrue(np.all(canal_verde == 100))

    def test_extraer_canal_saturacion(self):
        img_bgr = np.zeros((50, 50, 3), dtype=np.uint8)
        canal_sat = extraer_canal_nuclear(img_bgr, canal='saturacion')
        self.assertEqual(canal_sat.shape, (50, 50))


if __name__ == '__main__':
    unittest.main()
