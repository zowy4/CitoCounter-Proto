import unittest
import cv2
import numpy as np
from src.dog_filter import aplicar_multiscale_dog


class TestAplicarMultiscaleDog(unittest.TestCase):
    def test_aplicar_multiscale_dog_shape(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        cv2.circle(img, (50, 50), 10, 200, -1)
        dog_uint8, tensor_dog = aplicar_multiscale_dog(img)
        self.assertEqual(dog_uint8.shape, (100, 100))
        self.assertEqual(tensor_dog.shape, (100, 100, 3))
        self.assertEqual(dog_uint8.dtype, np.uint8)


if __name__ == '__main__':
    unittest.main()
