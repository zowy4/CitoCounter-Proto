import unittest

import numpy as np

from src.dog_filter import _calcular_diferencia_dog


class DogFilterTests(unittest.TestCase):
    def test_diferencia_conserva_valores_negativos(self):
        primer_gaussiano = np.array([[0, 10, 20]], dtype=np.uint8)
        segundo_gaussiano = np.array([[10, 10, 10]], dtype=np.uint8)

        diferencia = _calcular_diferencia_dog(
            primer_gaussiano,
            segundo_gaussiano,
        )

        np.testing.assert_array_equal(
            diferencia,
            np.array([[-10, 0, 10]], dtype=np.float32),
        )


if __name__ == "__main__":
    unittest.main()