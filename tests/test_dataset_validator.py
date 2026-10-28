import tempfile
import unittest
from pathlib import Path

from validar_consistencia_dataset import validar_par_imagenes_etiquetas


class DatasetValidatorTests(unittest.TestCase):
    def test_rechaza_archivo_de_etiqueta_huerfano(self):
        with tempfile.TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            imagenes = raiz / "images"
            etiquetas = raiz / "labels"
            imagenes.mkdir()
            etiquetas.mkdir()
            (etiquetas / "IMG_001.txt").write_text(
                "0 0.5 0.5 0.2 0.2\n",
                encoding="utf-8",
            )

            errores = validar_par_imagenes_etiquetas(imagenes, etiquetas)

            self.assertIn("Etiqueta sin imagen: IMG_001", errores)

    def test_rechaza_etiqueta_yolo_invalida(self):
        with tempfile.TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            imagenes = raiz / "images"
            etiquetas = raiz / "labels"
            imagenes.mkdir()
            etiquetas.mkdir()
            (imagenes / "IMG_001.jpg").touch()
            (etiquetas / "IMG_001.txt").write_text(
                "4 1.2 0.5 0.2 0.2\n",
                encoding="utf-8",
            )

            errores = validar_par_imagenes_etiquetas(imagenes, etiquetas)

            self.assertTrue(any("Clase inválida" in error for error in errores))
            self.assertTrue(any("Coordenada fuera de rango" in error for error in errores))


if __name__ == "__main__":
    unittest.main()