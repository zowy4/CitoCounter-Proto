"""
tests/test_barrido_platina.py - Pruebas unitarias para el simulador y guía de barrido de platina (Fase 4.1).
"""

import unittest
import numpy as np

from src.barrido_platina import SimuladorBarridoPlatina


class TestSimuladorBarridoPlatina(unittest.TestCase):
    """Casos de prueba para el patrón de escaneo y mapa de cobertura."""

    def test_inicializacion_patron(self) -> None:
        """Verifica la correcta inicialización del simulador y patrón serpiente."""
        sim = SimuladorBarridoPlatina(filas=3, columnas=3)
        self.assertEqual(len(sim.camino_zigzag), 9)
        self.assertEqual(sim.posicion_actual, (0, 0))

    def test_avanzar_y_cobertura(self) -> None:
        """Verifica el avance en el patrón de zigzag y actualización de cobertura."""
        sim = SimuladorBarridoPlatina(filas=2, columnas=2)
        sim.reiniciar()
        self.assertEqual(sim.posicion_actual, (0, 0))

        siguiente = sim.avanzar()
        self.assertIsNotNone(siguiente)
        self.assertEqual(np.sum(sim.matriz_cobertura), 2)  # (0,0) y la nueva posición

    def test_generar_mapa_visual(self) -> None:
        """Verifica la generación del mapa visual en imagen BGR."""
        sim = SimuladorBarridoPlatina(filas=3, columnas=3)
        mapa = sim.generar_mapa_visual(tamano_celda=50)
        self.assertEqual(mapa.shape, (150, 150, 3))
        self.assertEqual(mapa.dtype, np.uint8)


if __name__ == "__main__":
    unittest.main()
