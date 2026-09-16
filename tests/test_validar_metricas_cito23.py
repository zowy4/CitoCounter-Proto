import tempfile
import unittest
from pathlib import Path

from validar_metricas_cito23 import (
    BoundingBox,
    MetricsCalculator,
    obtener_etiquetas_faltantes,
)


class ValidarMetricasCito23Tests(unittest.TestCase):
    def test_informa_etiquetas_faltantes_para_las_imagenes_solicitadas(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            labels_dir = Path(tmp_dir)
            (labels_dir / 'existente.txt').write_text('', encoding='utf-8')
            faltantes = obtener_etiquetas_faltantes(
                ['MUESTRA_001.jpg', 'MUESTRA_002.jpg'],
                labels_dir,
                {
                    'MUESTRA_001.jpg': 'existente.bmp',
                    'MUESTRA_002.jpg': 'faltante.bmp',
                },
            )

        self.assertEqual(faltantes, [
            ('MUESTRA_002.jpg', labels_dir / 'faltante.txt'),
        ])


class BoundingBoxTests(unittest.TestCase):
    """Conversión de formatos e IoU con valores calculados a mano."""

    def test_from_yolo_convierte_a_coordenadas_absolutas(self):
        caja = BoundingBox.from_yolo(cx=0.5, cy=0.5, w=0.2, h=0.2,
                                     img_width=100, img_height=100)
        self.assertAlmostEqual(caja.x_min, 40.0)
        self.assertAlmostEqual(caja.y_min, 40.0)
        self.assertAlmostEqual(caja.x_max, 60.0)
        self.assertAlmostEqual(caja.y_max, 60.0)
        self.assertAlmostEqual(caja.area, 400.0)

    def test_from_contour_area_crea_caja_cuadrada(self):
        caja = BoundingBox.from_contour_area(x_center=50.0, y_center=50.0, area=100.0)
        self.assertAlmostEqual(caja.x_min, 45.0)
        self.assertAlmostEqual(caja.y_min, 45.0)
        self.assertAlmostEqual(caja.x_max, 55.0)
        self.assertAlmostEqual(caja.y_max, 55.0)
        self.assertAlmostEqual(caja.area, 100.0)

    def test_iou_identica_es_1_y_disjunta_es_0(self):
        a = BoundingBox(0, 0, 10, 10)
        self.assertAlmostEqual(a.iou(BoundingBox(0, 0, 10, 10)), 1.0)
        self.assertAlmostEqual(a.iou(BoundingBox(20, 20, 30, 30)), 0.0)
        # IoU con un no-BoundingBox no debe explotar
        self.assertAlmostEqual(a.iou("no soy una caja"), 0.0)


class MetricsCalculatorTests(unittest.TestCase):
    """Métricas TP/FP/FN/P/R/F1/IoU contra verdad conocida (Fase 2.1).

    Valores esperados calculados a mano:
    - d1 idéntica a ref1: IoU = 1.0
    - d2 desplazada 1px respecto a ref2: intersección 19*19=361,
      unión 400+400-361=439 => IoU = 361/439
    - d3 sin solape con ninguna referencia => FP
    """

    def test_metricas_tp_fp_fn_con_valores_calculados(self):
        refs = [
            BoundingBox(10, 10, 30, 30),
            BoundingBox(100, 100, 120, 120),
            BoundingBox(200, 200, 220, 220),
        ]
        dets = [
            BoundingBox(10, 10, 30, 30),      # IoU 1.0 con ref1
            BoundingBox(101, 101, 121, 121),  # IoU 361/439 con ref2
            BoundingBox(300, 300, 320, 320),  # sin solape => FP
        ]

        resultado = MetricsCalculator(iou_threshold=0.5).match_detections(dets, refs)

        self.assertEqual(resultado['tp'], 2)
        self.assertEqual(resultado['fp'], 1)
        self.assertEqual(resultado['fn'], 1)
        self.assertAlmostEqual(resultado['precision'], 2 / 3, places=6)
        self.assertAlmostEqual(resultado['recall'], 2 / 3, places=6)
        self.assertAlmostEqual(resultado['f1'], 2 / 3, places=6)
        self.assertAlmostEqual(resultado['mean_iou'], (1.0 + 361 / 439) / 2, places=6)
        self.assertEqual(resultado['unmatched_dets'], [2])
        self.assertEqual(resultado['unmatched_refs'], [2])

    def test_emparejamiento_greedy_elige_mejor_iou_y_no_repite_referencias(self):
        refs = [
            BoundingBox(0, 0, 10, 10),    # r1
            BoundingBox(8, 0, 18, 10),    # r2
        ]
        dets = [
            BoundingBox(5, 0, 15, 10),    # IoU(r1)=1/3 (<0.5), IoU(r2)=7/13 (>0.5) => r2
            BoundingBox(0, 0, 10, 10),    # IoU(r1)=1.0 => r1 (r2 ya tomada)
        ]

        resultado = MetricsCalculator(iou_threshold=0.5).match_detections(dets, refs)

        self.assertEqual(resultado['tp'], 2)
        self.assertEqual(resultado['fp'], 0)
        self.assertEqual(resultado['fn'], 0)
        self.assertAlmostEqual(resultado['mean_iou'], (7 / 13 + 1.0) / 2, places=6)
        emparejados = {(m['det_idx'], m['ref_idx']) for m in resultado['matches']}
        self.assertEqual(emparejados, {(0, 1), (1, 0)})

    def test_sin_detecciones_todo_es_fn_y_metricas_cero(self):
        refs = [BoundingBox(0, 0, 10, 10)] * 3
        resultado = MetricsCalculator(iou_threshold=0.5).match_detections([], refs)

        self.assertEqual(resultado['tp'], 0)
        self.assertEqual(resultado['fp'], 0)
        self.assertEqual(resultado['fn'], 3)
        self.assertEqual(resultado['precision'], 0.0)
        self.assertEqual(resultado['recall'], 0.0)
        self.assertEqual(resultado['f1'], 0.0)
        self.assertEqual(resultado['mean_iou'], 0.0)

    def test_iou_exactamente_en_umbral_no_cuenta_como_match(self):
        # IoU = 50/100 = 0.5 exacto; el emparejamiento exige estrictamente > umbral
        refs = [BoundingBox(0, 0, 10, 10)]
        dets = [BoundingBox(0, 0, 10, 5)]

        resultado = MetricsCalculator(iou_threshold=0.5).match_detections(dets, refs)

        self.assertEqual(resultado['tp'], 0)
        self.assertEqual(resultado['fp'], 1)
        self.assertEqual(resultado['fn'], 1)


if __name__ == '__main__':
    unittest.main()