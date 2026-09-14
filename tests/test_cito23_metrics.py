import tempfile
import unittest
from pathlib import Path
import csv

import calcular_metricas_cito23 as cito23


class Cito23MetricasTests(unittest.TestCase):
    def test_emparejamiento_espacial_uno_a_uno(self):
        tp, fp, fn = cito23.calcular_tp_fp_fn_por_emparejamiento(
            pred_centroids=[(10, 10), (100, 100), (200, 200)],
            gt_centroids=[(12, 12), (98, 98)],
            distancia_max=5.0,
        )

        self.assertEqual(tp, 2)
        self.assertEqual(fp, 1)
        self.assertEqual(fn, 0)

    def test_evaluar_calidad_sin_true_positives(self):
        estado, recomendacion = cito23.evaluar_calidad_resultados(
            total_tp=0,
            total_fp=39,
            total_fn=42,
            total_imagenes=9,
        )

        self.assertEqual(estado, 'EN CURSO')
        self.assertIn('No hubo verdaderos positivos', recomendacion)

    def test_evaluar_calidad_con_detecciones_validas(self):
        estado, recomendacion = cito23.evaluar_calidad_resultados(
            total_tp=8,
            total_fp=3,
            total_fn=2,
            total_imagenes=5,
        )

        self.assertEqual(estado, 'EN REVISION')
        self.assertIn('Métricas calculadas', recomendacion)

    def test_main_incluye_estado_recomendado_en_resumen(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_csv = tmp_path / 'metricas.csv'
            output_txt = tmp_path / 'resumen.txt'

            input_csv.write_text(
                '\n'.join([
                    'image_id,reference_status,tp,fp,fn,precision,recall,f1,jaccard_deteccion,pred_centroids,gt_centroids,match_distance_px,notes',
                    'MUESTRA_001.jpg,manual_review_done,0,0,0,,,,,10:10;100:100,12:12,5,',
                ]) + '\n',
                encoding='utf-8',
            )

            original_input = cito23.INPUT_PATH
            original_output = cito23.OUTPUT_PATH
            try:
                cito23.INPUT_PATH = input_csv
                cito23.OUTPUT_PATH = output_txt
                cito23.main(match_distance=5.0)
            finally:
                cito23.INPUT_PATH = original_input
                cito23.OUTPUT_PATH = original_output

            contenido = output_txt.read_text(encoding='utf-8')
            self.assertIn('Estado recomendado: EN REVISION', contenido)
            self.assertIn('Recomendación: Métricas calculadas con detecciones válidas', contenido)
            self.assertIn('origen=spatial_match dist=5.0px', contenido)
            self.assertIn('Jaccard de deteccion: 0.5000', contenido)


if __name__ == '__main__':
    unittest.main()
