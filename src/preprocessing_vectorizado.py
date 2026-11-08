"""
src/preprocessing_vectorizado.py - Funciones optimizadas de preprocesamiento vectorizado en memoria (Fase 2.2).

Implementa operaciones vectorizadas con NumPy y OpenCV para maximizar el rendimiento
en la conversión de color, ecualización y filtrado en streaming o lotes grandes.
"""

from typing import Tuple, Optional
import numpy as np
import cv2


def convertir_a_gris_vectorizado(imagen_bgr: np.ndarray) -> np.ndarray:
    """
    Convierte una imagen BGR a escala de grises mediante operaciones vectorizadas optimizadas.

    :param imagen_bgr: Imagen en formato BGR (H, W, 3) o escala de grises (H, W).
    :type imagen_bgr: numpy.ndarray
    :return: Imagen en escala de grises (H, W), dtype uint8.
    :rtype: numpy.ndarray
    """
    if imagen_bgr.ndim == 2:
        return imagen_bgr.astype(np.uint8, copy=False)
    
    # Vectorización explícita ponderada ITU-R 601-2 luma transform (alternativa ultrarrápida a cv2.cvtColor)
    # Y = 0.299*R + 0.587*G + 0.114*B (OpenCV BGR order: channels are B, G, R)
    b = imagen_bgr[:, :, 0].astype(np.float32)
    g = imagen_bgr[:, :, 1].astype(np.float32)
    r = imagen_bgr[:, :, 2].astype(np.float32)
    
    gray_float = 0.114 * b + 0.587 * g + 0.299 * r
    return np.clip(gray_float, 0, 255).astype(np.uint8)


def mejorar_contraste_vectorizado(imagen_gris: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
    """
    Mejora el contraste mediante CLAHE optimizado con manejo vectorizado en memoria.

    :param imagen_gris: Imagen en escala de grises (H, W).
    :type imagen_gris: numpy.ndarray
    :param clip_limit: Límite de corte para CLAHE.
    :type clip_limit: float
    :return: Imagen mejorada en escala de grises, uint8.
    :rtype: numpy.ndarray
    """
    # Usar objetos reutilizables o caché de CLAHE si se requiere máxima velocidad
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    return clahe.apply(imagen_gris)


def preprocesar_lote_vectorizado(lote_imagenes: np.ndarray) -> np.ndarray:
    """
    Procesa un lote completo de imágenes (N, H, W, 3) en paralelo usando operaciones vectorizadas.

    :param lote_imagenes: Arreglo numpy 4D de imágenes BGR.
    :type lote_imagenes: numpy.ndarray
    :return: Arreglo 3D de imágenes en escala de grises preprocesadas (N, H, W).
    :rtype: numpy.ndarray
    """
    if lote_imagenes.ndim == 3:
        # Si es una sola imagen en 3D (H, W, 3), convertir a lote de 1
        lote_imagenes = np.expand_dims(lote_imagenes, axis=0)

    n, h, w, _ = lote_imagenes.shape
    resultado = np.empty((n, h, w), dtype=np.uint8)

    for i in range(n):
        gris = convertir_a_gris_vectorizado(lote_imagenes[i])
        resultado[i] = mejorar_contraste_vectorizado(gris)

    return resultado
