import unittest
import numpy as np
import cv2
from src.analysis import verificar_gradiente_borde


class TestVerificarGradienteBorde(unittest.TestCase):

    def test_verificar_gradiente_borde_basico(self):
        img_gris = np.ones((100, 100), dtype=np.uint8) * 200
        # Dibujar un círculo oscuro (núcleo)
        cv2.circle(img_gris, (50, 50), 15, 50, -1)

        # Contorno del círculo
        contorno = np.array([
            [50, 35], [65, 50], [50, 65], [35, 50]
        ], dtype=np.int32).reshape((-1, 1, 2))

        resultado = verificar_gradiente_borde(img_gris, contorno, umbral_gradiente=5.0)
        self.assertIsInstance(resultado, bool)


if __name__ == '__main__':
    unittest.main()
