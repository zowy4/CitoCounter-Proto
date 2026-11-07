"""
src/captura_video.py - Módulo de captura de video en tiempo real para cámaras de microscopio (USB, C-mount, integrada).

Permite conectar con cámaras mediante OpenCV (cv2.VideoCapture), seleccionar dispositivo,
ajustar exposición, ganancia y resolución, y transmitir frames en tiempo real al pipeline de CitoCounter.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple, Dict, Any
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class CapturaVideoMicroscopio:
    """Controlador de captura de video en tiempo real desde cámaras de microscopio (USB / C-mount / Integrada)."""

    def __init__(self, indice_camara: int = 0) -> None:
        self.indice_camara = indice_camara
        self.cap: Optional[cv2.VideoCapture] = None
        self.ancho = 1280
        self.alto = 720
        self.fps = 30
        self.exposicion = -1.0
        self.ganancia = -1.0
        self.conectada = False

    def conectar(self, indice: Optional[int] = None) -> bool:
        """
        Conecta con la cámara de microscopio especificada.

        :param indice: Índice de la cámara (por defecto 0 o el configurado).
        :type indice: int, optional
        :return: True si la conexión fue exitosa, False en caso contrario.
        :rtype: bool
        """
        if indice is not None:
            self.indice_camara = indice

        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

        # Intentar DirectShow en Windows o estándar en Linux/macOS
        # cv2.CAP_ANY por defecto
        self.cap = cv2.VideoCapture(self.indice_camara, cv2.CAP_ANY)

        if not self.cap.isOpened():
            logger.error(f"No se pudo abrir la cámara con índice {self.indice_camara}")
            self.conectada = False
            return False

        # Configurar resolución predeterminada (HD o máxima soportada)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.ancho)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.alto)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        self.conectada = True
        logger.info(f"Cámara {self.indice_camara} conectada exitosamente.")
        return True

    def desconectar(self) -> None:
        """Libera los recursos de la cámara."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.conectada = False
        logger.info("Cámara desconectada.")

    def ajustar_propiedades(self, exposicion: Optional[float] = None, ganancia: Optional[float] = None, ancho: Optional[int] = None, alto: Optional[int] = None) -> None:
        """
        Ajusta parámetros de exposición, ganancia y resolución en tiempo real.

        :param exposicion: Valor de exposición (si la cámara lo soporta).
        :type exposicion: float, optional
        :param ganancia: Valor de ganancia (si la cámara lo soporta).
        :type ganancia: float, optional
        :param ancho: Ancho de frame.
        :type ancho: int, optional
        :param alto: Alto de frame.
        :type alto: int, optional
        """
        if self.cap is None or not self.cap.isOpened():
            return

        if ancho is not None and alto is not None:
            self.ancho = ancho
            self.alto = alto
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.ancho)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.alto)

        if exposicion is not None:
            self.exposicion = exposicion
            # Algunas cámaras requieren desactivar auto-exposición primero
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) # Manual mode en DirectShow
            self.cap.set(cv2.CAP_PROP_EXPOSURE, self.exposicion)

        if ganancia is not None:
            self.ganancia = ganancia
            self.cap.set(cv2.CAP_PROP_GAIN, self.ganancia)

    def leer_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Captura un frame actual desde la cámara de microscopio.

        :return: Tupla (exito, frame_bgr)
        :rtype: tuple[bool, numpy.ndarray | None]
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False, None

        return True, frame

    def obtener_estado(self) -> Dict[str, Any]:
        """
        Retorna el estado y propiedades actuales de la cámara.

        :return: Diccionario con estado, resolución, fps, exposición y ganancia.
        :rtype: dict
        """
        if self.cap is None or not self.cap.isOpened():
            return {"conectada": False}

        return {
            "conectada": True,
            "indice": self.indice_camara,
            "ancho": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "alto": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "exposicion": self.cap.get(cv2.CAP_PROP_EXPOSURE),
            "ganancia": self.cap.get(cv2.CAP_PROP_GAIN),
        }
