"""
Módulo de Captura de Video en Tiempo Real para Microscopio (Fase 1 / CITO-103 / ACT-32).
Gestiona la captura desde cámaras USB y C-mount con control de exposición y ganancia.
"""

import cv2
from typing import Dict, Any, Optional, Tuple

class GestorCapturaMicroscopio:
    """
    Gestor para la captura de frames de video desde cámaras de microscopio (USB o C-mount).
    """
    def __init__(self, fuente_id: int = 0) -> None:
        """:param fuente_id: Índice o ruta de la cámara de captura.
        :type fuente_id: int
        """
        self.fuente_id = fuente_id
        self.cap: Optional[cv2.VideoCapture] = None
        self.activo = False

    def iniciar_captura(self) -> bool:
        """
        Inicia la conexión con el dispositivo de captura de video.

        :return: True si se conectó exitosamente, False en caso contrario.
        :rtype: bool
        """
        try:
            self.cap = cv2.VideoCapture(self.fuente_id)
            if self.cap.isOpened():
                self.activo = True
                return True
        except Exception:
            pass
        return False

    def configurar_parametros(self, exposicion: Optional[float] = None, ganancia: Optional[float] = None) -> None:
        """
        Configura la exposición y ganancia de la cámara si el hardware lo soporta.

        :param exposicion: Valor de exposición.
        :type exposicion: float, optional
        :param ganancia: Valor de ganancia.
        :type ganancia: float, optional
        """
        if self.cap and self.cap.isOpened():
            if exposicion is not None:
                self.cap.set(cv2.CAP_PROP_EXPOSURE, exposicion)
            if ganancia is not None:
                self.cap.set(cv2.CAP_PROP_GAIN, ganancia)

    def leer_frame(self) -> Tuple[bool, Optional[Any]]:
        """
        Captura un frame actual del stream de video.

        :return: Tupla (exito, frame_numpy).
        :rtype: tuple
        """
        if self.cap and self.activo:
            return self.cap.read()
        return False, None

    def liberar(self) -> None:
        """Libera los recursos de captura de video."""
        if self.cap:
            self.cap.release()
            self.activo = False
