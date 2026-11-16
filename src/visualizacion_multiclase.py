"""
src/visualizacion_multiclase.py - Visualización Multiclase Codificada por Color (CITO-124 / ACT-46).

Permite renderizar contornos, bounding boxes y etiquetas en imágenes citológicas
según la taxonomía clínica estándar SIPaKMeD de 5 clases con códigos de color específicos.
"""

from __future__ import annotations

from typing import Dict, Any, List, Tuple
import cv2
import numpy as np


# Paleta de colores BGR para cada clase SIPaKMeD
COLORES_SIPAKMED_BGR: Dict[str, Tuple[int, int, int]] = {
    "Superficial-Intermediate": (0, 255, 0),     # Verde (Normal)
    "Parabasal": (255, 128, 0),                 # Azul claro / Celeste (Normal)
    "Metaplastic": (255, 255, 0),               # Cian / Amarillo-Cian (Benigno / Reactivo)
    "Koilocytotic": (0, 165, 255),              # Naranja (LSIL / Bajo riesgo)
    "Dyskeratotic": (0, 0, 255)                 # Rojo (HSIL / Alto riesgo)
}


def validar_tamano_visualizacion(imagen: np.ndarray, tamano_maximo_bytes: int = 65536 * 100) -> None:
    """
    Valida el tamaño de la imagen de entrada según los controles de seguridad OWASP/STRIDE.

    :param imagen: Arreglo numpy de la imagen
    :type imagen: np.ndarray
    :param tamano_maximo_bytes: Límite máximo en bytes
    :type tamano_maximo_bytes: int
    :raises ValueError: Si la imagen excede el tamaño máximo permitido
    """
    if imagen is None:
        raise ValueError("La imagen de entrada es nula.")
    if imagen.nbytes > tamano_maximo_bytes:
        raise ValueError(
            f"Tamaño de imagen excede el límite OWASP/STRIDE ({imagen.nbytes} bytes > {tamano_maximo_bytes} bytes)."
        )


def dibujar_celdas_multiclase(
    imagen: np.ndarray,
    detecciones: List[Dict[str, Any]],
    mostrar_etiquetas: bool = True
) -> np.ndarray:
    """
    Dibuja contornos o cajas delimitadoras sobre la imagen según la clase SIPaKMeD de cada célula.

    :param imagen: Imagen BGR de entrada
    :type imagen: np.ndarray
    :param detecciones: Lista de diccionarios con 'bbox' [x, y, w, h] o 'centroide' (cx, cy) y 'clase'
    :type detecciones: List[Dict[str, Any]]
    :param mostrar_etiquetas: Si se debe mostrar el texto de la clase sobre la celda
    :type mostrar_etiquetas: bool
    :return: Imagen anotada con códigos de color multiclase
    :rtype: np.ndarray
    """
    validar_tamano_visualizacion(imagen)
    img_salida = imagen.copy()

    if len(img_salida.shape) == 2:
        img_salida = cv2.cvtColor(img_salida, cv2.COLOR_GRAY2BGR)

    for det in detecciones:
        clase = det.get("clase", "Superficial-Intermediate")
        color = COLORES_SIPAKMED_BGR.get(clase, (0, 255, 0))

        # Dibujar bbox si está disponible
        if "bbox" in det:
            x, y, w, h = det["bbox"]
            cv2.rectangle(img_salida, (x, y), (x + w, y + h), color, 2)
            punto_texto = (x, max(15, y - 5))
        elif "centroide" in det:
            cx, cy = det["centroide"]
            radio = det.get("radio", 15)
            cv2.circle(img_salida, (int(cx), int(cy)), int(radio), color, 2)
            punto_texto = (int(cx) - radio, max(15, int(cy) - radio - 5))
        else:
            continue

        if mostrar_etiquetas:
            texto = f"{clase[:3].upper()}"
            cv2.putText(
                img_salida,
                texto,
                punto_texto,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
                cv2.LINE_AA
            )

    return img_salida
