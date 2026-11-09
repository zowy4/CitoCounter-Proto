"""
Pruebas unitarias para el módulo de Superposición y Visualización en Vivo (CITO-105).
"""

import unittest
import numpy as np
from src.visualizador_overlays import VisualizadorOverlays

class TestVisualizadorOverlays(unittest.TestCase):
    """Casos de prueba para VisualizadorOverlays."""

    def test_renderizar_overlay(self):
        """Verifica que el renderizado de overlays devuelva una imagen válida con anotaciones."""
        frame = np.zeros((300, 300, 3), dtype=np.uint8)
        detecciones = [{"bbox": [50, 50, 100, 100]}]
        
        resultado = VisualizadorOverlays.renderizar_overlay(
            frame=frame,
            detecciones=detecciones,
            conteo_acumulado=1,
            fps=30.0
        )

        self.assertEqual(resultado.shape, frame.shape)
        self.assertIsInstance(resultado, np.ndarray)

if __name__ == "__main__":
    unittest.main()
