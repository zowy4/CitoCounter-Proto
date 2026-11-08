"""
tests/test_calibracion_escala.py - Pruebas unitarias para la calibración de escala y micrómetros (Fase 3.1).
"""

import unittest

from src.calibracion_escala import CalibradorEscalaMicroscopio


class TestCalibradorEscalaMicroscopio(unittest.TestCase):
    """Casos de prueba para el calibrador de escala de microscopio."""

    def test_calibracion_con_regla(self) -> None:
        """Verifica el cálculo del factor um/px mediante regla micrométrica."""
        calibrador = CalibradorEscalaMicroscopio()
        # 100 píxeles equivalen a 50 micrómetros reales -> 0.5 um/px
        factor = calibrador.calibrar_con_regla(pixeles_medidos=100.0, micras_reales=50.0)
        self.assertAlmostEqual(factor, 0.5)
        self.assertEqual(calibrador.um_por_pixel, 0.5)

    def test_seleccion_aumentos(self) -> None:
        """Verifica la selección de aumentos preestablecidos."""
        calibrador = CalibradorEscalaMicroscopio()
        factor_40x = calibrador.seleccionar_aumento("40x")
        self.assertEqual(factor_40x, 0.25)
        self.assertEqual(calibrador.aumento_actual, "40x")

    def test_conversion_area(self) -> None:
        """Verifica la conversión correcta de área en píxeles a um^2."""
        calibrador = CalibradorEscalaMicroscopio()
        calibrador.um_por_pixel = 2.0  # 2 um por píxel
        # 10 píxeles cuadrados -> 10 * (2.0)^2 = 40 um^2
        area_um2 = calibrador.convertir_area_a_um2(10.0)
        self.assertAlmostEqual(area_um2, 40.0)


if __name__ == "__main__":
    unittest.main()
