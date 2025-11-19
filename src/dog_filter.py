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
    # Usamos cv2.subtract para manejar correctamente valores negativos
    dog = cv2.subtract(g1, g2)
    
    # 4. Normalizar para visualizar mejor (mapea al rango 0-255)
    # Esto es opcional pero útil para depuración y visualización
    dog_norm = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX)
    
    return dog_norm.astype(np.uint8)


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
    dog = cv2.subtract(g1, g2)
    dog_norm = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX)
    
    return {
        'g1': g1,
        'g2': g2,
        'dog': dog_norm
    }
