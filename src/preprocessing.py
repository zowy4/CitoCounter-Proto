"""
preprocessing.py - Preprocesamiento de Imágenes de Microscopía

Este módulo prepara las imágenes del microscopio para el análisis DoG:
1. Conversión a escala de grises
2. Mejora de contraste (ecualización de histograma)
3. Reducción de ruido (filtros opcionales)
4. Normalización de intensidad

Objetivo: Optimizar la imagen para que el filtro DoG funcione mejor
"""

import cv2
import numpy as np


def cargar_imagen(ruta_imagen):
    """
    Carga una imagen desde disco con validación.
    
    Args:
        ruta_imagen (str): Ruta al archivo de imagen
    
    Returns:
        numpy.ndarray: Imagen BGR (formato de OpenCV)
    
    Raises:
        FileNotFoundError: Si la imagen no existe
        ValueError: Si la imagen está corrupta o no puede leerse
    """
    imagen = cv2.imread(ruta_imagen)
    
    if imagen is None:
        raise FileNotFoundError(
            f"No se pudo cargar la imagen: {ruta_imagen}\n"
            "Verifica que el archivo existe y es una imagen válida."
        )
    
    return imagen


def convertir_a_gris(imagen_bgr):
    """
    Convierte una imagen BGR (color) a escala de grises.
    
    El filtro DoG trabaja sobre intensidades de píxeles, no colores.
    OpenCV usa una conversión ponderada: Gray = 0.299*R + 0.587*G + 0.114*B
    (Los valores están ajustados a la percepción humana del brillo)
    
    Args:
        imagen_bgr (numpy.ndarray): Imagen en formato BGR
    
    Returns:
        numpy.ndarray: Imagen en escala de grises (8-bit, 0-255)
    """
    if len(imagen_bgr.shape) == 2:
        # Ya está en escala de grises
        return imagen_bgr
    
    return cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2GRAY)


def mejorar_contraste(imagen_gris, metodo='clahe'):
    """
    Mejora el contraste de la imagen para resaltar estructuras celulares.
    
    En microscopía, la iluminación puede ser irregular. Esta función
    compensa esas variaciones para que el DoG funcione mejor.
    
    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises
        metodo (str): Método de mejora de contraste:
            - 'clahe': Contrast Limited Adaptive Histogram Equalization (RECOMENDADO)
            - 'histogram': Ecualización de histograma global
            - 'normalize': Normalización simple (remap a 0-255)
    
    Returns:
        numpy.ndarray: Imagen con contraste mejorado
    
    Notas:
        CLAHE es superior a ecualización global porque:
        - Preserva detalles locales
        - No amplifica demasiado el ruido
        - Funciona bien con iluminación irregular del microscopio
    """
    
    if metodo == 'clahe':
        # CLAHE: Mejor para microscopía
        # clipLimit: Limita la amplificación de ruido (2.0 es conservador)
        # tileGridSize: Tamaño de las regiones locales (8x8 es estándar)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(imagen_gris)
    
    elif metodo == 'histogram':
        # Ecualización global (puede amplificar ruido)
        return cv2.equalizeHist(imagen_gris)
    
    elif metodo == 'normalize':
        # Normalización simple: mapea [min, max] -> [0, 255]
        return cv2.normalize(imagen_gris, None, 0, 255, cv2.NORM_MINMAX)
    
    else:
        raise ValueError(f"Método desconocido: {metodo}. "
                        "Usa 'clahe', 'histogram' o 'normalize'")


def reducir_ruido(imagen_gris, nivel='medio'):
    """
    Aplica filtros de reducción de ruido sin perder detalles importantes.
    
    El ruido en microscopía puede venir de:
    - Ruido electrónico del sensor de la cámara
    - Polvo en el portaobjetos
    - Artefactos de tinción irregular
    
    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises
        nivel (str): Intensidad del filtro:
            - 'bajo': Suavizado mínimo (preserva máximo detalle)
            - 'medio': Balance entre ruido y detalle (RECOMENDADO)
            - 'alto': Reducción agresiva (puede perder detalles finos)
    
    Returns:
        numpy.ndarray: Imagen con ruido reducido
    
    Nota:
        Usa filtro bilateral que preserva bordes (mejor que Gaussiano simple)
    """
    
    if nivel == 'bajo':
        # Filtro bilateral conservador
        # d=5: vecindad pequeña
        # sigmaColor=50: diferencias de intensidad moderadas
        # sigmaSpace=50: distancia espacial moderada
        return cv2.bilateralFilter(imagen_gris, d=5, sigmaColor=50, sigmaSpace=50)
    
    elif nivel == 'medio':
        return cv2.bilateralFilter(imagen_gris, d=7, sigmaColor=75, sigmaSpace=75)
    
    elif nivel == 'alto':
        return cv2.bilateralFilter(imagen_gris, d=9, sigmaColor=100, sigmaSpace=100)
    
    else:
        raise ValueError(f"Nivel desconocido: {nivel}. Usa 'bajo', 'medio' o 'alto'")


def preprocesar_imagen(ruta_imagen, mejorar_contraste_flag=True, 
                       reducir_ruido_flag=False, metodo_contraste='clahe',
                       nivel_ruido='medio'):
    """
    Pipeline completo de preprocesamiento (función de conveniencia).
    
    Aplica todos los pasos en el orden correcto:
    1. Cargar imagen
    2. Convertir a gris
    3. Reducir ruido (opcional)
    4. Mejorar contraste (opcional)
    
    Args:
        ruta_imagen (str): Ruta al archivo de imagen
        mejorar_contraste_flag (bool): Si True, aplica mejora de contraste
        reducir_ruido_flag (bool): Si True, aplica reducción de ruido
        metodo_contraste (str): Método para mejora de contraste
        nivel_ruido (str): Nivel de reducción de ruido
    
    Returns:
        tuple: (imagen_procesada, imagen_original)
            - imagen_procesada: Escala de grises lista para DoG
            - imagen_original: Imagen BGR original (para visualización)
    
    Recomendaciones:
        Para imágenes de buena calidad: solo conversión a gris
        Para iluminación irregular: activar mejorar_contraste_flag
        Para imágenes muy ruidosas: activar reducir_ruido_flag
    """
    
    # 1. Cargar imagen original
    imagen_original = cargar_imagen(ruta_imagen)
    
    # 2. Convertir a escala de grises
    imagen_gris = convertir_a_gris(imagen_original)
    
    # 3. Reducir ruido (si se solicita)
    # NOTA: Se hace ANTES de mejorar contraste para no amplificar ruido
    if reducir_ruido_flag:
        imagen_gris = reducir_ruido(imagen_gris, nivel=nivel_ruido)
    
    # 4. Mejorar contraste (si se solicita)
    if mejorar_contraste_flag:
        imagen_gris = mejorar_contraste(imagen_gris, metodo=metodo_contraste)
    
    return imagen_gris, imagen_original


def verificar_calidad_imagen(imagen_gris):
    """
    Analiza métricas de calidad de la imagen para detectar problemas.
    
    Esta función ayuda a identificar imágenes problemáticas que pueden
    dar resultados incorrectos en el análisis.
    
    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises
    
    Returns:
        dict: Métricas de calidad:
            - 'contraste': Contraste medido (desviación estándar)
            - 'brillo_promedio': Intensidad promedio (0-255)
            - 'saturacion': % de píxeles saturados (muy oscuros/claros)
            - 'es_aceptable': bool indicando si la imagen es apta
            - 'advertencias': Lista de problemas detectados
    """
    
    metricas = {
        'contraste': float(np.std(imagen_gris)),
        'brillo_promedio': float(np.mean(imagen_gris)),
        'saturacion': 0.0,
        'es_aceptable': True,
        'advertencias': []
    }
    
    # Calcular píxeles saturados (muy oscuros o muy claros)
    pixels_oscuros = np.sum(imagen_gris < 10)
    pixels_claros = np.sum(imagen_gris > 245)
    total_pixels = imagen_gris.size
    metricas['saturacion'] = ((pixels_oscuros + pixels_claros) / total_pixels) * 100
    
    # Verificar problemas
    if metricas['contraste'] < 15:
        metricas['advertencias'].append("⚠️  Contraste muy bajo (imagen plana)")
        metricas['es_aceptable'] = False
    
    if metricas['brillo_promedio'] < 30:
        metricas['advertencias'].append("⚠️  Imagen muy oscura (subexpuesta)")
    elif metricas['brillo_promedio'] > 225:
        metricas['advertencias'].append("⚠️  Imagen muy clara (sobreexpuesta)")
    
    if metricas['saturacion'] > 10:
        metricas['advertencias'].append(
            f"⚠️  {metricas['saturacion']:.1f}% de píxeles saturados"
        )
    
    return metricas


def recortar_region_interes(imagen, x, y, ancho, alto):
    """
    Recorta una región rectangular de la imagen (útil para análisis focal).
    
    Args:
        imagen (numpy.ndarray): Imagen fuente
        x (int): Coordenada X de la esquina superior izquierda
        y (int): Coordenada Y de la esquina superior izquierda
        ancho (int): Ancho del recorte
        alto (int): Alto del recorte
    
    Returns:
        numpy.ndarray: Imagen recortada
    """
    return imagen[y:y+alto, x:x+ancho]
