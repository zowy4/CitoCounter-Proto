"""
tests/test_protocolo_metricas_clinicas.py - Pruebas unitarias para el protocolo de métricas clínicas (Fase 5.2).
"""

import unittest
from src.protocolo_metricas_clinicas import EvaluadorMetricasClinicas


class TestEvaluadorMetricasClinicas(unittest.TestCase):
    """Casos de prueba para precisión, recall, mAP@0.5, error relativo y FPS."""

    def test_calculo_iou(self) -> None:
        """Verifica el cálculo de IoU entre dos cajas."""
        evaluador = EvaluadorMetricasClinicas(umbral_iou=0.5)
        
        caja1 = (0, 0, 10, 10)
        caja2 = (0, 0, 10, 10)  # Solapamiento total -> IoU 1.0
        self.assertAlmostEqual(evaluador.calcular_iou(caja1, caja2), 1.0)

        caja3 = (20, 20, 30, 30)  # Sin solapamiento -> IoU 0.0
        self.assertAlmostEqual(evaluador.calcular_iou(caja1, caja3), 0.0)

    def test_evaluar_detecciones(self) -> None:
        """Verifica el cálculo de precisión, recall y mAP@0.5."""
        evaluador = EvaluadorMetricasClinicas(umbral_iou=0.5)
        
        gt = [(0, 0, 10, 10), (20, 20, 30, 30)]
        preds = [(0, 0, 10, 10), (20, 20, 30, 30)]  # Dos aciertos exactos (IoU 1.0)

        metricas = evaluador.evaluar_detecciones(preds, gt)
        self.assertIn("precision", metricas)
        self.assertIn("recall", metricas)
        self.assertIn("f1", metricas)
        self.assertIn("map50", metricas)
        self.assertEqual(metricas["precision"], 1.0)
        self.assertEqual(metricas["recall"], 1.0)

    def test_error_relativo_conteo(self) -> None:
        """Verifica el cálculo del error relativo de conteo."""
        evaluador = EvaluadorMetricasClinicas()
        
        error = evaluador.calcular_error_relativo_conteo(105, 100)
        self.assertAlmostEqual(error, 5.0)  # 5% de error

        error_cero = evaluador.calcular_error_relativo_conteo(0, 0)
        self.assertEqual(error_cero, 0.0)

    def test_rendimiento_fps(self) -> None:
        """Verifica el cálculo de FPS sostenidos."""
        evaluador = EvaluadorMetricasClinicas()
        
        fps = evaluador.evaluar_rendimiento_fps(2.0, 60)
        self.assertEqual(fps, 30.0)


if __name__ == "__main__":
    unittest.main()
