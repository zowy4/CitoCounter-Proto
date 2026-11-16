"""
tests/test_taxonomia_sipakmed.py - Pruebas unitarias para la Taxonomía Clínica SIPaKMeD de 5 Clases (CITO-123).
"""

import unittest
import numpy as np
from src.taxonomia_sipakmed import (
    SIPAKMED_CLASSES,
    clasificar_celda_sipakmed,
    calcular_riesgo_global_sipakmed,
    validar_tamano_taxonomia
)


class TestTaxonomiaSIPaKMeD(unittest.TestCase):
    """Casos de prueba para la taxonomía SIPaKMeD de 5 clases."""

    def test_clasificacion_celdas_individuales(self) -> None:
        """Verifica que cada rango morfométrico asigne la clase SIPaKMeD correcta."""
        # Célula superficial (área pequeña)
        res_sup = clasificar_celda_sipakmed(area_nucleo=45.0, relacion_nc=0.2, hipercromasia_score=0.2)
        self.assertEqual(res_sup["clase"], "Superficial-Intermediate")
        self.assertEqual(res_sup["categoria_clinica"], "Normal")

        # Célula disqueratósica (área grande y alta hipercromasia)
        res_dys = clasificar_celda_sipakmed(area_nucleo=300.0, relacion_nc=0.8, hipercromasia_score=0.9)
        self.assertEqual(res_dys["clase"], "Dyskeratotic")
        self.assertEqual(res_dys["nivel_riesgo"], "Alto")

    def test_calculo_riesgo_global(self) -> None:
        """Verifica el cálculo de agregación de riesgo global para un conjunto de células."""
        predicciones = [
            {"clase": "Superficial-Intermediate"},
            {"clase": "Superficial-Intermediate"},
            {"clase": "Koilocytotic"},
            {"clase": "Dyskeratotic"}
        ]
        res_global = calcular_riesgo_global_sipakmed(predicciones)
        self.assertEqual(res_global["total_celulas"], 4)
        self.assertIn("Alto Riesgo", res_global["riesgo_global"])
        self.assertEqual(res_global["conteo_por_clase"]["Dyskeratotic"], 1)
        self.assertEqual(res_global["conteo_por_clase"]["Koilocytotic"], 1)

    def test_validar_tamano_taxonomia(self) -> None:
        """Verifica la validación de tamaño de imagen para seguridad OWASP."""
        img_valida = np.zeros((10, 10), dtype=np.uint8)
        try:
            validar_tamano_taxonomia(img_valida)
        except ValueError:
            self.fail("validar_tamano_taxonomia lanzó excepción inesperada.")

        img_gigante = np.zeros((5000, 5000, 3), dtype=np.uint8)
        with self.assertRaises(ValueError):
            validar_tamano_taxonomia(img_gigante, tamano_maximo_bytes=1000)


if __name__ == "__main__":
    unittest.main()
