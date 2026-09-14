import tempfile
import unittest
from pathlib import Path

from validar_metricas_cito23 import obtener_etiquetas_faltantes


class ValidarMetricasCito23Tests(unittest.TestCase):
    def test_informa_etiquetas_faltantes_para_las_imagenes_solicitadas(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            labels_dir = Path(tmp_dir)
            (labels_dir / 'existente.txt').write_text('', encoding='utf-8')
            faltantes = obtener_etiquetas_faltantes(
                ['MUESTRA_001.jpg', 'MUESTRA_002.jpg'],
                labels_dir,
                {
                    'MUESTRA_001.jpg': 'existente.bmp',
                    'MUESTRA_002.jpg': 'faltante.bmp',
                },
            )

        self.assertEqual(faltantes, [
            ('MUESTRA_002.jpg', labels_dir / 'faltante.txt'),
        ])


if __name__ == '__main__':
    unittest.main()