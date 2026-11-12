import unittest
import numpy as np
from src.preprocessing import corregir_iluminacion_fondo

class TestCorregirIluminacionFondo(unittest.TestCase):
    def test_corregir_iluminacion_valida(self):
        img = np.random.randint(50, 200, (100, 100), dtype=np.uint8)
        corregida = corregir_iluminacion_fondo(img, sigma_fondo=20)
        self.assertEqual(corregida.shape, (100, 100))
        self.assertEqual(corregida.dtype, np.uint8)

    def test_corregir_iluminacion_vacia(self):
        img_vacia = np.array([], dtype=np.uint8)
        with self.assertRaises(ValueError):
            corregir_iluminacion_fondo(img_vacia)

if __name__ == '__main__':
    unittest.main()
