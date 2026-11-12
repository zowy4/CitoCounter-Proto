import unittest
import numpy as np
from src.dog_filter import supresion_no_maximos_3d


class TestDetectorMultiscale3D(unittest.TestCase):
    def test_supresion_no_maximos_3d(self):
        tensor = np.zeros((50, 50, 3), dtype=np.float32)
        tensor[25, 25, 1] = 50.0  # Peak at scale 1
        picos = supresion_no_maximos_3d(tensor, umbral=10.0)
        self.assertTrue(len(picos) > 0)
        self.assertEqual(picos[0][:3], (25, 25, 1))


if __name__ == '__main__':
    unittest.main()
