"""
Módulo de Superposición y Visualización en Vivo (Fase 1 / CITO-105 / ACT-34).
Renderiza bounding boxes, centroides y conteo acumulado sobre el stream de video de forma fluida.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any

class VisualizadorOverlays:
    """
    Renderiza anotaciones visuales (bounding boxes, centroides, contadores) sobre imágenes o frames de video.
    """
    @staticmethod
    def renderizar_overlay(
        frame: np.ndarray,
        detecciones: List[Dict[str, Any]],
        conteo_acumulado: int,
        fps: float = 0.0
    ) -> np.ndarray:
        """
        Dibuja los elementos superpuestos sobre el frame de video.

        :param frame: Imagen de entrada (numpy array BGR).
        :type frame: np.ndarray
        :param detecciones: Lista de diccionarios con 'bbox' [ymin, xmin, ymax, xmax] y opcionalmente 'clase'.
        :type detecciones: list
        :param conteo_acumulado: Número total de núcleos detectados.
        :type conteo_acumulado: int
        :param fps: Fotogramas por segundo actuales.
        :type fps: float
        :return: Frame anotado.
        :rtype: np.ndarray
        """
        salida = frame.copy()
        
        # Dibujar bounding boxes y centroides
        for det in detecciones:
            bbox = det.get("bbox")
            if bbox and len(bbox) == 4:
                ymin, xmin, ymax, xmax = map(int, bbox)
                cv2.rectangle(salida, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                
                # Centroide
                cx = (xmin + xmax) // 2
                cy = (ymin + ymax) // 2
                cv2.circle(salida, (cx, cy), 3, (0, 0, 255), -1)

        # Panel superior de información (Conteo y FPS)
        h, w = salida.shape[:2]
        cv2.rectangle(salida, (10, 10), (min(w - 10, 320), 80), (50, 50, 50), -1)
        cv2.putText(salida, f"Conteo Acumulado: {conteo_acumulado}", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(salida, f"FPS: {fps:.1f}", (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        return salida
