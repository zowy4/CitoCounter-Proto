"""
Pruebas unitarias para el módulo de captura de video en tiempo real (CITO-103).
"""

import unittest
from unittest.mock import MagicMock, patch
from src.captura_microscopio import GestorCapturaMicroscopio

class TestGestorCapturaMicroscopio(unittest.TestCase):
    """Casos de prueba para GestorCapturaMicroscopio."""

    @patch('cv2.VideoCapture')
    def test_iniciar_y_liberar_captura(self, mock_videocapture):
        """Verifica el flujo de inicio, lectura y liberación de la cámara."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "fake_frame")
        mock_videocapture.return_value = mock_cap

        gestor = GestorCapturaMicroscopio(fuente_id=0)
        exito = gestor.iniciar_captura()
        self.assertTrue(exito)
        self.assertTrue(gestor.activo)

        ret, frame = gestor.leer_frame()
        self.assertTrue(ret)
        self.assertEqual(frame, "fake_frame")

        gestor.liberar()
        self.assertFalse(gestor.activo)

if __name__ == "__main__":
    unittest.main()
