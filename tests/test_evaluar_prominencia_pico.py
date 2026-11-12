import unittest
import numpy as np
from src.analysis import evaluar_prominencia_pico

class TestEvaluarProminenciaPico(unittest.TestCase):
    def test_prominencia_valida(self):
        dog = np.ones((100, 100), dtype=np.uint8) * 50
        dog[50, 50] = 200
        prom = evaluar_prominencia_pico(dog, (50, 50), radio=5)
        self.assertGreater(prom, 100.0)

    def test_prominencia_fuera_de_limites(self):
        dog = np.ones((100, 100), dtype=np.uint8) * 50
        prom = evaluar_prominencia_pico(dog, (200, 200), radio=5)
        self.assertEqual(prom, 0.0)

if __name__ == '__main__':
    unittest.main()
