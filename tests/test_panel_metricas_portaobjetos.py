"""
Pruebas unitarias para el panel de métricas y estadísticas de portaobjetos (CITO-125).
"""

import unittest
from src.panel_metricas_portaobjetos import calcular_metricas_portaobjetos


class TestPanelMetricasPortaobjetos(unittest.TestCase):
    def test_calcular_metricas_vacio(self):
        metricas = calcular_metricas_portaobjetos([])
        self.assertEqual(metricas["total_celulas"], 0)
        self.assertEqual(metricas["indice_riesgo_global"], 0.0)

    def test_calcular_metricas_con_celulas(self):
        celdas = [
            {"clase": "Superficial-Intermediate"},
            {"clase": "Dyskeratotic"},
            {"clase": "Koilocytotic"}
        ]
        metricas = calcular_metricas_portaobjetos(celdas)
        self.assertEqual(metricas["total_celulas"], 3)
        self.assertEqual(metricas["conteo_por_clase"]["Dyskeratotic"], 1)
        self.assertEqual(metricas["conteo_por_clase"]["Koilocytotic"], 1)
        self.assertGreater(metricas["indice_riesgo_global"], 0.0)
        self.assertIn("ALTO RIESGO", metricas["estado_clinico"])


if __name__ == "__main__":
    unittest.main()

