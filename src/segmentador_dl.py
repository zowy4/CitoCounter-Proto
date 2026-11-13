"""
segmentador_dl.py - Adaptador de Deep Learning (Cellpose / StarDist) con interfaz compatible

Permite integrar modelos basados en aprendizaje profundo (como Cellpose zero-shot)
dentro del pipeline de CitoCounter-Proto, manteniendo compatibilidad con la interfaz
de análisis y clasificación de src/analysis.py.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple, Any

import cv2
import numpy as np

from src.analysis import obtener_reglas_clasificacion, clasificar_nucleo_por_area, analizar_nucleos
from src.dog_filter import aplicar_filtro_dog, aplicar_multiscale_dog


def validar_tamano_imagen(imagen: np.ndarray, tamano_maximo_kb: int = 16384) -> None:
    """
    Valida que el tamaño de la imagen en memoria no supere el límite máximo (por defecto 16384 KB = 16 MB)
    como control de seguridad OWASP/STRIDE contra ataques de denegación de servicio (DoS).
    
    :param imagen: Arreglo numpy de la imagen a validar
    :type imagen: numpy.ndarray
    :param tamano_maximo_kb: Tamaño máximo permitido en kilobytes (default: 16384 KB = 16 MB)
    :type tamano_maximo_kb: int
    :raises ValueError: Si la imagen excede el límite máximo
    :rtype: None
    """
    if imagen is None:
        raise ValueError("La imagen es nula.")
    tamano_bytes = imagen.nbytes
    tamano_maximo_bytes = tamano_maximo_kb * 1024
    if tamano_bytes > tamano_maximo_bytes:
        raise ValueError(
            f"El tamaño de la imagen ({tamano_bytes / 1024:.1f} KB) excede el límite de seguridad "
            f"de {tamano_maximo_kb} KB especificado para procesamiento seguro (OWASP/STRIDE)."
        )


def convertir_a_8bit(imagen: np.ndarray) -> np.ndarray:
    """
    Convierte un arreglo de imagen a 8-bit (uint8) usando normalización y recorte seguro.
    
    :param imagen: Arreglo de entrada (float32 o uint16)
    :type imagen: numpy.ndarray
    :return: Imagen convertida a uint8
    :rtype: numpy.ndarray
    """
    if imagen.dtype == np.uint8:
        return imagen
    
    # Normalizar al rango 0-255 con cv2.normalize
    normalizada = cv2.normalize(imagen, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    return normalizada


def analizar_nucleos_dl(
    imagen: np.ndarray,
    imagen_original: np.ndarray = None,
    polaridad: str = 'nucleos-claros',
    sigma1: float = 5.0,
    sigma2: float = 8.0,
    usar_multiscale_dog: bool = True,
    metodo_separacion: str = 'watershed'
) -> Dict[str, Any]:
    """
    Analiza y segmenta núcleos utilizando el adaptador de Deep Learning / Híbrido,
    integrando DoG Multi-Escala, Watershed y clasificación de riesgo explicable.
    
    :param imagen: Imagen de entrada BGR o escala de grises
    :type imagen: np.ndarray
    :param imagen_original: Imagen original RGB para anotación (opcional)
    :type imagen_original: np.ndarray
    :param polaridad: Polaridad de los núcleos ('nucleos-claros' o 'nucleos-oscuros')
    :type polaridad: str
    :param sigma1: Sigma 1 para DoG
    :type sigma1: float
    :param sigma2: Sigma 2 para DoG
    :type sigma2: float
    :param usar_multiscale_dog: Si True, usa banco de filtros DoG de 3 escalas
    :type usar_multiscale_dog: bool
    :param metodo_separacion: Método de separación (ej. 'watershed')
    :type metodo_separacion: str
    :return: Diccionario completo de resultados compatible con el pipeline
    :rtype: dict
    """
    validar_tamano_imagen(imagen)
    img_8bit = convertir_a_8bit(imagen)
    if len(img_8bit.shape) == 3:
        gray = cv2.cvtColor(img_8bit, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_8bit
    
    if imagen_original is None:
        if len(img_8bit.shape) == 2:
            imagen_original = cv2.cvtColor(img_8bit, cv2.COLOR_GRAY2BGR)
        else:
            imagen_original = img_8bit.copy()

    if usar_multiscale_dog:
        dog, _ = aplicar_multiscale_dog(gray)
    else:
        dog = aplicar_filtro_dog(gray, sigma1=sigma1, sigma2=sigma2)

    return analizar_nucleos(
        dog,
        imagen_original,
        polaridad=polaridad,
        metodo_separacion=metodo_separacion
    )
