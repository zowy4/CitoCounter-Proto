import unittest

import cv2
import numpy as np

from src.dog_filter import _calcular_diferencia_dog, aplicar_filtro_dog


class DogFilterTests(unittest.TestCase):
    def test_diferencia_conserva_valores_negativos(self):
        """Test base: _calcular_diferencia_dog preserva valores negativos en float32."""
        primer_gaussiano = np.array([[0, 10, 20]], dtype=np.uint8)
        segundo_gaussiano = np.array([[10, 10, 10]], dtype=np.uint8)

        diferencia = _calcular_diferencia_dog(
            primer_gaussiano,
            segundo_gaussiano,
        )

        np.testing.assert_array_equal(
            diferencia,
            np.array([[-10, 0, 10]], dtype=np.float32),
        )

    def test_aplicar_filtro_dog_retorna_uint8(self):
        """CITO-42: aplicar_filtro_dog debe retornar uint8 (0-255)."""
        img = np.zeros((100, 100), dtype=np.uint8)
        img[40:60, 40:60] = 255  # White circle on black background
        dog = aplicar_filtro_dog(img, sigma1=7.0, sigma2=8.0)

        # Verificar que el retorno es uint8
        self.assertEqual(dog.dtype, np.uint8)
        # Verificar rango [0, 255]
        self.assertGreaterEqual(dog.min(), 0)
        self.assertLessEqual(dog.max(), 255)
        # Verificar que no es todo cero (a menos que la imagen sea uniforme)
        self.assertGreater(dog.max(), 0)

    def test_aplicar_filtro_dog_imagen_uniforme(self):
        """CITO-42: Imagen uniforme debe producir DoG constante (cero después de normalize)."""
        img = np.full((100, 100), 128, dtype=np.uint8)
        dog = aplicar_filtro_dog(img, sigma1=7.0, sigma2=8.0)

        # Imagen uniforme debería tener DoG cercano a cero después de normalize
        # (puede tener valores muy pequeños por ruido de GaussianBlur)
        self.assertLessEqual(dog.max(), 1)  # Debería ser casi todo cero

    def test_aplicar_filtro_dog_rango_valores(self):
        """CITO-42: Los valores DoG normalizados deben estar en [0, 255]."""
        # Probar con diferentes imágenes y parámetros
        for sigma1, sigma2 in [(1.0, 2.0), (3.0, 5.0), (7.0, 8.0), (10.0, 15.0)]:
            img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
            dog = aplicar_filtro_dog(img, sigma1=sigma1, sigma2=sigma2)

            # Verificar rango
            self.assertGreaterEqual(dog.min(), 0,
                                    f"sigma1={sigma1}, sigma2={sigma2}: min < 0")
            self.assertLessEqual(dog.max(), 255,
                                 f"sigma1={sigma1}, sigma2={sigma2}: max > 255")

    def test_calcular_diferencia_dog_tipo_dato(self):
        """Test base: _calcular_diferencia_dog debe retornar float32."""
        primer_gaussiano = np.array([[0, 10, 20]], dtype=np.uint8)
        segundo_gaussiano = np.array([[10, 10, 10]], dtype=np.uint8)

        diferencia = _calcular_diferencia_dog(
            primer_gaussiano,
            segundo_gaussiano,
        )

        self.assertEqual(diferencia.dtype, np.float32)

    def test_negativos_en_dog_antes_normalizar(self):
        """CITO-42: El DoG sin normalizar puede tener valores negativos."""
        img = np.zeros((100, 100), dtype=np.uint8)
        img[40:60, 40:60] = 255

        # Obtener el DoG antes de que aplicar_filtro_dog lo normalice
        g1 = cv2.GaussianBlur(img, (0, 0), 7.0)
        g2 = cv2.GaussianBlur(img, (0, 0), 8.0)
        dog_float = _calcular_diferencia_dog(g1, g2)

        # Deberían existir valores negativos antes del normalize
        self.assertTrue(np.any(dog_float < 0),
                        "El DoG sin normalizar debería tener valores negativos")


if __name__ == "__main__":
    unittest.main()