"""
Pruebas unitarias para el adaptador segmentador_dl.py (CITO-95).
Cubre casos edge: imagen vacía, sin detecciones y validación de tamaño <= 64 KiB (OWASP/STRIDE).
"""

import unittest
import csv
import pathlib
import numpy as np

from src.segmentador_dl import (
    analizar_nucleos_dl,
    validar_tamano_imagen,
    convertir_a_8bit,
)


class SegmentadorDLTests(unittest.TestCase):
    def test_validar_tamano_imagen_valido(self):
        # Imagen pequeña de 100x100 uint8 (10 KB) -> OK
        img = np.zeros((100, 100), dtype=np.uint8)
        self.assertLessEqual(img.nbytes, 65536)
        validar_tamano_imagen(img)  # No debe lanzar excepción

    def test_validar_tamano_imagen_excede_64kib(self):
        # Imagen grande que excede 64 KiB -> Debe lanzar ValueError por OWASP/STRIDE
        img = np.zeros((300, 300), dtype=np.uint8)  # 90 KB
        self.assertGreater(img.nbytes, 65536)
        with self.assertRaises(ValueError):
            validar_tamano_imagen(img)

    def test_convertir_a_8bit(self):
        img_float = np.array([[0.0, 1.0], [0.5, 0.8]], dtype=np.float32)
        res = convertir_a_8bit(img_float)
        self.assertEqual(res.dtype, np.uint8)
        self.assertEqual(res.shape, (2, 2))

    def test_analizar_nucleos_dl_imagen_vacia(self):
        # Imagen de 50x50 ceros (2.5 KB)
        img = np.zeros((50, 50), dtype=np.uint8)
        resultado = analizar_nucleos_dl(img)
        self.assertIn("contornos", resultado)
        self.assertIn("areas", resultado)
        self.assertIn("total_celulas", resultado)
        self.assertEqual(resultado["total_celulas"], 0)

    def test_segmentador_dl_conectividad(self):
        """Verifica que el adaptador DL se importa y ejecuta sin errores."""
        img = np.ones((100, 100), dtype=np.uint8) * 200  # Imagen con relieve
        resultado = analizar_nucleos_dl(img)
        self.assertIsInstance(resultado, dict)
        self.assertIn("total_celulas", resultado)
        self.assertIn("reglas", resultado)


    class TestCellposeRegresion(unittest.TestCase):
        """
        Test de regresión para verificar que Cellpose mantiene F1 >= 0.90.
        Requiere el archivo data/results/CITO-95-cellpose-zeroshot.csv generado
        por la evaluación en CITO-96.
        """

        def test_cellpose_f1_metas(self):
            """Verifica que F1 promedio >= 0.90 en test set Herlev (CITO-96)."""
            results_path = pathlib.Path(
                "data/results/CITO-95-cellpose-zeroshot.csv"
            )
            if not results_path.exists():
                self.skipTest("Archivo de resultados de Cellpose no encontrado")

            with results_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                # Solo incluir filas con IDs numéricos (34 imágenes)
                data_rows = [r for r in reader if r.get("image_id") and r["image_id"].isdigit()]

            if not data_rows:
                self.skipTest("No hay datos de resultados disponibles")

            tp_total = sum(int(r["tp"]) for r in data_rows)
            fp_total = sum(int(r["fp"]) for r in data_rows)
            fn_total = sum(int(r["fn"]) for r in data_rows)

            precision = tp_total / (tp_total + fp_total) if (tp_total + fp_total) > 0 else 0
            recall = tp_total / (tp_total + fn_total) if (tp_total + fn_total) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            # Métricas requeridas para CITO-95
            self.assertGreaterEqual(
                f1,
                0.90,
                f"F1-Score {f1:.4f} no alcanza la meta de 0.90 (Cellpose debe mantenerse >= 90%)",
            )
            self.assertGreaterEqual(
                precision,
                0.89,
                f"Precision {precision:.4f} no alcanza 0.89",
            )
            self.assertGreaterEqual(
                recall,
                0.93,
                f"Recall {recall:.4f} no alcanza 0.93",
            )


if __name__ == "__main__":
    unittest.main()
