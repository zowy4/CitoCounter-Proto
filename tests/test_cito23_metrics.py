import tempfile
import unittest
from pathlib import Path

import calcular_metricas_cito23 as cito23


class Cito23MetricasTests(unittest.TestCase):
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
                    'image_id,reference_status,tp,fp,fn,precision,recall,f1,IoU,notes',
                    'MUESTRA_001.jpg,manual_review_done,0,2,1,,,,,',
                ]) + '\n',
                encoding='utf-8',
            )

            original_input = cito23.INPUT_PATH
            original_output = cito23.OUTPUT_PATH
            try:
                cito23.INPUT_PATH = input_csv
                cito23.OUTPUT_PATH = output_txt
                cito23.main()
            finally:
                cito23.INPUT_PATH = original_input
                cito23.OUTPUT_PATH = original_output

            contenido = output_txt.read_text(encoding='utf-8')
            self.assertIn('Estado recomendado: EN CURSO', contenido)
            self.assertIn('Recomendación: No hubo verdaderos positivos', contenido)


if __name__ == '__main__':
    unittest.main()
