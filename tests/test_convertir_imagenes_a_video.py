"""
test_convertir_imagenes_a_video.py - Tests unitarios para la conversión de datasets de imágenes a video.
"""

import unittest
import pathlib
import tempfile
import shutil
import numpy as np
import cv2

from src.convertir_imagenes_a_video import convertir_carpeta_a_video


class TestConvertirImagenesAVideo(unittest.TestCase):
    """Casos de prueba para la conversión de carpetas de imágenes a video."""

    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.img_dir = pathlib.Path(self.test_dir) / "imagenes"
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.out_video = pathlib.Path(self.test_dir) / "videos" / "salida.mp4"

        # Crear algunas imágenes sintéticas de prueba
        for i in range(5):
            img = np.ones((100, 100, 3), dtype=np.uint8) * (i * 40)
            cv2.imwrite(str(self.img_dir / f"img_{i:03d}.png"), img)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_convertir_carpeta_exitosa(self) -> None:
        """Verifica que la conversión de una carpeta con imágenes genere un video válido."""
        exito = convertir_carpeta_a_video(
            carpeta_imagenes=self.img_dir,
            ruta_salida_video=self.out_video,
            fps=2
        )
        self.assertTrue(exito)
        self.assertTrue(self.out_video.exists())
        self.assertGreater(self.out_video.stat().st_size, 0)

    def test_carpeta_inexistente(self) -> None:
        """Verifica manejo correcto cuando la carpeta no existe."""
        exito = convertir_carpeta_a_video(
            carpeta_imagenes="carpeta_falsa_inexistente",
            ruta_salida_video=self.out_video
        )
        self.assertFalse(exito)


if __name__ == "__main__":
    unittest.main()
