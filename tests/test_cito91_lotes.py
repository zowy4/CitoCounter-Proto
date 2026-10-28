"""Regresiones para el control de lotes CITO-91."""

import tempfile
import unittest
from pathlib import Path

from main import seleccionar_archivos_lote


class LotesCito91Tests(unittest.TestCase):
    def test_limita_y_ordena_archivos_compatibles(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            for nombre in ("z.PNG", "a.jpg", "nota.txt", "b.tif"):
                (ruta / nombre).touch()

            archivos = seleccionar_archivos_lote(ruta, max_imagenes=2)

        self.assertEqual([archivo.name for archivo in archivos], ["a.jpg", "b.tif"])

    def test_rechaza_limite_no_positivo(self):
        with tempfile.TemporaryDirectory() as directorio:
            with self.assertRaises(ValueError):
                seleccionar_archivos_lote(Path(directorio), max_imagenes=0)


if __name__ == "__main__":
    unittest.main()
