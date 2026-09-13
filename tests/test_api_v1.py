import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from api_v1 import PROJECT_ROOT, analyze_from_payload


class ApiV1Tests(unittest.TestCase):
    def setUp(self):
        self.raw_dir = PROJECT_ROOT / "data" / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def test_rechaza_payload_sin_image_path(self):
        payload = {"sigma1": 7.0, "sigma2": 8.0}
        response, status = analyze_from_payload(payload)
        self.assertEqual(status, 400)
        self.assertFalse(response["ok"])

    def test_rechaza_sigmas_invalidos(self):
        img = self.raw_dir / "api_test_sigmas.jpg"
        img.touch()
        payload = {"image_path": str(img), "sigma1": 8.0, "sigma2": 8.0}
        response, status = analyze_from_payload(payload)
        self.assertEqual(status, 400)
        self.assertIn("sigma2", response["error"]["message"])
        img.unlink(missing_ok=True)

    def test_rechaza_ruta_fuera_de_directorio_permitido(self):
        with tempfile.TemporaryDirectory() as d:
            img = Path(d) / "externa.jpg"
            img.touch()
            payload = {"image_path": str(img), "sigma1": 7.0, "sigma2": 8.0}
            response, status = analyze_from_payload(payload)
            self.assertEqual(status, 400)
            self.assertIn("Ruta no permitida", response["error"]["message"])

    @patch("api_v1.analizar_nucleos")
    @patch("api_v1.aplicar_filtro_dog")
    @patch("api_v1.preprocesar_imagen")
    def test_flujo_valido_entrega_resultado(
        self, mock_preprocesar, mock_dog, mock_analizar
    ):
        with tempfile.TemporaryDirectory() as d:
            img_path = self.raw_dir / "api_test_muestra.jpg"
            img_path.touch()
            mock_preprocesar.return_value = (
                np.zeros((10, 10), dtype=np.uint8),
                np.zeros((10, 10, 3), dtype=np.uint8),
            )
            mock_dog.return_value = np.zeros((10, 10), dtype=np.uint8)
            mock_analizar.return_value = {
                "total_celulas": 10,
                "normales": 7,
                "sospechosas": 3,
                "frontera": 2,
                "porcentaje_riesgo": 30.0,
            }

            payload = {
                "image_path": str(img_path),
                "sigma1": 7.0,
                "sigma2": 8.0,
                "noise_reduction": True,
                "enhance_contrast": True,
            }
            response, status = analyze_from_payload(payload)

            self.assertEqual(status, 200)
            self.assertTrue(response["ok"])
            self.assertEqual(response["result"]["total_cells"], 10)
            self.assertEqual(response["result"]["suspicious_cells"], 3)
            self.assertEqual(response["result"]["borderline_cells"], 2)
            img_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
