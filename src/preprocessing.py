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


# Polaridades soportadas por el pipeline (hallazgo Fase 2.1, CITO-22/23).
# - 'nucleos-claros': núcleos claros sobre fondo oscuro (fluorescencia).
#   Es el dominio que el DoG + Otsu detecta sin cambios.
# - 'nucleos-oscuros': núcleos oscuros sobre fondo claro (campo claro,
#   Papanicolaou, imágenes reales EDF). Requiere invertir la imagen
#   antes del DoG para que los núcleos se comporten como blobs claros.
POLARIDADES_VALIDAS = ('nucleos-claros', 'nucleos-oscuros')


def validar_polaridad(polaridad):
    """Valida el valor de polaridad o lanza ValueError con opciones válidas."""
    if polaridad not in POLARIDADES_VALIDAS:
        raise ValueError(
            f"Polaridad desconocida: {polaridad}. "
            f"Usa una de: {', '.join(POLARIDADES_VALIDAS)}"
        )
    return polaridad


def invertir_polaridad(imagen_gris):
    """
    Invierte la polaridad de una imagen en escala de grises (255 - valor).

    El filtro DoG + umbralizado de Otsu detecta blobs CLAROS sobre fondo
    oscuro. Las imágenes reales de citología (EDF, Papanicolaou) tienen
    núcleos OSCUROS sobre citoplasma claro, por lo que su respuesta DoG
    es negativa en el centro del núcleo y no se segmenta (hallazgo Fase
    2.1: 0-1 detecciones en imágenes reales).

    Invertir la imagen convierte los núcleos oscuros en blobs claros y
    permite reutilizar el pipeline sin cambiar el DoG ni las reglas de
    clasificación.

    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises (8-bit)

    Returns:
        numpy.ndarray: Imagen invertida (mismo dtype y dimensiones)
    """
    return cv2.bitwise_not(imagen_gris)


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


def mejorar_contraste(imagen_gris, metodo='clahe', automatico=False):
    """
    Mejora el contraste de la imagen para resaltar estructuras celulares.
    
    En microscopía, la iluminación puede ser irregular. Esta función
    compensa esas variaciones para que el DoG funcione mejor.
    
    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises
        metodo (str): Método de mejora de contraste:
            - 'clahe': Contrast Limited Adaptive Histogram Equalization (RECOMENDADO)
            - 'histogram': Ecualización de histograma global
            - 'normalize': Normalización simple (remap a 0-255
        - 'auto': Selecciona automáticamente basado en el contraste actual (CITO-33)
    
    Returns:
        tuple: (imagen_mejorada, metodo_usado, contraste_original, contraste_mejorado)
    
    Notas:
        CLAHE es superior a ecualización global porque:
        - Preserva detalles locales
        - No amplifica demasiado el ruido
        - Funciona bien con iluminación irregular del microscopio
    """
    
    # Calcular contraste original
    contraste_original = np.std(imagen_gris)
    
    if metodo == 'auto':
        # CITO-33: Selección automática basada en el contraste actual
        if contraste_original < 20:
            # Contraste muy bajo: usar CLAHE con configuración suave
            clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(8, 8))
            imagen_mejorada = clahe.apply(imagen_gris)
            metodo_usado = 'clahe-suave'
        elif contraste_original < 40:
            # Contraste medio: CLAHE estándar
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            imagen_mejorada = clahe.apply(imagen_gris)
            metodo_usado = 'clahe'
        else:
            # Contraste alto: ecualización global suave
            imagen_mejorada = cv2.equalizeHist(imagen_gris)
            metodo_usado = 'histogram-suave'
    elif metodo == 'clahe':
        # CLAHE: Mejor para microscopía
        # clipLimit: Limita la amplificación de ruido (2.0 es conservador)
        # tileGridSize: Tamaño de las regiones locales (8x8 es estándar)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        imagen_mejorada = clahe.apply(imagen_gris)
        metodo_usado = 'clahe'
    elif metodo == 'histogram':
        # Ecualización global (puede amplificar ruido)
        imagen_mejorada = cv2.equalizeHist(imagen_gris)
        metodo_usado = 'histogram'
    elif metodo == 'normalize':
        # Normalización simple: mapea [min, max] -> [0, 255]
        imagen_mejorada = cv2.normalize(imagen_gris, None, 0, 255, cv2.NORM_MINMAX)
        metodo_usado = 'normalize'
    else:
        raise ValueError(f"Método desconocido: {metodo}. "
                        "Usa 'clahe', 'histogram', 'normalize' o 'auto'")
    
    # Calcular contraste mejorado
    contraste_mejorado = np.std(imagen_mejorada)
    
    return imagen_mejorada, metodo_usado, contraste_original, contraste_mejorado


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
                       nivel_ruido='medio', polaridad='nucleos-claros'):
    """
    Pipeline completo de preprocesamiento (función de conveniencia).
    
    Aplica todos los pasos en el orden correcto:
    1. Cargar imagen
    2. Convertir a gris
    3. Reducir ruido (opcional)
    4. Mejorar contraste (opcional)
    5. Ajustar polaridad (opcional, CITO-22/23 Fase 2.3)
    
    Args:
        ruta_imagen (str): Ruta al archivo de imagen
        mejorar_contraste_flag (bool): Si True, aplica mejora de contraste
        reducir_ruido_flag (bool): Si True, aplica reducción de ruido
        metodo_contraste (str): Método para mejora de contraste
        nivel_ruido (str): Nivel de reducción de ruido
        polaridad (str): 'nucleos-claros' (default, sin cambios) o
            'nucleos-oscuros' (invierte la imagen para citología de campo
            claro tipo Papanicolaou/EDF)
    
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
        resultado = mejorar_contraste(imagen_gris, metodo=metodo_contraste)
        # El nuevo formato retorna tupla (imagen, metodo, contraste_orig, contraste_mej)
        # Para compatibilidad, usamos solo la imagen mejorada
        if isinstance(resultado, tuple):
            imagen_gris = resultado[0]
        else:
            imagen_gris = resultado
    
    # 5. Ajustar polaridad (si se solicita)
    # Se aplica al final para que CLAHE y la reducción de ruido trabajen
    # sobre la intensidad original de la imagen; la inversión solo cambia
    # el signo de la respuesta DoG, no la geometría de los núcleos.
    validar_polaridad(polaridad)
    if polaridad == 'nucleos-oscuros':
        imagen_gris = invertir_polaridad(imagen_gris)
    
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
    """"
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


def segmentar_por_hsv(imagen_bgr, umbral_sat=100, umbral_val=100, metodo='saturation'):
    """
    Segmenta núcleos usando el espacio de color HSV.

    Convierte la imagen de BGR a HSV y aplica umbrales en el canal de saturación (S)
    o valor (V) para separar núcleos del citoplasma. Útil cuando el contraste de intensidad
    es bajo pero la diferencia de color es significativa.

    Args:
        imagen_bgr (numpy.ndarray): Imagen original en formato BGR (3 canales)
        umbral_sat (int): Umbral mínimo para el canal de saturación (0-255). Default: 100
        umbral_val (int): Umbral mínimo para el canal de valor (0-255). Default: 100
        metodo (str): Método de umbralización:
            - 'saturation': Umbralizar en canal S (saturación). Usa cuando los núcleos
              tienen color distinto al citoplasma.
            - 'value': Umbralizar en canal V (brillo/valor). Usa cuando los núcleos son
              más brillos u oscuros que el fondo.

    Returns:
        numpy.ndarray: Máscara binaria donde blancos = núcleos detectados, negros = fondo

    Ejemplo:
        >>> mask = segmentar_por_hsv(imagen, umbral_sat=80, umbral_val=80, metodo='saturation')
        >>> # Resultado: máscara lista para aplicar cv2.findContours()

    Nota:
        - El canal S (saturación) varía de 0 (gris) a 255 (color puro)
        - El canal V (valor/brillo) varía de 0 (negro) a 255 (blanco brillante)
        - Después del umbralizado, aplica apertura morfológica para eliminar ruido pequeño
        - La dilatación ligera ayuda a conectar regiones nucleares cercanas
    """
    
    # Convertir de BGR a HSV
    imagen_hsv = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2HSV)
    
    # Umbralizar según el método especificado
    if metodo == 'saturation':
        # Usar canal S (saturación): 1 = totalmente desaturado, 255 = color puro
        _, mask = cv2.threshold(imagen_hsv[:, :, 1], umbral_sat, 255, cv2.THRESH_BINARY)
    elif metodo == 'value':
        # Usar canal V (brillo/valor): 0 = negro, 255 = blanco brillante
        _, mask = cv2.threshold(imagen_hsv[:, :, 2], umbral_val, 255, cv2.THRESH_BINARY)
    else:
        raise ValueError(f"Método HSV desconocido: {metodo}. "
                        "Usa 'saturation' o 'value'")
    
    # Aplicar morfología abierta para eliminar ruido pequeño
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Aplicar dilatación ligera para conectar regiones cercanas
    mask = cv2.dilate(mask, kernel, iterations=1)
    
    return mask


def preprocesar_imagen(ruta_imagen, mejorar_contraste=True,
                       reducir_ruido=False, metodo_contraste='clahe',
                       nivel_ruido='medio', polaridad='nucleos-claros', 
                       usar_hsv=False, metodo_hsv='saturation', umbral_hsv=100):
    """
    Preprocesa una imagen para el análisis DoG, con opciones extendidas.
    
    Flujo completo:
    1. Cargar imagen BGR
    2. Convertir a escala de grises
    3. (Opcional) Aplicar segmentación HSV para resaltar núcleos por color
    4. (Opcional) Mejorar contraste con CLAHE
    5. (Opcional) Reducir ruido con filtro bilateral
    6. Normalizar intensidad
    
    Args:
        ruta_imagen (str): Ruta al archivo de imagen
        mejorar_contraste (bool): Si mejorar contraste con CLAHE (default: True)
        reducir_ruido (bool): Si aplicar filtro bilateral de ruido (default: False)
        metodo_contraste (str): Método CLAHE ('clahe', 'histogram', 'normalize')
        nivel_ruido (str): Nivel de reducción de ruido ('bajo', 'medio', 'alto')
        polaridad (str): 'nucleos-claros' o 'nucleos-oscuros'
        usar_hsv (bool): Si aplicar segmentación HSV antes del pipeline (default: False)
        metodo_hsv (str): Método HSV ('saturation' o 'value')
        umbral_hsv (int): Umbral para segmentación HSV (0-255, default: 100)
    
    Returns:
        tuple: (imagen_procesada, metadata)
        - imagen_procesada (numpy.ndarray): Imagen lista para DoG (gris, ruido reducido, CLAHE)
        - metadata (dict): Registro de operaciones aplicadas para reproducibilidad
    
    Notas:
        - Cuando usar_hsv=True, la segmentación HSV se aplica SOBRE la imagen original
          y sus resultados se combinan con el pipeline DoG estándar
        - metadata incluye: 'polaridad', 'usar_hsv', 'metodo_hsv', 'umbral_hsv',
          'contraste_mejorado', 'ruido_reducido'
    """
    
    # 1. Cargar imagen
    imagen_bgr = cargar_imagen(ruta_imagen)
    
    # Inicializar metadata
    metadata = {
        'ruta': ruta_imagen,
        'polaridad': polaridad,
        'usar_hsv': usar_hsv,
        'metodo_hsv': metodo_hsv,
        'umbral_hsv': umbral_hsv,
        'contraste_mejorado': False,
        'ruido_reducido': False
    }
    
    # 2. Convertir a escala de grises
    imagen_gris = convertir_a_gris(imagen_bgr)
    
    # 3. (Opcional) Segmentación HSV para resaltar núcleos por color
    if usar_hsv:
        mask_hsv = segmentar_por_hsv(imagen_bgr, umbral_sat=umbral_hsv,
                                      umbral_val=umbral_hsv,
                                      metodo=metodo_hsv)
        # Combinar máscara HSV con imagen gris: donde hay máscara HSV = mantener píxel original
        # donde no hay máscara = fondo negro
        imagen_gris = cv2.bitwise_and(imagen_gris, imagen_gris, mask=mask_hsv)
        metadata['metodo_hsv_aplicado'] = metodo_hsv
        metadata['umbral_hsv_aplicado'] = umbral_hsv
    
    # 4. Mejorar contraste
    if mejorar_contraste:
        imagen_gris, metodo_usado, contraste_original, contraste_mejorado = \
            mejorar_contraste(imagen_gris, metodo=metodo_contraste)
        metadata['metodo_contraste'] = metodo_usado
        metadata['contraste_original'] = float(contraste_original)
        metadata['contraste_mejorado'] = float(contraste_mejorado)
        metadata['contraste_aumento'] = float(contraste_mejorado - contraste_original)
    else:
        metadata['metodo_contraste'] = 'none'
        metadata['contraste_original'] = float(np.std(imagen_gris))
        metadata['contraste_mejorado'] = float(np.std(imagen_gris))
    
    # 5. Reducir ruido
    if reducir_ruido:
        imagen_gris = reducir_ruido(imagen_gris, nivel=nivel_ruido)
        metadata['ruido_reducido'] = True
        metadata['nivel_ruido'] = nivel_ruido
    else:
        metadata['ruido_reducido'] = False
    
    # 6. Normalizar intensidad (último paso antes de DoG)
    imagen_procesada = cv2.normalize(imagen_gris, None, 0, 1, cv2.NORM_MINMAX)
    
    # Agregar metadata de normalización
    metadata['normalizada'] = True
    metadata['rango_normalizado'] = (0.0, 1.0)
    
    return imagen_procesada, metadata
