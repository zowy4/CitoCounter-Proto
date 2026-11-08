"""
src/normalizacion_color.py - Normalización adaptativa de color e iluminación (Fase 3.2).

Implementa balance de blancos automático y normalización de histograma adaptativa
para tolerar variaciones en la tinción de Papanicolaou y tintes de citología cervical.
"""

from typing import Tuple
import numpy as np
import cv2


def balance_blancos_gris_mundial(imagen_bgr: np.ndarray) -> np.ndarray:
    """
    Aplica balance de blancos automático utilizando el método del mundo gris (Gray World Hypothesis).

    Asume que el promedio de los canales R, G y B en una escena equilibrada debe ser neutro (gris).

    :param imagen_bgr: Imagen en formato BGR (H, W, 3).
    :type imagen_bgr: numpy.ndarray
    :return: Imagen BGR con balance de blancos aplicado.
    :rtype: numpy.ndarray
    """
    if imagen_bgr.ndim != 3 or imagen_bgr.shape[2] != 3:
        return imagen_bgr

    img_float = imagen_bgr.astype(np.float32)
    media_b = np.mean(img_float[:, :, 0])
    media_g = np.mean(img_float[:, :, 1])
    media_r = np.mean(img_float[:, :, 2])

    media_global = (media_b + media_g + media_r) / 3.0

    if media_b > 0:
        img_float[:, :, 0] *= (media_global / media_b)
    if media_g > 0:
        img_float[:, :, 1] *= (media_global / media_g)
    if media_r > 0:
        img_float[:, :, 2] *= (media_global / media_r)

    return np.clip(img_float, 0, 255).astype(np.uint8)


def normalizar_iluminacion_papanicolaou(imagen_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Normaliza la iluminación y el color de imágenes teñidas con Papanicolaou.

    Aplica balance de blancos (Gray World) seguido de ecualización adaptativa (CLAHE)
    en el canal de luminosidad (espacio LAB) para compensar variaciones de tinción.

    :param imagen_bgr: Imagen BGR de entrada.
    :type imagen_bgr: numpy.ndarray
    :return: Tupla (imagen BGR normalizada, imagen en escala de grises resultante).
    :rtype: tuple
    """
    # 1. Balance de blancos automático
    bgr_balanceado = balance_blancos_gris_mundial(imagen_bgr)

    # 2. Conversión a espacio LAB para separar luminosidad y color
    lab = cv2.cvtColor(bgr_balanceado, cv2.COLOR_BGR2LAB)
    l_chan, a_chan, b_chan = cv2.split(lab)

    # 3. Aplicar CLAHE en el canal de luminancia L
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l_chan)

    # 4. Recombinar canales LAB y volver a BGR
    lab_unido = cv2.merge((l_clahe, a_chan, b_chan))
    bgr_normalizado = cv2.cvtColor(lab_unido, cv2.COLOR_LAB2BGR)

    # 5. Generar escala de grises final para el pipeline DoG
    gris_final = cv2.cvtColor(bgr_normalizado, cv2.COLOR_BGR2GRAY)

    return bgr_normalizado, gris_final
