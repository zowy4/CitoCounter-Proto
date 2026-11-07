"""
test_captura_video.py - Tests unitarios para el módulo de captura de video (Fase 1.1).
"""

import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from src.captura_video import CapturaVideo


class TestCapturaVideo(unittest.TestCase):
    """Casos de prueba para el administrador de captura de video."""

    def test_inicializacion(self) -> None:
        """Verifica la correcta inicialización del objeto CapturaVideo."""
        cap_mgr = CapturaVideo(fuente=0)
        self.assertEqual(cap_mgr.fuente, 0)
        self.assertIsNone(cap_mgr.cap)

    @patch("cv2.VideoCapture")
    def test_abrir_y_cerrar(self, mock_videocapture: MagicMock) -> None:
        """Verifica apertura y cierre de la fuente de video."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_videocapture.return_value = mock_cap

        cap_mgr = CapturaVideo(fuente=0)
        self.assertTrue(cap_mgr.abrir())
        self.assertTrue(cap_mgr.cap.isOpened())

        cap_mgr.cerrar()
        self.assertIsNone(cap_mgr.cap)

    def test_modo_sintetico(self) -> None:
        """Verifica la generación y lectura de frames en modo sintético (fallback sin cámara física)."""
        cap_mgr = CapturaVideo(fuente="sintetico")
        self.assertTrue(cap_mgr.abrir())
        self.assertEqual(cap_mgr.cap, "sintetico")

        frame = cap_mgr.leer_frame()
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (720, 1280, 3))

        info = cap_mgr.obtener_info()
        self.assertTrue(info["activo"])
        self.assertIn("sintetico", info["fuente"])

        cap_mgr.cerrar()
        self.assertIsNone(cap_mgr.cap)


if __name__ == "__main__":
    unittest.main()
