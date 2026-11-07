"""
test_captura_video.py - Pruebas unitarias para la captura de video en tiempo real de microscopio (CITO-Fase 1).
"""

import unittest
import numpy as np
from src.captura_video import CapturaVideoMicroscopio


class TestCapturaVideoMicroscopio(unittest.TestCase):
    """Pruebas para CapturaVideoMicroscopio."""

    def test_inicializacion(self) -> None:
        """Verifica que el controlador se inicialice correctamente."""
        cam = CapturaVideoMicroscopio(indice_camara=0)
        self.assertEqual(cam.indice_camara, 0)
        self.assertFalse(cam.conectada)
        estado = cam.obtener_estado()
        self.assertFalse(estado["conectada"])

    def test_mock_frame_handling(self) -> None:
        """Verifica comportamiento cuando la cámara no está conectada."""
        cam = CapturaVideoMicroscopio(indice_camara=999)
        exito, frame = cam.leer_frame()
        self.assertFalse(exito)
        self.assertIsNone(frame)


if __name__ == "__main__":
    unittest.main()
