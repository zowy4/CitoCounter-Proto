"""
analysis.py - Análisis y Clasificación de Núcleos Celulares

Implementa la lógica de la Dra. Rangel:
"Núcleos con área > 3x el tamaño promedio normal son sospechosos"

Este módulo contiene la inteligencia del sistema:
1. Segmentación (detección de núcleos individuales)
2. Filtrado de ruido (descartar artefactos)
3. Clasificación (aplicar regla del 3x)
"""

import cv2
import numpy as np


# ============================================================================
# PARÁMETROS DE CALIBRACIÓN (Fase 2: Recolección de Datos)
# ============================================================================
# IMPORTANTE: Estos valores son TEMPORALES y deben calibrarse con imágenes reales
# de la Dra. Rangel durante la Fase 2 del proyecto.

AREA_PROMEDIO_NUCLEO_NORMAL = 300  # Píxeles² (¡CALIBRAR CON DATOS REALES!)
FACTOR_RIESGO = 3.0                 # Regla de la Dra. Rangel: >3x = sospechoso

# Filtros de ruido
AREA_MINIMA_NUCLEO = 50             # Píxeles² - Descartar polvo/ruido
AREA_MAXIMA_NUCLEO = 5000           # Píxeles² - Descartar manchas grandes

# Parámetros de umbralización
UMBRAL_DOG = 15                     # Valor mínimo para considerar un píxel como borde


def analizar_nucleos(imagen_dog, imagen_original, mostrar_debug=False):
    """
    Analiza una imagen DoG para detectar y clasificar núcleos celulares.
    
    Pipeline de análisis:
    1. Binarización (convertir a blanco/negro)
    2. Detección de contornos (encontrar núcleos individuales)
    3. Filtrado de ruido (eliminar artefactos)
    4. Clasificación según regla del 3x
    5. Anotación visual (semáforo verde/rojo)
    
    Args:
        imagen_dog (numpy.ndarray): Imagen procesada con filtro DoG (8-bit)
        imagen_original (numpy.ndarray): Imagen RGB original para anotar
        mostrar_debug (bool): Si True, incluye información de depuración
    
    Returns:
        dict: Resultados del análisis con las siguientes claves:
            - 'total_celulas': Número total de núcleos detectados
            - 'normales': Número de núcleos normales (área < 3x)
            - 'sospechosas': Número de núcleos sospechosos (área >= 3x)
            - 'porcentaje_riesgo': % de células sospechosas
            - 'imagen_procesada': Imagen con anotaciones visuales
            - 'areas': Lista de áreas detectadas (para análisis posterior)
            - 'contornos_normales': Lista de contornos normales
            - 'contornos_sospechosos': Lista de contornos sospechosos
    """
    
    # 1. BINARIZACIÓN
    # Método de Otsu: calcula automáticamente el umbral óptimo
    # THRESH_BINARY: píxeles > umbral = 255 (blanco), resto = 0 (negro)
    _, thresh = cv2.threshold(
        imagen_dog, 
        UMBRAL_DOG, 
        255, 
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    
    # 2. DETECCIÓN DE CONTORNOS
    # RETR_EXTERNAL: solo contornos externos (ignora huecos internos)
    # CHAIN_APPROX_SIMPLE: comprime segmentos rectos (ahorra memoria)
    contornos, _ = cv2.findContours(
        thresh, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    # Inicializar estructura de resultados
    resultados = {
        "total_celulas": 0,
        "normales": 0,
        "sospechosas": 0,
        "porcentaje_riesgo": 0.0,
        "imagen_procesada": imagen_original.copy(),
        "areas": [],
        "contornos_normales": [],
        "contornos_sospechosos": []
    }
    
    # 3. ANÁLISIS DE CADA CONTORNO DETECTADO
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        
        # FILTRO DE RUIDO: Descartar objetos demasiado pequeños o grandes
        if area < AREA_MINIMA_NUCLEO or area > AREA_MAXIMA_NUCLEO:
            continue
        
        # Es un núcleo válido
        resultados["total_celulas"] += 1
        resultados["areas"].append(area)
        
        # Obtener caja delimitadora (bounding box)
        x, y, w, h = cv2.boundingRect(contorno)
        
        # ====================================================================
        # APLICACIÓN DE LA REGLA DE LA DRA. RANGEL
        # "Núcleos con área > 3 veces el promedio normal son sospechosos"
        # ====================================================================
        umbral_sospechoso = AREA_PROMEDIO_NUCLEO_NORMAL * FACTOR_RIESGO
        
        if area >= umbral_sospechoso:
            # --- CÉLULA SOSPECHOSA ---
            color = (0, 0, 255)  # ROJO en BGR
            etiqueta = "RIESGO"
            resultados["sospechosas"] += 1
            resultados["contornos_sospechosos"].append(contorno)
            
        else:
            # --- CÉLULA NORMAL ---
            color = (0, 255, 0)  # VERDE en BGR
            etiqueta = "NORMAL"
            resultados["normales"] += 1
            resultados["contornos_normales"].append(contorno)
        
        # 4. ANOTACIÓN VISUAL
        # Dibujar rectángulo alrededor del núcleo
        cv2.rectangle(
            resultados["imagen_procesada"], 
            (x, y), 
            (x + w, y + h), 
            color, 
            2
        )
        
        # Agregar etiqueta de texto
        cv2.putText(
            resultados["imagen_procesada"], 
            etiqueta, 
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.4, 
            color, 
            1
        )
        
        # Información adicional de depuración (opcional)
        if mostrar_debug:
            texto_area = f"{int(area)}px"
            cv2.putText(
                resultados["imagen_procesada"], 
                texto_area, 
                (x, y + h + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.3, 
                color, 
                1
            )
    
    # 5. CALCULAR PORCENTAJE DE RIESGO
    if resultados["total_celulas"] > 0:
        resultados["porcentaje_riesgo"] = (
            resultados["sospechosas"] / resultados["total_celulas"]
        ) * 100.0
    
    return resultados


def calibrar_area_promedio(lista_imagenes_normales):
    """
    Calcula el área promedio de núcleos normales a partir de un conjunto de imágenes.
    
    Esta función debe ejecutarse durante la FASE 2 (Recolección de Datos)
    con imágenes anotadas por la Dra. Rangel como "100% normales".
    
    Args:
        lista_imagenes_normales (list): Lista de imágenes DoG de muestras normales
    
    Returns:
        float: Área promedio en píxeles²
        
    Uso:
        # Durante la calibración
        area_calibrada = calibrar_area_promedio(imagenes_de_control)
        # Luego actualizar AREA_PROMEDIO_NUCLEO_NORMAL con este valor
    """
    todas_las_areas = []
    
    for imagen_dog in lista_imagenes_normales:
        _, thresh = cv2.threshold(imagen_dog, UMBRAL_DOG, 255, 
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 
                                        cv2.CHAIN_APPROX_SIMPLE)
        
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            if AREA_MINIMA_NUCLEO < area < AREA_MAXIMA_NUCLEO:
                todas_las_areas.append(area)
    
    if len(todas_las_areas) == 0:
        raise ValueError("No se detectaron núcleos válidos en las imágenes de control")
    
    area_promedio = np.mean(todas_las_areas)
    desviacion_std = np.std(todas_las_areas)
    
    print(f"📊 CALIBRACIÓN COMPLETADA:")
    print(f"   - Núcleos analizados: {len(todas_las_areas)}")
    print(f"   - Área promedio: {area_promedio:.2f} ± {desviacion_std:.2f} px²")
    print(f"   - Rango típico: [{area_promedio - desviacion_std:.1f}, "
          f"{area_promedio + desviacion_std:.1f}] px²")
    
    return area_promedio


def generar_reporte_estadistico(resultados):
    """
    Genera un reporte estadístico textual del análisis.
    
    Args:
        resultados (dict): Diccionario de resultados de analizar_nucleos()
    
    Returns:
        str: Reporte formateado para consola/archivo
    """
    reporte = []
    reporte.append("=" * 60)
    reporte.append("REPORTE DE ANÁLISIS - CitoCounter Proto")
    reporte.append("=" * 60)
    reporte.append(f"Total de células detectadas: {resultados['total_celulas']}")
    reporte.append(f"  • Células normales:         {resultados['normales']}")
    reporte.append(f"  • Células sospechosas:      {resultados['sospechosas']}")
    reporte.append(f"  • Porcentaje de riesgo:     {resultados['porcentaje_riesgo']:.1f}%")
    reporte.append("-" * 60)
    
    if resultados['areas']:
        areas = np.array(resultados['areas'])
        reporte.append(f"Estadísticas de áreas:")
        reporte.append(f"  • Área mínima:   {np.min(areas):.1f} px²")
        reporte.append(f"  • Área máxima:   {np.max(areas):.1f} px²")
        reporte.append(f"  • Área promedio: {np.mean(areas):.1f} px²")
        reporte.append(f"  • Desv. estándar: {np.std(areas):.1f} px²")
    
    reporte.append("=" * 60)
    
    return "\n".join(reporte)
