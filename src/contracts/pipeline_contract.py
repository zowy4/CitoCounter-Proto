"""
Contratos de datos e interfaces base para el pipeline de CitoCounter-Proto.

Define estructuras tipo dataclass y clases abstractas que establecen
contratos explícitos entre los módulos del pipeline (preprocesamiento,
filtro DoG, análisis y visualización).
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np


@dataclass
class ParametrosAnalisis:
    """
    Parámetros de configuración para el análisis de nucleos.

    Attributes:
        sigma1: Sigma para el primer gaussiano del filtro DoG.
        sigma2: Sigma para el segundo gaussiano del filtro DoG.
        umbral_dog: Umbral para la detección de núcleos después del DoG.
        polaridad: 'nucleos-claros' o 'nucleos-oscuros' según la polaridad
            esperada en la imagen.
        tamano_maximo_kb: Tamaño máximo permitido de la imagen en KB para
            validación OWASP/STRIDE antes del procesamiento.
    """

    sigma1: float
    sigma2: float
    umbral_dog: float
    polaridad: str
    tamano_maximo_kb: int


@dataclass
class ResultadoSegmentacion:
    """
    Resultado de una operación de segmentación de núcleos.

    Attributes:
        exitoso: Indica si la segmentación completó exitosamente.
        total_nucleos: Número total de núcleos detectados.
        mapa_contornos: Arreglo de numpy con los contornos detectados (Optional).
        metricas_detalle: Diccionario con métricas detalladas (Precision, Recall, F1, IoU).
        errores: Lista de mensajes de error ocurridos durante la segmentación.
    """

    exitoso: bool
    total_nucleos: int
    mapa_contornos: Optional[np.ndarray]
    metricas_detalle: dict[str, Any]
    errores: list[str]


class AlgoritmoSegmentacionBase(abc.ABC):
    """
    Clase abstracta base que define la interfaz para todos los algoritmos
    de segmentación en el pipeline.

    Subclases deben implementar el método `procesar` con la firma exacta
    definida aquí para garantizar la compatibilidad con el pipeline.
    """

    @abc.abstractmethod
    def procesar(self, imagen: np.ndarray) -> ResultadoSegmentacion:
        """
        Procesa una imagen y devuelve el resultado de segmentación.

        Args:
            imagen: Imagen en escala de grises (8-bit) lista para el procesamiento.

        Returns:
            ResultadoSegmentacion: Objeto con los resultados de la segmentación.

        Raises:
            ValueError: Si la imagen no cumple con los requisitos de validación.
            RuntimeError: Si ocurre un error durante el procesamiento.
        """
        ...


def validar_tamano_imagen(
    imagen: np.ndarray, tamano_maximo_kb: int = 65536
) -> None:
    """
    Valida que el tamaño de la imagen no supere el límite máximo en KB.

    Aplica controles OWASP/STRIDE para prevenir ataques de denegación de servicio
    dirigidos a recursos de procesamiento de imágenes.

    Args:
        imagen: Arreglo de numpy con la imagen a validar.
        tamano_maximo_kb: Tamaño máximo permitido en kilobytes (default: 65536 = 64 KiB).

    Raises:
        ValueError: Si el tamaño de la imagen excede el límite máximo.
    """
    tamano_bytes = imagen.nbytes
    tamano_maximo_bytes = tamano_maximo_kb * 1024

    if tamano_bytes > tamano_maximo_bytes:
        raise ValueError(
            f"Tamaño de imagen excedido: {tamano_bytes / 1024:.1f} KB > "
            f"{tamano_maximo_kb} KB máximo permitido. "
            "Aplique controles OWASP/STRIDE o procese la imagen en lotes más pequeños."
        )