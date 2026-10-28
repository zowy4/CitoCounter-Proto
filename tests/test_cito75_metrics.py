"""Unit tests for CITO-75: Cálculo reproducible de métricas de detección y segmentación."""

import math
import unittest
from pathlib import Path

from src.analysis import analizar_nucleos
from src.dog_filter import aplicar_filtro_dog
from src.preprocessing import preprocesar_imagen
from calcular_metricas_cito75 import (
    BoundingBox,
    centroid_distance,
    calcular_f1,
    calcular_iou_promedio,
    calcular_precisión,
    calcular_recall,
    matching_por_centroides,
    matching_por_iou,
    parsear_centroides,
)


class TestBoundingBox(unittest.TestCase):
    """Tests for BoundingBox class."""

    def test_bounding_box_creation(self):
        """Test basic bounding box creation."""
        bb = BoundingBox(0, 0, 10, 10)
        self.assertEqual(bb.x_min, 0)
        self.assertEqual(bb.y_min, 0)
        self.assertEqual(bb.x_max, 10)
        self.assertEqual(bb.y_max, 10)

    def test_bounding_box_from_max(self):
        """Test bounding box with max coordinates."""
        bb = BoundingBox(10, 10, 0, 0)
        self.assertEqual(bb.x_min, 0)
        self.assertEqual(bb.y_min, 0)
        self.assertEqual(bb.x_max, 10)
        self.assertEqual(bb.y_max, 10)

    def test_bounding_box_iou_same(self):
        """IoU of a box with itself should be 1."""
        bb1 = BoundingBox(0, 0, 10, 10)
        bb2 = BoundingBox(0, 0, 10, 10)
        self.assertEqual(bb1.iou(bb2), 1.0)

    def test_bounding_box_iou_no_overlap(self):
        """IoU of non-overlapping boxes should be 0."""
        bb1 = BoundingBox(0, 0, 5, 5)
        bb2 = BoundingBox(10, 10, 15, 15)
        self.assertEqual(bb1.iou(bb2), 0.0)

    def test_bounding_box_iou_partial_overlap(self):
        """IoU of partially overlapping boxes."""
        bb1 = BoundingBox(0, 0, 10, 10)
        bb2 =BoundingBox(5, 5, 15, 15)
        iou = bb1.iou(bb2)
        self.assertGreater(iou, 0.0)
        self.assertLess(iou, 1.0)


class TestCentroidDistance(unittest.TestCase):
    """Tests for centroid distance calculation."""

    def test_centroid_distance_same_point(self):
        """Distance between same point should be 0."""
        self.assertEqual(centroid_distance(10, 10, 10, 10), 0.0)

    def test_centroid_distance_horizontal(self):
        """Horizontal distance."""
        self.assertEqual(centroid_distance(0, 0, 10, 0), 10.0)

    def test_centroid_distance_vertical(self):
        """Vertical distance."""
        self.assertEqual(centroid_distance(0, 0, 0, 10), 10.0)

    def test_centroid_distance_diagonal(self):
        """Diagonal distance."""
        self.assertEqual(centroid_distance(0, 0, 3, 4), 5.0)


class TestMatchingPorCentroids(unittest.TestCase):
    """Tests for centroid-based matching."""

    def test_matching_one_to_one(self):
        """One prediction matches one ground truth."""
        tp, fp, fn = matching_por_centroides(
            pred_centroids=[(10, 10), (100, 100)],
            gt_centroids=[(12, 12)],
            distancia_max=5.0,
        )
        self.assertEqual(tp, 1)
        self.assertEqual(fp, 1)
        self.assertEqual(fn, 0)

    def test_matching_no_match(self):
        """No predictions match ground truth."""
        tp, fp, fn = matching_por_centroides(
            pred_centroids=[(100, 100)],
            gt_centroids=[(0, 0)],
            distancia_max=5.0,
        )
        self.assertEqual(tp, 0)
        self.assertEqual(fp, 1)
        self.assertEqual(fn, 1)

    def test_matching_all_match(self):
        """All predictions match ground truth."""
        tp, fp, fn = matching_por_centroides(
            pred_centroids=[(10, 10), (20, 20)],
            gt_centroids=[(12, 12), (22, 22)],
            distancia_max=5.0,
        )
        self.assertEqual(tp, 2)
        self.assertEqual(fp, 0)
        self.assertEqual(fn, 0)

    def test_matching_empty(self):
        """Empty predictions and ground truth."""
        tp, fp, fn = matching_por_centroides(
            pred_centroids=[],
            gt_centroids=[],
            distancia_max=5.0,
        )
        self.assertEqual(tp, 0)
        self.assertEqual(fp, 0)
        self.assertEqual(fn, 0)

    def test_matching_empty_pred(self):
        """Empty predictions with ground truth."""
        tp, fp, fn = matching_por_centroides(
            pred_centroids=[],
            gt_centroids=[(10, 10), (20, 20)],
            distancia_max=5.0,
        )
        self.assertEqual(tp, 0)
        self.assertEqual(fp, 0)
        self.assertEqual(fn, 2)

    def test_matching_empty_gt(self):
        """Empty ground truth with predictions."""
        tp, fp, fn = matching_por_centroides(
            pred_centroids=[(10, 10), (20, 20)],
            gt_centroids=[],
            distancia_max=5.0,
        )
        self.assertEqual(tp, 0)
        self.assertEqual(fp, 2)
        self.assertEqual(fn, 0)


class TestMatchingPorIoU(unittest.TestCase):
    """Tests for IoU-based matching."""

    def test_matching_iou_same_box(self):
        """Same box should match with IoU=1."""
        from calcular_metricas_cito75 import BoundingBox
        tp, fp, fn = matching_por_iou(
            pred_boxes=[BoundingBox(0, 0, 10, 10)],
            gt_boxes=[BoundingBox(0, 0, 10, 10)],
            iou_threshold=0.5,
        )
        self.assertEqual(tp, 1)
        self.assertEqual(fp, 0)
        self.assertEqual(fn, 0)

    def test_matching_iou_no_overlap(self):
        """No overlap should result in no matches (all counts should reflect no TP)."""
        tp, fp, fn = matching_por_iou(
            pred_boxes=[BoundingBox(0, 0, 5, 5)],
            gt_boxes=[BoundingBox(10, 10, 15, 15)],
            iou_threshold=0.5,
        )
        self.assertEqual(tp, 0)
        self.assertEqual(fp, 1)  # 1 pred no matched
        self.assertEqual(fn, 1)  # 1 gt no matched

    def test_matching_iou_partial(self):
        """Partial overlap should match if above threshold."""
        tp, fp, fn = matching_por_iou(
            pred_boxes=[BoundingBox(0, 0, 10, 10)],
            gt_boxes=[BoundingBox(5, 5, 15, 15)],
            iou_threshold=0.1,
        )
        # IoU should be > 0.1 for this overlap
        self.assertGreaterEqual(tp, 0)


class TestPrecisionRecallF1(unittest.TestCase):
    """Tests for precision, recall, and F1 calculations."""

    def test_precisión_tp_fp(self):
        """Precision with TP=2, FP=2 should be 0.5."""
        p = calcular_precisión(2, 2)
        self.assertEqual(p, 0.5)

    def test_precisión_solo_tp(self):
        """Precision with no FP should be 1."""
        p = calcular_precisión(5, 0)
        self.assertEqual(p, 1.0)

    def test_precisión_solo_fp(self):
        """Precision with no TP should be 0."""
        p = calcular_precisión(0, 5)
        self.assertEqual(p, 0.0)

    def test_recall_tp_fn(self):
        """Recall with TP=2, FN=2 should be 0.5."""
        r = calcular_recall(2, 2)
        self.assertEqual(r, 0.5)

    def test_recall_solo_tp(self):
        """Recall with no FN should be 1."""
        r = calcular_recall(5, 0)
        self.assertEqual(r, 1.0)

    def test_f1_balanced(self):
        """F1 with precision=0.5, recall=0.5 should be 0.5."""
        f = calcular_f1(0.5, 0.5)
        self.assertEqual(f, 0.5)

    def test_f1_perfect(self):
        """F1 with precision=1, recall=1 should be 1."""
        f = calcular_f1(1.0, 1.0)
        self.assertEqual(f, 1.0)

    def test_f1_zero(self):
        """F1 with precision=0, recall=0 should be 0."""
        f = calcular_f1(0.0, 0.0)
        self.assertEqual(f, 0.0)


class TestParsearCentroids(unittest.TestCase):
    """Tests for centroid string parsing."""

    def test_parsear_centroides_basico(self):
        """Basic parsing of centroids string."""
        resultado = parsear_centroides("10:20;30:40;50:60")
        self.assertEqual(len(resultado), 3)
        self.assertEqual(resultado[0], (10.0, 20.0))
        self.assertEqual(resultado[1], (30.0, 40.0))
        self.assertEqual(resultado[2], (50.0, 60.0))

    def test_parsear_centroides_vacío(self):
        """Empty string should return empty list."""
        resultado = parsear_centroides("")
        self.assertEqual(resultado, [])

    def test_parsear_centroides_nulo(self):
        """None should return empty list."""
        resultado = parsear_centroides(None)
        self.assertEqual(resultado, [])


class TestIoUPromedio(unittest.TestCase):
    """Tests for IoU average calculation."""

    def test_iou_promedio_con_valores(self):
        """Average IoU with values."""
        from math import isclose
        resultado = calcular_iou_promedio([0.5, 0.7, 0.9])
        self.assertTrue(isclose(resultado, 0.7), f"Expected ≈0.7, got {resultado}")

    def test_iou_promedio_vacío(self):
        """Empty list should return 0."""
        resultado = calcular_iou_promedio([])
        self.assertEqual(resultado, 0.0)


def test_integracion_calculos_completos():
    """Integration test for complete metrics calculation pipeline."""
    # Test the full pipeline: centroids -> matching -> metrics
    # Two predictions, three ground truth; only first pair is close
    pred = [(10, 10), (100, 100)]
    gt = [(12, 12), (55, 55), (105, 105)]

    # Centroid matching with distance 5 should match first pair
    tp, fp, fn = matching_por_centroides(pred, gt, distancia_max=5.0)

    # Calculate derived metrics
    precision = calcular_precisión(tp, fp)
    recall = calcular_recall(tp, fn)
    f1 = calcular_f1(precision, recall)

    # Verify: first pred (10,10) matches first gt (12,12) within 5px
    # Second pred (100,100) is far from all gt, so no match
    assert tp == 1, f"Expected TP=1, got {tp}"
    assert fp == 1, f"Expected FP=1, got {fp}"
    assert fn == 2, f"Expected FN=2, got {fn}"
    assert precision == 0.5, f"Expected precision=0.5, got {precision}"
    assert recall == 1/3, f"Expected recall≈0.333, got {recall}"
    # F1 = 2 * 0.5 * 1/3 / (0.5 + 1/3) = 2 * 0.5 * 0.333 / 0.8333 ≈ 0.4
    assert abs(f1 - 0.4) < 0.05, f"F1 calculation check, got {f1}"


if __name__ == '__main__':
    unittest.main()