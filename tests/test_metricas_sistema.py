import unittest
from src.metricas_sistema import (
    calcular_metricas_imagen,
    metricas_conjunto,
    reporte_resumen,
)


class MetricasSistemaTests(unittest.TestCase):
    def test_calcular_metricas_imagen_basicas(self):
        metricas = calcular_metricas_imagen(
            total_celulas=10,
            normales=6,
            sospechosas=2,
            frontera=2,
            porcentaje_riesgo=20.0,
        )

        self.assertIn("precision", metricas)
        self.assertIn("recall", metricas)
        self.assertIn("f1", metricas)
        self.assertIn("razon_sospechosas", metricas)
        self.assertIn("porcentaje_riesgo", metricas)
        self.assertIn("frontera", metricas)
        self.assertIn("riesgo_elevado", metricas)
        self.assertIn("consistencia", metricas)

    def test_metricas_imagen_con_cero_celulas(self):
        metricas = calcular_metricas_imagen(
            total_celulas=0,
            normales=0,
            sospechosas=0,
            frontera=0,
            porcentaje_riesgo=0.0,
        )

        self.assertEqual(metricas["precision"], 0.0)
        self.assertEqual(metricas["recall"], 1.0)  # sin normales vs total = 1.0 por definición
        self.assertEqual(metricas["f1"], 0.0)
        self.assertEqual(metricas["consistencia"], 1.0)

    def test_metricas_conjunto_vacio(self):
        m = metricas_conjunto(historial=[])
        self.assertEqual(m["total_ejecuciones"], 0)
        self.assertEqual(m["imagenes_unicas"], 0)
        self.assertEqual(m["total_celulas_promedio"], 0.0)

    def test_metricas_con_con_historial(self):
        hist = [
            {"total_celulas": 10, "normales": 6, "sospechosas": 2, "porcentaje_riesgo": 20.0, "frontera": 2},
            {"total_celulas": 8, "normales": 5, "sospechosas": 1, "porcentaje_riesgo": 12.5, "frontera": 1},
        ]
        m = metricas_conjunto(historial=hist)

        self.assertEqual(m["total_ejecuciones"], 2)
        self.assertEqual(m["imagenes_unicas"], 2)
        self.assertAlmostEqual(m["total_celulas_promedio"], 9.0)
        self.assertAlmostEqual(m["riesgo_promedio"], 16.25)
        self.assertAlmostEqual(m["tasa_riesgo_alto"], 100.0)

    def test_reporte_resumen_vacio(self):
        reporte = reporte_resumen(historial=[])
        self.assertIn("Ejecuciones registradas: 0", reporte)
        self.assertIn("FIN DEL REPORTE", reporte)

    def test_reporte_con_historial(self):
        hist = [
            {"total_celulas": 10, "normales": 6, "sospechosas": 2, "porcentaje_riesgo": 20.0, "frontera": 2},
        ]
        reporte = reporte_resumen(historial=hist)
        self.assertIn("Ejecuciones registradas: 1", reporte)
        self.assertIn("FIN DEL REPORTE", reporte)


if __name__ == "__main__":
    unittest.main()