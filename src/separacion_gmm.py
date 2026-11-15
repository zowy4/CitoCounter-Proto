"""
src/separacion_gmm.py - Módulo de Separación Avanzada de Cúmulos Celulares mediante GMM (CITO-121 / ACT-43).

Combina la transformada de distancia euclidiana, estimación de umbrales locales basados en
Modelos de Mezcla Gaussiana (GMM) y Watershed para resolver la fusión de núcleos en cúmulos densos
de citología cervical.
"""

from typing import List, Tuple, Optional
import numpy as np
import cv2
from sklearn.mixture import GaussianMixture


def validar_tamano_imagen_gmm(imagen: np.ndarray, tamano_maximo_bytes: int = 65536 * 100) -> None:
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


def separar_cumulos_gmm(
    imagen_dog: np.ndarray,
    n_components: int = 2,
    distancia_minima: int = 10,
    mascara: Optional[np.ndarray] = None
) -> Tuple[List[np.ndarray], List[float]]:
    """
    Separa cúmulos celulares superpuestos ajustando un Modelo de Mezcla Gaussiana (GMM)
    a la distribución de intensidades, combinándolo con la transformada de distancia y Watershed.

    :param imagen_dog: Imagen DoG en escala de grises (8-bit).
    :type imagen_dog: np.ndarray
    :param n_components: Número de componentes gaussianas para el GMM (típicamente 2: fondo y cúmulo/núcleos).
    :type n_components: int
    :param distancia_minima: Distancia mínima entre picos para evitar detecciones redundantes.
    :type distancia_minima: int
    :param mascara: Máscara binaria opcional (255=válido, 0=ignorar).
    :type mascara: Optional[np.ndarray]
    :return: Tupla con (lista de contornos de núcleos separados, lista de áreas de cada núcleo).
    :rtype: Tuple[List[np.ndarray], List[float]]
    :raises ValueError: Si la imagen es inválida o excede los límites OWASP.
    """
    validar_tamano_imagen_gmm(imagen_dog)

    # Asegurar escala de grises uint8
    if len(imagen_dog.shape) == 3:
        gris = cv2.cvtColor(imagen_dog, cv2.COLOR_BGR2GRAY)
    else:
        gris = imagen_dog.copy()

    # Normalizar a float en [0, 1] para GMM
    pixels = gris.astype(np.float32).reshape(-1, 1)

    # Ajustar GMM de n_components
    gmm = GaussianMixture(n_components=n_components, random_state=42, n_init=3)
    gmm.fit(pixels)
    labels = gmm.predict(pixels).reshape(gris.shape)

    # Identificar cuál componente corresponde al fondo (media más alta en imágenes DoG oscuras o según luminancia)
    means = gmm.means_.flatten()
    cluster_fondo = int(np.argmax(means))

    # Crear máscara binaria donde las regiones que NO son fondo representan los cúmulos/núcleos
    binaria_gmm = np.ones(gris.shape, dtype=np.uint8) * 255
    binaria_gmm[labels == cluster_fondo] = 0

    # Aplicar apertura morfológica suave para eliminar ruido
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binaria_gmm = cv2.morphologyEx(binaria_gmm, cv2.MORPH_OPEN, kernel)

    # Transformada de distancia euclidiana sobre la máscara binaria GMM
    dist_transform = cv2.distanceTransform(binaria_gmm, cv2.DIST_L2, 5)

    if dist_transform.max() == 0:
        return [], []

    # Encontrar máximos locales (picos de distancia) para marcadores de Watershed
    kernel_size = max(3, distancia_minima * 2 + 1)
    kernel_maximos = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    dist_dilatada = cv2.dilate(dist_transform, kernel_maximos)
    picos = np.logical_and(
        dist_transform >= 0.3 * dist_transform.max(),
        dist_transform == dist_dilatada
    ).astype(np.uint8) * 255

    _, marcadores = cv2.connectedComponents(picos)
    marcadores = marcadores.astype(np.int32) + 1

    fondo_seguro = cv2.dilate(binaria_gmm, kernel, iterations=2)
    region_desconocida = cv2.subtract(fondo_seguro, picos)
    marcadores[region_desconocida == 255] = 0

    # Preparar imagen en 8-bit de 3 canales para cv2.watershed
    imagen_8bit = cv2.normalize(gris, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    imagen_bgr = cv2.cvtColor(imagen_8bit, cv2.COLOR_GRAY2BGR)

    # Aplicar Watershed
    marcadores = cv2.watershed(imagen_bgr, marcadores)
    marcadores[marcadores == -1] = 0  # Fronteras

    # Extraer contornos individuales de cada etiqueta de Watershed
    contornos_nucleos = []
    areas = []

    for label in range(2, marcadores.max() + 1):
        mask = np.zeros_like(marcadores, dtype=np.uint8)
        mask[marcadores == label] = 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = float(cv2.contourArea(largest_contour))
            if area > 0:
                # Filtrar por máscara si se proporciona
                if mascara is not None:
                    M = cv2.moments(largest_contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        if 0 <= cy < mascara.shape[0] and 0 <= cx < mascara.shape[1]:
                            if mascara[cy, cx] > 0:
                                contornos_nucleos.append(largest_contour)
                                areas.append(area)
                else:
                    contornos_nucleos.append(largest_contour)
                    areas.append(area)

    return contornos_nucleos, areas
