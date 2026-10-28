"""Pruebas para generar_groundtruth_sintetico.py (Fase 2.1, CITO-23)."""

import csv
import math
import tempfile
import unittest
from pathlib import Path

from generar_groundtruth_sintetico import (
    AREA_MAXIMA_NUCLEO,
    AREA_MINIMA_NUCLEO,
    CLASE_NORMAL,
    CLASE_SOSPECHOSA,
    UMBRAL_SOSPECHOSO,
    generar_dataset,
)


class GenerarGroundtruthSinteticoTests(unittest.TestCase):
    def _leer_indice(self, ruta_indice):
        with ruta_indice.open('r', encoding='utf-8', newline='') as f:
            return list(csv.DictReader(f))

    def _leer_etiquetas(self, ruta_etiquetas):
        lineas = []
        for archivo in sorted(ruta_etiquetas.glob('*.txt')):
            for linea in archivo.read_text(encoding='utf-8').splitlines():
                if linea.strip():
                    lineas.append((archivo.name, linea.split()))
        return lineas

    def test_genera_conjuntos_separados_e_indice(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            salida = Path(tmp_dir) / 'sintetico'
            indice = generar_dataset(salida, n_calibracion=2, n_evaluacion=3,
                                     semilla=42, ancho=256, alto=256)

            self.assertTrue(indice.is_file())
            self.assertEqual(len(list((salida / 'calibracion' / 'images').glob('*.png'))), 2)
            self.assertEqual(len(list((salida / 'calibracion' / 'labels').glob('*.txt'))), 2)
            self.assertEqual(len(list((salida / 'evaluacion' / 'images').glob('*.png'))), 3)
            self.assertEqual(len(list((salida / 'evaluacion' / 'labels').glob('*.txt'))), 3)

            filas = self._leer_indice(indice)
            self.assertEqual(len(filas), 5)
            self.assertEqual({f['Origen'] for f in filas}, {'calibracion', 'evaluacion'})
            # Numeración disjunta por construcción
            cal = [f['ID_Imagen'] for f in filas if f['Origen'] == 'calibracion']
            ev = [f['ID_Imagen'] for f in filas if f['Origen'] == 'evaluacion']
            self.assertTrue(all(int(n.split('_')[1].split('.')[0]) < 100 for n in cal))
            self.assertTrue(all(int(n.split('_')[1].split('.')[0]) >= 100 for n in ev))
            # Nombre_Original coincide con ID (mapeo directo del validador)
            for fila in filas:
                self.assertEqual(fila['Nombre_Original'], fila['ID_Imagen'])
                self.assertGreaterEqual(int(fila['Nucleos']), 1)

    def test_etiquetas_yolo_validas_y_areas_coherentes_con_reglas(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            salida = Path(tmp_dir) / 'sintetico'
            generar_dataset(salida, n_calibracion=1, n_evaluacion=1,
                            semilla=7, ancho=256, alto=256)

            for origen in ('calibracion', 'evaluacion'):
                etiquetas = self._leer_etiquetas(salida / origen / 'labels')
                self.assertTrue(etiquetas)
                for nombre_archivo, campos in etiquetas:
                    self.assertEqual(len(campos), 5, f"{nombre_archivo}: {campos}")
                    clase = int(campos[0])
                    self.assertIn(clase, (CLASE_NORMAL, CLASE_SOSPECHOSA))
                    valores = [float(v) for v in campos[1:]]
                    for v in valores:
                        self.assertGreaterEqual(v, 0.0)
                        self.assertLessEqual(v, 1.0)

                    # Área reconstruida desde YOLO debe respetar las reglas CITO-24
                    _, cx, cy, w, h = campos
                    rx = float(w) * 256 / 2
                    ry = float(h) * 256 / 2
                    area = math.pi * rx * ry
                    self.assertGreaterEqual(area, AREA_MINIMA_NUCLEO)
                    self.assertLessEqual(area, AREA_MAXIMA_NUCLEO)
                    if clase == CLASE_NORMAL:
                        self.assertLess(area, UMBRAL_SOSPECHOSO)
                    else:
                        self.assertGreaterEqual(area, UMBRAL_SOSPECHOSO)

    def test_misma_semilla_genera_dataset_identico(self):
        with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
            salida_a = Path(tmp_a) / 'sintetico'
            salida_b = Path(tmp_b) / 'sintetico'
            generar_dataset(salida_a, n_calibracion=2, n_evaluacion=2, semilla=123)
            generar_dataset(salida_b, n_calibracion=2, n_evaluacion=2, semilla=123)

            self.assertEqual(self._leer_indice(salida_a / 'dataset_index.csv'),
                             self._leer_indice(salida_b / 'dataset_index.csv'))
            for origen in ('calibracion', 'evaluacion'):
                for archivo in sorted((salida_a / origen / 'labels').glob('*.txt')):
                    gemelo = salida_b / origen / 'labels' / archivo.name
                    self.assertEqual(archivo.read_text(encoding='utf-8'),
                                     gemelo.read_text(encoding='utf-8'))

    def test_polaridades_producen_mismo_gt_geometrico(self):
        """La inversión de intensidad no altera la geometría: el GT YOLO
        (y por tanto la validación de métricas) es idéntico en ambas polaridades."""
        with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
            salida_a = Path(tmp_a) / 'sintetico'
            salida_b = Path(tmp_b) / 'sintetico'
            generar_dataset(salida_a, n_calibracion=1, n_evaluacion=1, semilla=42,
                            polaridad='nucleos-claros')
            generar_dataset(salida_b, n_calibracion=1, n_evaluacion=1, semilla=42,
                            polaridad='nucleos-oscuros')

            self.assertEqual(self._leer_indice(salida_a / 'dataset_index.csv'),
                             self._leer_indice(salida_b / 'dataset_index.csv'))
            for origen in ('calibracion', 'evaluacion'):
                for archivo in sorted((salida_a / origen / 'labels').glob('*.txt')):
                    gemelo = salida_b / origen / 'labels' / archivo.name
                    self.assertEqual(archivo.read_text(encoding='utf-8'),
                                     gemelo.read_text(encoding='utf-8'))

            # La polaridad por defecto debe ser el dominio detectable
            import cv2
            img_claros = cv2.imread(str(salida_a / 'calibracion' / 'images' / 'SINTETICA_001.png'),
                                    cv2.IMREAD_GRAYSCALE)
            img_oscuros = cv2.imread(str(salida_b / 'calibracion' / 'images' / 'SINTETICA_001.png'),
                                     cv2.IMREAD_GRAYSCALE)
            self.assertLess(float(img_claros.mean()), float(img_oscuros.mean()),
                            'nucleos-claros debe ser la imagen invertida (más oscura de media)')


if __name__ == '__main__':
    unittest.main()
