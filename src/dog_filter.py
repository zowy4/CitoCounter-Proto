"""
dog_filter.py - Implementación del Filtro Diferencia de Gaussiana (DoG)

El filtro DoG es el corazón del algoritmo. Resalta estructuras del tamaño
de interés (núcleos celulares) mientras suprime el ruido de fondo.

Parámetros clave:
- sigma1: Desenfoque fino (captura detalles pequeños)
- sigma2: Desenfoque grueso (captura estructura general)
- La diferencia g1 - g2 aísla los bordes del tamaño objetivo
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional


def _calcular_diferencia_dog(g1, g2):
    """Calcula la diferencia DoG conservando valores negativos."""
    return g1.astype(np.float32) - g2.astype(np.float32)


def aplicar_filtro_dog(imagen_gris, sigma1=1.0, sigma2=2.0):
    """
    Aplica la Diferencia de Gaussiana (DoG) a una imagen en escala de grises.
    
    La clave es elegir sigmas que 'encierren' el tamaño promedio de un núcleo.
    Estos valores deberán ajustarse experimentalmente durante la calibración.
    
    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises (8-bit)
        sigma1 (float): Desviación estándar del primer Gaussiano (detalles finos)
        sigma2 (float): Desviación estándar del segundo Gaussiano (estructura general)
                        Debe ser > sigma1 (típicamente sigma2 = 1.6 * sigma1)
    
    Returns:
        numpy.ndarray: Imagen DoG normalizada (0-255)
    
    Notas científicas:
        - DoG aproxima el Laplaciano de Gaussiana (LoG) pero es más rápido
        - Resalta bordes a la escala definida por sigma2/sigma1
        - El tamaño del kernel se calcula automáticamente como 6*sigma + 1
    """
    
    # Validación de parámetros
    if sigma2 <= sigma1:
        raise ValueError(f"sigma2 ({sigma2}) debe ser mayor que sigma1 ({sigma1})")
    
    # 1. Primer desenfoque Gaussiano (detalles finos)
    # ksize=(0,0) hace que OpenCV calcule automáticamente el tamaño óptimo del kernel
    g1 = cv2.GaussianBlur(imagen_gris, (0, 0), sigma1)
    
    # 2. Segundo desenfoque Gaussiano (estructura general)
    g2 = cv2.GaussianBlur(imagen_gris, (0, 0), sigma2)
    
    # 3. La Diferencia de Gaussiana (DoG)
    # Convertir antes a float evita que uint8 recorte las diferencias negativas.
    dog = _calcular_diferencia_dog(g1, g2)
    
    # 4. Normalizar para visualizar mejor (mapea al rango 0-255)
    # Esto es opcional pero útil para depuración y visualización
    # NOTA: cv2.normalize con NORM_MINMAX mapea el valor mínimo a 0 y el máximo a 255.
    # Los valores negativos del DoG se desplazan hacia 0, lo que puede hacer que
    # regiones con fuerte respuesta negativa aparezcan como fondo oscuro.
    dog_norm = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX)
    
    # 5. Convertir a uint8 para compatibilidad con watershed y visualización
    # Rule CITO-42: float32 -> uint8 antes de watershed u otros operadores de 8-bit
    dog_uint8 = dog_norm.astype(np.uint8)
    
    return dog_uint8


def calcular_sigmas_optimas(diametro_promedio_nucleo):
    """
    Calcula valores iniciales de sigma basados en el tamaño esperado del núcleo.
    
    Regla empírica: sigma1 ≈ diametro/6, sigma2 ≈ diametro/3
    Esto asegura que el filtro DoG sea sensible a estructuras del tamaño del núcleo.
    
    Args:
        diametro_promedio_nucleo (float): Diámetro promedio del núcleo en píxeles
    
    Returns:
        tuple: (sigma1, sigma2) sugeridos
    
    Ejemplo:
        Si un núcleo mide ~30 píxeles de diámetro:
        sigma1 = 30/6 = 5.0
        sigma2 = 30/3 = 10.0
    """
    sigma1 = diametro_promedio_nucleo / 6.0
    sigma2 = diametro_promedio_nucleo / 3.0
    
    return sigma1, sigma2


def visualizar_filtros_gauss(imagen_gris, sigma1, sigma2):
    """
    Función de depuración para visualizar los componentes del filtro DoG.
    
    Útil durante la fase de calibración para entender qué detecta cada sigma.
    
    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises
        sigma1 (float): Sigma del primer Gaussiano
        sigma2 (float): Sigma del segundo Gaussiano
    
    Returns:
        dict: Diccionario con las imágenes intermedias
            - 'g1': Primer desenfoque
            - 'g2': Segundo desenfoque
            - 'dog': Diferencia de Gaussiana
    """
    g1 = cv2.GaussianBlur(imagen_gris, (0, 0), sigma1)
    g2 = cv2.GaussianBlur(imagen_gris, (0, 0), sigma2)
    dog = _calcular_diferencia_dog(g1, g2)
    dog_norm = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX)
    
    return {
        'g1': g1,
        'g2': g2,
        'dog': dog_norm
    }


def aplicar_multiscale_dog(
    imagen_gris: np.ndarray,
    escalas: Optional[List[Tuple[float, float]]] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Aplica múltiples niveles de escalas DoG (Multi-Scale DoG) para detectar
    núcleos celulares de diferentes tamaños (pequeños, normales, agrandados/SIL).

    Escalas predeterminadas:
    - Fina: (2.0, 4.0) -> Núcleos pequeños / linfocitos
    - Media: (5.0, 8.0) -> Núcleos normales (escamosos intermedios/superficiales)
    - Gruesa: (8.0, 14.0) -> Núcleos agrandados / discarióticos / SIL

    :param imagen_gris: Imagen en escala de grises (8-bit)
    :type imagen_gris: np.ndarray
    :param escalas: Lista de tuplas (sigma1, sigma2). Si es None, usa las 3 escalas estándar.
    :type escalas: list, optional
    :rtype: Tuple[np.ndarray, np.ndarray] (dog_combinado_uint8, tensor_escalas_float32)
    """
    if escalas is None:
        escalas = [
            (2.0, 4.0),   # Fina
            (5.0, 8.0),   # Media
            (8.0, 14.0)   # Gruesa
        ]

    h, w = imagen_gris.shape[:2]
    num_escalas = len(escalas)
    tensor_dog = np.zeros((h, w, num_escalas), dtype=np.float32)

    for idx, (sig1, sig2) in enumerate(escalas):
        if sig2 <= sig1:
            raise ValueError(f"sigma2 ({sig2}) debe ser mayor que sigma1 ({sig1})")
        g1 = cv2.GaussianBlur(imagen_gris, (0, 0), sig1)
        g2 = cv2.GaussianBlur(imagen_gris, (0, 0), sig2)
        dog = _calcular_diferencia_dog(g1, g2)
        tensor_dog[:, :, idx] = np.maximum(dog, 0.0)

    dog_combinado = np.max(tensor_dog, axis=2)
    dog_norm = cv2.normalize(dog_combinado, None, 0, 255, cv2.NORM_MINMAX)
    dog_uint8 = np.clip(dog_norm, 0, 255).astype(np.uint8)

    return dog_uint8, tensor_dog


def supresion_no_maximos_3d(
    tensor_dog: np.ndarray,
    umbral: float = 5.0,
    radio_espacial: int = 3
) -> List[Tuple[int, int, int, float]]:
    """
    Aplica supresión de no-máximos en 3D (espacio x, y, escala/sigma)
    para encontrar la escala óptima y evitar detecciones duplicadas.

    :param tensor_dog: Tensor 3D de respuestas DoG (H x W x NumEscalas)
    :type tensor_dog: np.ndarray
    :param umbral: Umbral mínimo de respuesta para considerar un pico
    :type umbral: float
    :param radio_espacial: Radio de vecindad en (x, y) para comprobar máximos
    :type radio_espacial: int
    :rtype: List[Tuple[int, int, int, float]] (lista de tuplas x, y, idx_escala, valor_respuesta)
    """
    h, w, num_escalas = tensor_dog.shape
    picos_3d = []

    for s in range(num_escalas):
        capa = tensor_dog[:, :, s]
        kernel_size = max(3, radio_espacial * 2 + 1)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        capa_dilatada = cv2.dilate(capa, kernel)

        maximos_espaciales = (capa == capa_dilatada) & (capa >= umbral)

        y_idxs, x_idxs = np.where(maximos_espaciales)
        for y, x in zip(y_idxs, x_idxs):
            val = capa[y, x]
            es_max_escala = True
            if s > 0 and tensor_dog[y, x, s - 1] > val:
                es_max_escala = False
            if s < num_escalas - 1 and tensor_dog[y, x, s + 1] > val:
                es_max_escala = False

            if es_max_escala:
                picos_3d.append((int(x), int(y), int(s), float(val)))

    return picos_3d
