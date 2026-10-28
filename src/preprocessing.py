"""
preprocessing.py - Preprocesamiento de ImÃ¡genes de MicroscopÃ­a

Este mÃ³dulo prepara las imÃ¡genes del microscopio para el anÃ¡lisis DoG:
1. ConversiÃ³n a escala de grises
2. Mejora de contraste (ecualizaciÃ³n de histograma)
3. ReducciÃ³n de ruido (filtros opcionales)
4. NormalizaciÃ³n de intensidad

Objetivo: Optimizar la imagen para que el filtro DoG funcione mejor
"""

import cv2
import numpy as np


# Polaridades soportadas por el pipeline (hallazgo Fase 2.1, CITO-22/23).
# - 'nucleos-claros': nÃºcleos claros sobre fondo oscuro (fluorescencia).
#   Es el dominio que el DoG + Otsu detecta sin cambios.
# - 'nucleos-oscuros': nÃºcleos oscuros sobre fondo claro (campo claro,
#   Papanicolaou, imÃ¡genes reales EDF). Requiere invertir la imagen
#   antes del DoG para que los nÃºcleos se comporten como blobs claros.
POLARIDADES_VALIDAS = ('nucleos-claros', 'nucleos-oscuros')


def validar_polaridad(polaridad):
    """Valida el valor de polaridad o lanza ValueError con opciones vÃ¡lidas."""
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
    oscuro. Las imÃ¡genes reales de citologÃ­a (EDF, Papanicolaou) tienen
    nÃºcleos OSCUROS sobre citoplasma claro, por lo que su respuesta DoG
    es negativa en el centro del nÃºcleo y no se segmenta (hallazgo Fase
    2.1: 0-1 detecciones en imÃ¡genes reales).

    Invertir la imagen convierte los nÃºcleos oscuros en blobs claros y
    permite reutilizar el pipeline sin cambiar el DoG ni las reglas de
    clasificaciÃ³n.

    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises (8-bit)

    Returns:
        numpy.ndarray: Imagen invertida (mismo dtype y dimensiones)
    """
    return cv2.bitwise_not(imagen_gris)


def cargar_imagen(ruta_imagen):
    """
    Carga una imagen desde disco con validaciÃ³n.

    Args:
        ruta_imagen (str): Ruta al archivo de imagen

    Returns:
        numpy.ndarray: Imagen BGR (formato de OpenCV)

    Raises:
        FileNotFoundError: Si la imagen no existe
        ValueError: Si la imagen estÃ¡ corrupta o no puede leerse
    """
    imagen = cv2.imread(ruta_imagen)

    if imagen is None:
        raise FileNotFoundError(
            f"No se pudo cargar la imagen: {ruta_imagen}\n"
            "Verifica que el archivo existe y es una imagen vÃ¡lida."
        )

    return imagen


def convertir_a_gris(imagen_bgr):
    """
    Convierte una imagen BGR (color) a escala de grises.

    El filtro DoG trabaja sobre intensidades de pÃ­xeles, no colores.
    OpenCV usa una conversiÃ³n ponderada: Gray = 0.299*R + 0.587*G + 0.114*B
    (Los valores estÃ¡n ajustados a la percepciÃ³n humana del brillo)

    Args:
        imagen_bgr (numpy.ndarray): Imagen en formato BGR

    Returns:
        numpy.ndarray: Imagen en escala de grises (8-bit, 0-255)
    """
    if len(imagen_bgr.shape) == 2:
        # Ya estÃ¡ en escala de grises
        return imagen_bgr

    return cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2GRAY)


def mejorar_contraste(imagen_gris, metodo='clahe', automatico=False):
    """
    Mejora el contraste de la imagen para resaltar estructuras celulares.

    En microscopÃ­a, la iluminaciÃ³n puede ser irregular. Esta funciÃ³n
    compensa esas variaciones para que el DoG funcione mejor.

    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises
        metodo (str): MÃ©todo de mejora de contraste:
            - 'clahe': Contrast Limited Adaptive Histogram Equalization (RECOMENDADO)
            - 'histogram': EcualizaciÃ³n de histograma global
            - 'normalize': NormalizaciÃ³n simple (remap a 0-255
        - 'auto': Selecciona automÃ¡ticamente basado en el contraste actual (CITO-33)

    Returns:
        tuple: (imagen_mejorada, metodo_usado, contraste_original, contraste_mejorado)

    Notas:
        CLAHE es superior a ecualizaciÃ³n global porque:
        - Preserva detalles locales
        - No amplifica demasiado el ruido
        - Funciona bien con iluminaciÃ³n irregular del microscopio
    """

    # Calcular contraste original
    contraste_original = np.std(imagen_gris)

    if metodo == 'auto':
        # CITO-33: SelecciÃ³n automÃ¡tica basada en el contraste actual
        if contraste_original < 20:
            # Contraste muy bajo: usar CLAHE con configuraciÃ³n suave
            clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(8, 8))
            imagen_mejorada = clahe.apply(imagen_gris)
            metodo_usado = 'clahe-suave'
        elif contraste_original < 40:
            # Contraste medio: CLAHE estÃ¡ndar
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            imagen_mejorada = clahe.apply(imagen_gris)
            metodo_usado = 'clahe'
        else:
            # Contraste alto: ecualizaciÃ³n global suave
            imagen_mejorada = cv2.equalizeHist(imagen_gris)
            metodo_usado = 'histogram-suave'
    elif metodo == 'clahe':
        # CLAHE: Mejor para microscopÃ­a
        # clipLimit: Limita la amplificaciÃ³n de ruido (2.0 es conservador)
        # tileGridSize: TamaÃ±o de las regiones locales (8x8 es estÃ¡ndar)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        imagen_mejorada = clahe.apply(imagen_gris)
        metodo_usado = 'clahe'
    elif metodo == 'histogram':
        # EcualizaciÃ³n global (puede amplificar ruido)
        imagen_mejorada = cv2.equalizeHist(imagen_gris)
        metodo_usado = 'histogram'
    elif metodo == 'normalize':
        # NormalizaciÃ³n simple: mapea [min, max] -> [0, 255]
        imagen_mejorada = cv2.normalize(imagen_gris, None, 0, 255, cv2.NORM_MINMAX)
        metodo_usado = 'normalize'
    else:
        raise ValueError(f"MÃ©todo desconocido: {metodo}. "
                        "Usa 'clahe', 'histogram', 'normalize' o 'auto'")

    # Calcular contraste mejorado
    contraste_mejorado = np.std(imagen_mejorada)

    return imagen_mejorada, metodo_usado, contraste_original, contraste_mejorado


def reducir_ruido(imagen_gris, nivel='medio'):
    """
    Aplica filtros de reducciÃ³n de ruido sin perder detalles importantes.

    El ruido en microscopÃ­a puede venir de:
    - Ruido electrÃ³nico del sensor de la cÃ¡mara
    - Polvo en el portaobjetos
    - Artefactos de tinciÃ³n irregular

    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises
        nivel (str): Intensidad del filtro:
            - 'bajo': Suavizado mÃ­nimo (preserva mÃ¡ximo detalle)
            - 'medio': Balance entre ruido y detalle (RECOMENDADO)
            - 'alto': ReducciÃ³n agresiva (puede perder detalles finos)

    Returns:
        numpy.ndarray: Imagen con ruido reducido

    Nota:
        Usa filtro bilateral que preserva bordes (mejor que Gaussiano simple)
    """

    if nivel == 'bajo':
        # Filtro bilateral conservador
        # d=5: vecindad pequeÃ±a
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
                       nivel_ruido='medio', polaridad='nucleos-claros',
                       usar_hsv=False, metodo_hsv='saturation', umbral_hsv=100):
    """
    Pipeline completo de preprocesamiento (funciÃ³n de conveniencia).

    Aplica todos los pasos en el orden correcto:
    1. Cargar imagen
    2. Convertir a gris
    3. Reducir ruido (opcional)
    4. Mejorar contraste (opcional)
    5. Ajustar polaridad (opcional, CITO-22/23 Fase 2.3)
    6. SegmentaciÃ³n HSV (opcional, CITO-33)

    Args:
        ruta_imagen (str): Ruta al archivo de imagen
        mejorar_contraste_flag (bool): Si True, aplica mejora de contraste
        reducir_ruido_flag (bool): Si True, aplica reducciÃ³n de ruido
        metodo_contraste (str): MÃ©todo para mejora de contraste
        nivel_ruido (str): Nivel de reducciÃ³n de ruido
        polaridad (str): 'nucleos-claros' (default, sin cambios) o
            'nucleos-oscuros' (invierte la imagen para citologÃ­a de campo
            claro tipo Papanicolaou/EDF)
        usar_hsv (bool): Si True, aplica segmentaciÃ³n HSV sobre la imagen
            original para resaltar nÃºcleos por color (CITO-33)
        metodo_hsv (str): 'saturation' o 'value'
        umbral_hsv (int): Umbral HSV en 0-255 (default: 100)

    Returns:
        tuple: (imagen_procesada, imagen_original)
            - imagen_procesada: Escala de grises lista para DoG
            - imagen_original: Imagen BGR original (para visualizaciÃ³n)

    Recomendaciones:
        Para imÃ¡genes de buena calidad: solo conversiÃ³n a gris
        Para iluminaciÃ³n irregular: activar mejorar_contraste_flag
        Para imÃ¡genes muy ruidosas: activar reducir_ruido_flag
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
    # Se aplica al final para que CLAHE y la reducciÃ³n de ruido trabajen
    # sobre la intensidad original de la imagen; la inversiÃ³n solo cambia
    # el signo de la respuesta DoG, no la geometrÃ­a de los nÃºcleos.
    validar_polaridad(polaridad)
    if polaridad == 'nucleos-oscuros':
        imagen_gris = invertir_polaridad(imagen_gris)

    # 6. SegmentaciÃ³n HSV (si se solicita, CITO-33)
    # La mÃ¡scara se calcula sobre la imagen BGR original y se aplica al final:
    # si se aplicara antes de la inversiÃ³n, el fondo a 0 se volverÃ­a 255
    # (bitwise_not(0) = 255) y la mÃ¡scara perderÃ­a su efecto.
    if usar_hsv:
        mask_hsv = segmentar_por_hsv(imagen_original, umbral_sat=umbral_hsv,
                                     umbral_val=umbral_hsv,
                                     metodo=metodo_hsv)
        imagen_gris = cv2.bitwise_and(imagen_gris, imagen_gris, mask=mask_hsv)

    return imagen_gris, imagen_original


def anonimizar_metadata(metadata_dict: dict) -> dict:
    """
    Remueve identificadores personales de un diccionario de metadata.

    Elimina claves que contengan informaciÃ³n identificable:
    - patient_id: Identificador Ãºnico del paciente
    - nombre_archivo: Nombre completo de la imagen
    - fecha_registro: Fecha de registro/colecciÃ³n

    Args:
        metadata_dict (dict): Diccionario de metadata del preprocesado

    Returns:
        dict: Metadata anonimizada sin identificadores personales

    Ejemplo:
        >>> metadata = {
        ...     'ruta': 'data/raw/IMG_001.jpg',
        ...     'patient_id': 'P-12345',
        ...     'nombre_archivo': 'IMG_001.jpg',
        ...     'fecha_registro': '2024-03-15',
        ...     'usar_hsv': True,
        ...     'metodo_hsv': 'saturation'
        ... }
        >>> anonimizada = anonimizar_metadata(metadata)
        >>> # patient_id, nombre_archivo, fecha_registro removidos
        >>> print(anonimizada.keys())
        dict_keys(['ruta', 'usar_hsv', 'metodo_hsv'])
    """
    # Claves a remover (identificadores personales)
    claves_remover = {'patient_id', 'nombre_archivo', 'fecha_registro'}

    # Crear nuevo diccionario sin las claves sensibles
    anonimizada = {k: v for k, v in metadata_dict.items() if k not in claves_remover}

    return anonimizada


def obtener_id_sin_identificar(archivo: str) -> str:
    """
    Retorna una versiÃ³n del nombre de archivo sin informaciÃ³n identificable.

    Convierte nombres como 'IMG_001.jpg' o 'paciente_01_cyt01.dat'
    en un formato genÃ©rico 'muestra_XXX'.

    Args:
        archivo (str): Nombre original del archivo

    Returns:
        str: ID anonimizado en formato 'muestra_XXX'

    Ejemplo:
        >>> obtener_id_sin_identificar('IMG_001.jpg')
        'muestra_001'
        >>> obtener_id_sin_identificar('paciente_01_cyt01.dat')
        'muestra_001'
    """
    # Extraer el nÃºmero de muestra del nombre del archivo
    # Buscar patrÃ³n de dÃ­gitos en el nombre
    import re
    match = re.search(r'(\d+)', archivo)
    if match:
        numero = match.group(1)
        return f'muestra_{numero}'
    else:
        # Si no hay nÃºmero, generar ID genÃ©rico
        return 'muestra_001'


def verificar_calidad_imagen(imagen_gris):
    """
    Analiza mÃ©tricas de calidad de la imagen para detectar problemas.

    Esta funciÃ³n ayuda a identificar imÃ¡genes problemÃ¡ticas que pueden
    dar resultados incorrectos en el anÃ¡lisis.

    Args:
        imagen_gris (numpy.ndarray): Imagen en escala de grises

    Returns:
        dict: MÃ©tricas de calidad:
            - 'contraste': Contraste medido (desviaciÃ³n estÃ¡ndar)
            - 'brillo_promedio': Intensidad promedio (0-255)
            - 'saturacion': % de pÃ­xeles saturados (muy oscuros/claros)
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

    # Calcular pÃ­xeles saturados (muy oscuros o muy claros)
    pixels_oscuros = np.sum(imagen_gris < 10)
    pixels_claros = np.sum(imagen_gris > 245)
    total_pixels = imagen_gris.size
    metricas['saturacion'] = ((pixels_oscuros + pixels_claros) / total_pixels) * 100

    # Verificar problemas
    if metricas['contraste'] < 15:
        metricas['advertencias'].append("âš ï¸  Contraste muy bajo (imagen plana)")
        metricas['es_aceptable'] = False

    if metricas['brillo_promedio'] < 30:
        metricas['advertencias'].append("âš ï¸  Imagen muy oscura (subexpuesta)")
    elif metricas['brillo_promedio'] > 225:
        metricas['advertencias'].append("âš ï¸  Imagen muy clara (sobreexpuesta)")

    if metricas['saturacion'] > 10:
        metricas['advertencias'].append(
            f"âš ï¸  {metricas['saturacion']:.1f}% de pÃ­xeles saturados"
        )

    return metricas


def recortar_region_interes(imagen, x, y, ancho, alto):
    """"
    Recorta una regiÃ³n rectangular de la imagen (Ãºtil para anÃ¡lisis focal).

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
    Segmenta nÃºcleos usando el espacio de color HSV.

    Convierte la imagen de BGR a HSV y aplica umbrales en el canal de saturaciÃ³n (S)
    o valor (V) para separar nÃºcleos del citoplasma. Ãštil cuando el contraste de intensidad
    es bajo pero la diferencia de color es significativa.

    Args:
        imagen_bgr (numpy.ndarray): Imagen original en formato BGR (3 canales)
        umbral_sat (int): Umbral mÃ­nimo para el canal de saturaciÃ³n (0-255). Default: 100
        umbral_val (int): Umbral mÃ­nimo para el canal de valor (0-255). Default: 100
        metodo (str): MÃ©todo de umbralizaciÃ³n:
            - 'saturation': Umbralizar en canal S (saturaciÃ³n). Usa cuando los nÃºcleos
              tienen color distinto al citoplasma.
            - 'value': Umbralizar en canal V (brillo/valor). Usa cuando los nÃºcleos son
              mÃ¡s brillos u oscuros que el fondo.

    Returns:
        numpy.ndarray: MÃ¡scara binaria donde blancos = nÃºcleos detectados, negros = fondo

    Ejemplo:
        >>> mask = segmentar_por_hsv(imagen, umbral_sat=80, umbral_val=80, metodo='saturation')
        >>> # Resultado: mÃ¡scara lista para aplicar cv2.findContours()

    Nota:
        - El canal S (saturaciÃ³n) varÃ­a de 0 (gris) a 255 (color puro)
        - El canal V (valor/brillo) varÃ­a de 0 (negro) a 255 (blanco brillante)
        - DespuÃ©s del umbralizado, aplica apertura morfolÃ³gica para eliminar ruido pequeÃ±o
        - La dilataciÃ³n ligera ayuda a conectar regiones nucleares cercanas
    """

    # Convertir de BGR a HSV
    imagen_hsv = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2HSV)

    # Umbralizar segÃºn el mÃ©todo especificado
    if metodo == 'saturation':
        # Usar canal S (saturaciÃ³n): 1 = totalmente desaturado, 255 = color puro
        _, mask = cv2.threshold(imagen_hsv[:, :, 1], umbral_sat, 255, cv2.THRESH_BINARY)
    elif metodo == 'value':
        # Usar canal V (brillo/valor): 0 = negro, 255 = blanco brillante
        _, mask = cv2.threshold(imagen_hsv[:, :, 2], umbral_val, 255, cv2.THRESH_BINARY)
    else:
        raise ValueError(f"MÃ©todo HSV desconocido: {metodo}. "
                        "Usa 'saturation' o 'value'")

    # Aplicar morfologÃ­a abierta para eliminar ruido pequeÃ±o
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Aplicar dilataciÃ³n ligera para conectar regiones cercanas
    mask = cv2.dilate(mask, kernel, iterations=1)

    return mask


    def anonimizar_metadata(metadata_dict: dict) -> dict:
        """
        Remueve identificadores personales de un diccionario de metadata.

        Elimina claves que contengan informaciÃ³n identificable:
        - patient_id: Identificador Ãºnico del paciente
        - nombre_archivo: Nombre completo de la imagen
        - fecha_registro: Fecha de registro/colecciÃ³n

        Args:
            metadata_dict (dict): Diccionario de metadata del preprocesado

        Returns:
            dict: Metadata anonimizada sin identificadores personales

        Ejemplo:
            >>> metadata = {
            ...     'ruta': 'data/raw/IMG_001.jpg',
            ...     'patient_id': 'P-12345',
            ...     'nombre_archivo': 'IMG_001.jpg',
            ...     'fecha_registro': '2024-03-15',
            ...     'usar_hsv': True,
            ...     'metodo_hsv': 'saturation'
            ... }
            >>> anonimizada = anonimizar_metadata(metadata)
            >>> # patient_id, nombre_archivo, fecha_registro removidos
            >>> print(anonimizada.keys())
            dict_keys(['ruta', 'usar_hsv', 'metodo_hsv'])
        """
        # Claves a remover (identificadores personales)
        claves_remover = {'patient_id', 'nombre_archivo', 'fecha_registro'}

        # Crear nuevo diccionario sin las claves sensibles
        anonimizada = {k: v for k, v in metadata_dict.items() if k not in claves_remover}

        return anonimizada


    def obtener_id_sin_identificar(archivo: str) -> str:
        """
        Retorna una versiÃ³n del nombre de archivo sin informaciÃ³n identificable.

        Convierte nombres como 'IMG_001.jpg' o 'paciente_01_cyt01.dat'
        en un formato genÃ©rico 'muestra_XXX'.

        Args:
            archivo (str): Nombre original del archivo

        Returns:
            str: ID anonimizado en formato 'muestra_XXX'

        Ejemplo:
            >>> obtener_id_sin_identificar('IMG_001.jpg')
            'muestra_001'
            >>> obtener_id_sin_identificar('paciente_01_cyt01.dat')
            'muestra_001'
        """
        # Extraer el nÃºmero de muestra del nombre del archivo
        # Buscar patrÃ³n de dÃ­gitos en el nombre
        import re
        match = re.search(r'(\d+)', archivo)
        if match:
            numero = match.group(1)
            return f'muestra_{numero}'
        else:
            # Si no hay nÃºmero, generar ID genÃ©rico
            return 'muestra_001'


