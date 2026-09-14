import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from api_v1 import (
    CitoCounterApiHandler,
    HTTPServer,
    MAX_REQUEST_BODY_BYTES,
    PROJECT_ROOT,
    analyze_from_payload,
    validate_payload,
)


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
        payload = {
            "image_name": img.name,
            "image_dir": "raw",
            "sigma1": 8.0,
            "sigma2": 8.0,
        }
        response, status = analyze_from_payload(payload)
        self.assertEqual(status, 400)
        self.assertIn("sigma2", response["error"]["message"])
        img.unlink(missing_ok=True)

    def test_rechaza_sigmas_no_numericos(self):
        img = self.raw_dir / "api_test_sigma_texto.jpg"
        img.touch()
        response, status = validate_payload({
            "image_name": img.name,
            "sigma1": "no-numero",
            "sigma2": 8.0,
        })
        self.assertEqual(status, 400)
        self.assertIn("numéricos", response["error"]["message"])
        img.unlink(missing_ok=True)

    def test_rechaza_booleano_como_cadena(self):
        img = self.raw_dir / "api_test_booleano.jpg"
        img.touch()
        response, status = validate_payload({
            "image_name": img.name,
            "noise_reduction": "false",
        })
        self.assertEqual(status, 400)
        self.assertIn("noise_reduction", response["error"]["message"])
        img.unlink(missing_ok=True)

    def test_conserva_booleanos_json(self):
        img = self.raw_dir / "api_test_booleanos_validos.jpg"
        img.touch()
        response, status = validate_payload({
            "image_name": img.name,
            "noise_reduction": True,
            "enhance_contrast": False,
        })
        self.assertEqual(status, 200)
        self.assertTrue(response["reducir_ruido"])
        self.assertFalse(response["mejorar_contraste"])
        img.unlink(missing_ok=True)

    def test_rechaza_ruta_fuera_de_directorio_permitido(self):
        payload = {
            "image_name": "../externa.jpg",
            "image_dir": "raw",
            "sigma1": 7.0,
            "sigma2": 8.0,
        }
        response, status = analyze_from_payload(payload)
        self.assertEqual(status, 400)
        self.assertIn("no debe contener rutas", response["error"]["message"])

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
                "image_name": img_path.name,
                "image_dir": "raw",
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


class ApiV1HttpTests(unittest.TestCase):
    def setUp(self):
        self.server = HTTPServer(("127.0.0.1", 0), CitoCounterApiHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        connection.close()
        return response.status, payload

    def test_health_endpoint(self):
        status, payload = self.request("GET", "/api/v1/health")
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])

    def test_rechaza_json_invalido(self):
        status, payload = self.request(
            "POST",
            "/api/v1/analyze",
            body="{",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(status, 400)
        self.assertIn("JSON inválido", payload["error"]["message"])

    def test_rechaza_cuerpo_excesivo(self):
        status, payload = self.request(
            "POST",
            "/api/v1/analyze",
            body="x" * (MAX_REQUEST_BODY_BYTES + 1),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(status, 413)
        self.assertEqual(payload["error"]["code"], 413)


if __name__ == "__main__":
    unittest.main()
