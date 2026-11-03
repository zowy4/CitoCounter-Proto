"""Pruebas unitarias para src/herlev_evaluation.py (CITO-95, J-41)."""

import unittest
from pathlib import Path
from src.herlev_evaluation import (
    cargar_celulas_gt,
    extraer_centroides_predichos,
    calcular_metricas_emparejamiento,
)


class HerlevEvaluationTests(unittest.TestCase):
    """Pruebas para las funciones de evaluación Herlev."""

    def test_cargar_celulas_gt_inexistente(self):
        """Verifica comportamiento con archivo CSV inexistente."""
        res = cargar_celulas_gt(Path("ruta/inexistente.csv"))
        self.assertEqual(res, [])

    def test_extraer_centroides_predichos_vacio(self):
        """Verifica extracción con resultados vacíos."""
        res = extraer_centroides_predichos({})
        self.assertEqual(res, [])

    def test_calcular_metricas_emparejamiento_vacio(self):
        """Verifica métricas con listas vacías (casos edge)."""
        tp, fp, fn, p, r, f1, jacc = calcular_metricas_emparejamiento([], [], 10.0)
        self.assertEqual(tp, 0)
        self.assertEqual(fp, 0)
        self.assertEqual(fn, 0)
        self.assertEqual(f1, 0.0)

    def test_calcular_metricas_emparejamiento_perfecto(self):
        """Verifica emparejamiento exacto."""
        pred = [(10, 10), (20, 20)]
        gt = [(10.5, 10.5), (20.1, 20.1)]
        tp, fp, fn, p, r, f1, jacc = calcular_metricas_emparejamiento(pred, gt, 5.0)
        self.assertEqual(tp, 2)
        self.assertEqual(fp, 0)
        self.assertEqual(fn, 0)
        self.assertAlmostEqual(f1, 1.0)


if __name__ == "__main__":
    unittest.main()
