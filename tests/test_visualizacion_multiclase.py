"""
Pruebas unitarias para el módulo de visualización multiclase (CITO-124).
"""

import unittest
import numpy as np
from src.visualizacion_multiclase import validar_tamano_visualizacion, dibujar_celdas_multiclase


class TestVisualizacionMulticlase(unittest.TestCase):
    def test_validar_tamano_visualizacion_valido(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        # No debe lanzar excepción
        validar_tamano_visualizacion(img)

    def test_validar_tamano_visualizacion_nulo(self):
        with self.assertRaises(ValueError):
            validar_tamano_visualizacion(None)

    def test_dibujar_celdas_multiclase(self):
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        detecciones = [
            {"bbox": [10, 10, 30, 30], "clase": "Superficial-Intermediate"},
            {"centroide": (100, 100), "radio": 20, "clase": "Dyskeratotic"}
        ]
        img_result = dibujar_celdas_multiclase(img, detecciones, mostrar_etiquetas=True)
        self.assertEqual(img_result.shape, (200, 200, 3))


if __name__ == "__main__":
    unittest.main()

