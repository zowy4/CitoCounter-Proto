"""Regresiones para los casos especiales documentados en CITO-86."""

import unittest

import cv2
import numpy as np

from src.analysis import crear_mascara_borde, watershed_separar_nucleos
from src.preprocessing import mejorar_contraste, reducir_ruido, verificar_calidad_imagen


class CasosEspecialesCito86Tests(unittest.TestCase):
    """Verifica mitigaciones para superposición, artefactos e iluminación."""

    def test_watershed_separa_nucleos_en_contacto(self):
        imagen = np.zeros((160, 160), dtype=np.uint8)
        cv2.circle(imagen, (65, 80), 30, 255, -1)
        cv2.circle(imagen, (95, 80), 30, 255, -1)

        contornos, areas = watershed_separar_nucleos(
            imagen,
            usar_picos_locales=True,
        )

        self.assertEqual(len(contornos), 2)
        self.assertEqual(len(areas), 2)
        self.assertTrue(all(area > 0 for area in areas))

    def test_contraste_automatico_mitiga_iluminacion_de_bajo_contraste(self):
        imagen = np.tile(np.arange(100, 110, dtype=np.uint8), (100, 10))

        mejorada, metodo, contraste_original, contraste_mejorado = mejorar_contraste(
            imagen,
            metodo="auto",
        )

        self.assertEqual(metodo, "clahe-suave")
        self.assertEqual(mejorada.shape, imagen.shape)
        self.assertEqual(mejorada.dtype, np.uint8)
        self.assertGreater(contraste_mejorado, contraste_original)

    def test_filtro_bilateral_reduce_artefactos_de_alta_frecuencia(self):
        generador = np.random.default_rng(42)
        imagen = np.full((128, 128), 120, dtype=np.uint8)
        ruido = generador.integers(-30, 31, size=imagen.shape)
        imagen_ruidosa = np.clip(imagen.astype(np.int16) + ruido, 0, 255).astype(np.uint8)

        filtrada = reducir_ruido(imagen_ruidosa, nivel="medio")

        self.assertEqual(filtrada.dtype, np.uint8)
        self.assertLess(float(np.std(filtrada)), float(np.std(imagen_ruidosa)))

    def test_mascara_borde_descarta_artefactos_de_convolucion(self):
        mascara = crear_mascara_borde((100, 100), ancho_borde=20)

        self.assertEqual(mascara[0, 50], 0)
        self.assertEqual(mascara[50, 0], 0)
        self.assertEqual(mascara[50, 50], 255)

    def test_calidad_advierte_sobre_iluminacion_plana(self):
        calidad = verificar_calidad_imagen(np.full((64, 64), 120, dtype=np.uint8))

        self.assertFalse(calidad["es_aceptable"])
        self.assertTrue(any("Contraste muy bajo" in aviso for aviso in calidad["advertencias"]))


if __name__ == "__main__":
    unittest.main()
