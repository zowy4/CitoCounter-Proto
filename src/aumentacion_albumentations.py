"""
src/aumentacion_albumentations.py - Pipeline de Aumento de Datos Extendido con Albumentations (CITO-120 / ACT-42).

Proporciona aumentación de datos robusta para microscopía cervical simulando variaciones reales:
1. Ruido gaussiano y artefactos de sensor.
2. Jitter de color independiente por canales RGB y balance de blancos.
3. Transformaciones afines (rotación, escala, traslación, cizallamiento).
4. CLAHE y ajustes de contraste/brillo adaptativo.
5. Validación OWASP/STRIDE de tamaño de imagen.
"""

from typing import Optional, Tuple
import numpy as np
import cv2
import albumentations as A


def validar_tamano_imagen(imagen: np.ndarray, tamano_maximo_bytes: int = 65536 * 100) -> None:
    """
    Valida que el tamaño de la imagen no supere el límite máximo permitido
    para cumplir con los controles OWASP/STRIDE contra ataques DoS.

    :param imagen: Arreglo numpy de la imagen.
    :type imagen: np.ndarray
    :param tamano_maximo_bytes: Tamaño máximo en bytes.
    :type tamano_maximo_bytes: int
    :raises ValueError: Si la imagen excede el tamaño máximo permitido.
    """
    if imagen is None:
        raise ValueError("La imagen de entrada es nula.")
    if imagen.nbytes > tamano_maximo_bytes:
        raise ValueError(
            f"Tamaño de imagen excede el límite OWASP/STRIDE ({imagen.nbytes} bytes > {tamano_maximo_bytes} bytes)."
        )


def crear_pipeline_aumentacion_microscopia(p: float = 0.5) -> A.Compose:
    """
    Crea un pipeline de Albumentations adaptado a microscopía cervical con transformaciones afines,
    ruido gaussiano, jitter de color independiente y CLAHE.

    :param p: Probabilidad de aplicación de las transformaciones.
    :type p: float
    :rtype: albumentations.Compose
    """
    return A.Compose([
        A.Affine(
            scale=(0.9, 1.1),
            translate_percent=(-0.05, 0.05),
            rotate=(-15, 15),
            shear=(-5, 5),
            p=p
        ),
        A.CLAHE(clip_limit=(1.0, 4.0), tile_grid_size=(8, 8), p=p),
        A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=p),
        A.GaussNoise(p=p),
        A.GaussianBlur(blur_limit=(3, 7), p=p * 0.5),
    ])


def aplicar_aumentacion_albumentations(
    imagen: np.ndarray,
    pipeline: Optional[A.Compose] = None,
    probabilidad: float = 0.5
) -> np.ndarray:
    """
    Aplica el pipeline de aumentación de datos basado en Albumentations a una imagen,
    validando restricciones OWASP/STRIDE y asegurando la conversión a 8-bit (uint8).

    :param imagen: Imagen de entrada en formato BGR o RGB (numpy ndarray).
    :type imagen: np.ndarray
    :param pipeline: Instancia opcional de albumentations.Compose.
    :type pipeline: Optional[A.Compose]
    :param probabilidad: Probabilidad por defecto si no se provee pipeline.
    :type probabilidad: float
    :return: Imagen aumentada y convertida a uint8 de 8-bit.
    :rtype: np.ndarray
    :raises ValueError: Si la imagen excede el tamaño permitido o es inválida.
    """
    validar_tamano_imagen(imagen)

    # Convertir float32 a uint8 si es necesario
    if imagen.dtype == np.float32 or imagen.dtype == np.float64:
        img_uint8 = np.clip(imagen * 255.0 if imagen.max() <= 1.0 else imagen, 0, 255).astype(np.uint8)
    else:
        img_uint8 = imagen.astype(np.uint8)

    if pipeline is None:
        pipeline = crear_pipeline_aumentacion_microscopia(p=probabilidad)

    augmented = pipeline(image=img_uint8)
    resultado = augmented["image"]

    if not isinstance(resultado, np.ndarray):
        resultado = np.array(resultado, dtype=np.uint8)

    return resultado.astype(np.uint8)


