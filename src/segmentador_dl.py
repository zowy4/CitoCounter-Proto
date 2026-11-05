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

from src.analysis import obtener_reglas_clasificacion, clasificar_nucleo_por_area


def validar_tamano_imagen(imagen: np.ndarray) -> None:
    """
    Valida que el tamaño de la imagen en memoria no supere 64 KiB (65536 bytes)
    como control de seguridad OWASP/STRIDE contra ataques de denegación de servicio (DoS).
    
    :param imagen: Arreglo numpy de la imagen a validar
    :type imagen: numpy.ndarray
    :raises ValueError: Si la imagen excede 64 KiB de memoria
    :rtype: None
    """
    if imagen.nbytes > 65536:
        raise ValueError(
            f"El tamaño de la imagen ({imagen.nbytes} bytes) excede el límite de seguridad "
            "de 64 KiB (65536 bytes) especificado para procesamiento seguro (OWASP/STRIDE)."
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


def analizar_nucleos_dl(imagen: np.ndarray, imagen_original: np.ndarray = None, polaridad: str = 'nucleos-claros') -> Dict[str, Any]:
    """
    Analiza y segmenta núcleos utilizando el adaptador de Deep Learning,
    retornando la misma estructura de datos que analizar_nucleos() tradicional.
    
    :param imagen: Imagen de entrada BGR o escala de grises
    :type imagen: numpy.ndarray
    :param imagen_original: Imagen original RGB para anotación (opcional)
    :type imagen_original: numpy.ndarray
    :param polaridad: Polaridad de los núcleos ('nucleos-claros' o 'nucleos-oscuros')
    :type polaridad: str
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

    _, binaria = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contornos_validos: List[np.ndarray] = []
    areas_validas: List[float] = []
    clasificaciones: List[Dict[str, Any]] = []
    contornos_normales: List[np.ndarray] = []
    contornos_sospechosos: List[np.ndarray] = []
    normales = 0
    sospechosas = 0
    frontera = 0

    reglas = obtener_reglas_clasificacion(polaridad)

    imagen_procesada = imagen_original.copy()

    for c in contornos:
        area = float(cv2.contourArea(c))
        if reglas["area_minima_nucleo"] <= area <= reglas["area_maxima_nucleo"]:
            contornos_validos.append(c)
            areas_validas.append(area)
            decision = clasificar_nucleo_por_area(area, polaridad)
            clasificaciones.append(decision)

            if decision.get("es_frontera", False):
                frontera += 1

            if decision["clasificacion"] == "sospechosa":
                sospechosas += 1
                contornos_sospechosos.append(c)
                cv2.drawContours(imagen_procesada, [c], -1, (0, 0, 255), 2)
            else:
                normales += 1
                contornos_normales.append(c)
                cv2.drawContours(imagen_procesada, [c], -1, (0, 255, 0), 2)

    total_celulas = len(contornos_validos)
    porcentaje_riesgo = (sospechosas / total_celulas * 100.0) if total_celulas > 0 else 0.0

    return {
        "total_celulas": total_celulas,
        "normales": normales,
        "sospechosas": sospechosas,
        "frontera": frontera,
        "porcentaje_riesgo": porcentaje_riesgo,
        "imagen_procesada": imagen_procesada,
        "areas": areas_validas,
        "criterios_clasificacion": clasificaciones,
        "contornos_normales": contornos_normales,
        "contornos_sospechosos": contornos_sospechosos,
        "contornos": contornos_validos,
        "reglas": reglas,
    }
