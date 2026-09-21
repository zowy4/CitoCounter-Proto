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
from typing import List, Tuple, Optional


# ============================================================================
# PARÁMETROS DE CALIBRACIÓN (Fase 2: Recolección de Datos)
# ============================================================================
# IMPORTANTE: Estos valores son TEMPORALES y deben calibrarse con imágenes reales
# de la Dra. Rangel durante la Fase 2 del proyecto.

AREA_PROMEDIO_NUCLEO_NORMAL = 300  # Píxeles² (¡CALIBRAR CON DATOS REALES!)
FACTOR_RIESGO = 3.0                 # Regla de la Dra. Rangel: >3x = sospechoso
MARGEN_FRONTERA = 0.10              # ±10% alrededor del umbral de riesgo

# Filtros de ruido
AREA_MINIMA_NUCLEO = 50             # Píxeles² - Descartar polvo/ruido
AREA_MAXIMA_NUCLEO = 5000           # Píxeles² - Descartar manchas grandes

# Parámetros de umbralización
UMBRAL_DOG = 15                     # Valor mínimo para considerar un píxel como borde


# Umbrales de área por polaridad (Fase 2.3, CITO-22/23)
# Estos valores fueron ajustados para cada polaridad basándose en el análisis
# de imágenes de prueba. 'nucleos-claros' usa los valores por defecto,
# mientras que 'nucleos-oscuros' requiere umbrales mayores debido a que los
# núcleos aparecen como estructuras más grandes después de la inversión.
AREA_MINIMA_NUCLEO = {
    'nucleos-claros': 50,
    'nucleos-oscuros': 200,
}
AREA_MAXIMA_NUCLEO = {
    'nucleos-claros': 5000,
    'nucleos-oscuros': 300000,
}


# ============================================================================
# FILTRO DE SEPARACIÓN POR WATERSHED (CITO-32 / ACT-10)
# Implementa separación de núcleos superpuestos usando transformada de distancia
# y watershed. Útil para imágenes con núcleos en contacto o superposición.
# ============================================================================

def _maximos_locales(imagen: np.ndarray, umbral: int = UMBRAL_DOG,
                     distancia_minima: int = 10) -> List[Tuple[int, int]]:
    """
    Detecta máximos locales en una imagen usando thresholding y detección de picos.
    
    Args:
        imagen: Imagen DoG (8-bit) donde detectar máximos
        umbral: Umbral de binarización (se usa Otsu si es 0)
        distancia_minima: Distancia mínima entre picos para evitar detecciones redundantes
    
    Returns:
        Lista de (x, y) coordenadas de los máximos locales detectados
    """
    # Binarización con Otsu
    _, binaria = cv2.threshold(imagen, umbral, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Transformada de distancia sobre los píxeles blancos
    dist_transform = cv2.distanceTransform(binaria, cv2.DIST_L2, 5)
    
    # Non-maximum suppression para encontrar picos
    # Umbralizar la distancia para obtener solo los picos más prominentes
    _, picos = cv2.threshold(dist_transform, 0.1 * dist_transform.max(), 255, cv2.THRESH_BINARY)
    
    # Encontrar contornos de los picos
    contornos_picos, _ = cv2.findContours(picos.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Obtener centros de los contornos
    maximos = []
    for c in contornos_picos:
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m01"])
            maximos.append((cx, cy))
    
    # Aplicar filtrado de distancia mínima entre picos
    maximos_filtrados = []
    for (x, y) in maximos:
        # Verificar si este pico está muy cerca de uno ya seleccionado
        muy_cercano = False
        for (x0, y0) in maximos_filtrados:
            if np.sqrt((x - x0)**2 + (y - y0)**2) < distancia_minima:
                muy_cercano = True
                break
        if not muy_cercano:
            maximos_filtrados.append((x, y))
    
    return maximos_filtrados


def watershed_separar_nucleos(imagen_dog: np.ndarray, metodo: str = 'distancia',
                              umbral: int = UMBRAL_DOG,
                              distancia_minima: int = 10) -> Tuple[List[np.ndarray], List[int]]:
    """
    Separa núcleos superpuestos usando watershed (transformada de distancia + watershed).
    
    Args:
        imagen_dog: Imagen procesada con filtro DoG (8-bit)
        metodo: Método de separación ('distancia' o 'gradiente')
        umbral: Umbral de binarización para el watershed
        distancia_minima: Distancia mínima entre núcleos separados
    
    Returns:
        Tupla con:
        - Lista de contornos de núcleos separados
        - Lista de áreas de cada núcleo
    """
    # Binarización
    _, binaria = cv2.threshold(imagen_dog, umbral, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    if metodo == 'distancia':
        # Usar transformada de distancia + watershed
        dist_transform = cv2.distanceTransform(binaria, cv2.DIST_L2, 5)
        
        # Aplicar watershed
        # Marcadores: píxeles oscuros (fondo) = 0, píxeles blancos = 1, ... 
        # Los picos de la transformada de distancia serán los centros de los núcleos
        _, marcadores = cv2.connectedComponents(binaria.astype(np.uint8))
        marcadores = marcadores.astype(np.int32) + 1  # Fondo = 1
        
        # Aplicar watershed
        # Convertir imagen_dog a 8-bit 3-channel para watershed
        # Normalizar y convertir a uint8
        imagen_8bit = cv2.normalize(imagen_dog, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        # Convertir a 3 canales si es necesario
        if len(imagen_8bit.shape) == 2:
            imagen_8bit = cv2.cvtColor(imagen_8bit, cv2.COLOR_GRAY2BGR)
        
        marcadores = cv2.watershed(imagen_8bit, marcadores)
        marcadores[marcadores == -1] = 0  # Fronteras = 0
        
        # Obtener contornos de cada región segmentada
        nuclei_contours = []
        areas = []
        for label in range(2, marcadores.max() + 1):
            mask = np.zeros_like(marcadores, dtype=np.uint8)
            mask[marcadores == label] = 255
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                # Tomar el contorno más grande (el núcleo)
                largest_contour = max(contours, key=cv2.contourArea)
                nuclei_contours.append(largest_contour)
                areas.append(cv2.contourArea(largest_contour))
    
    elif metodo == 'gradiente':
        # Método alternativo usando gradientes
        gradientes = cv2.Canny(imagen_dog, 50, 150)
        _, marcadores = cv2.connectedComponents(gradientes.astype(np.uint8))
        marcadores = marcadores.astype(np.int32) + 1
        # Convertir imagen_dog a 8-bit 3-channel para watershed
        imagen_8bit = cv2.normalize(imagen_dog, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        # Convertir a 3 canales si es necesario
        if len(imagen_8bit.shape) == 2:
            imagen_8bit = cv2.cvtColor(imagen_8bit, cv2.COLOR_GRAY2BGR)
        marcadores = cv2.watershed(imagen_8bit, marcadores)
        marcadores[marcadores == -1] = 0
        
        nuclei_contours = []
        areas = []
        for label in range(2, marcadores.max() + 1):
            mask = np.zeros_like(marcadores, dtype=np.uint8)
            mask[marcadores == label] = 255
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                nuclei_contours.append(largest_contour)
                areas.append(cv2.contourArea(largest_contour))
    
    else:
        raise ValueError(f"Método '{metodo}' no reconocido. Use 'distancia' o 'gradiente'.")
    
    return nuclei_contours, areas


def obtener_reglas_clasificacion(polaridad: str = 'nucleos-claros'):
    """
    Devuelve las reglas activas de clasificación para CITO-24.
    
    Args:
        polaridad: 'nucleos-claros' o 'nucleos-oscuros'
    
    Returns:
        dict con las reglas de clasificación ajustadas para la polaridad especificada
    """
    # Usar umbrales de área específicos para la polaridad
    area_min = AREA_MINIMA_NUCLEO[polaridad]
    area_max = AREA_MAXIMA_NUCLEO[polaridad]
    
    umbral_sospechoso = AREA_PROMEDIO_NUCLEO_NORMAL * FACTOR_RIESGO
    return {
        "area_minima_nucleo": area_min,
        "area_maxima_nucleo": area_max,
        "area_promedio_nucleo_normal": AREA_PROMEDIO_NUCLEO_NORMAL,
        "factor_riesgo": FACTOR_RIESGO,
        "umbral_sospechoso": umbral_sospechoso,
        "limite_frontera_inferior": umbral_sospechoso * (1.0 - MARGEN_FRONTERA),
        "limite_frontera_superior": umbral_sospechoso * (1.0 + MARGEN_FRONTERA),
    }


def clasificar_nucleo_por_area(area, polaridad: str = 'nucleos-claros'):
    """
    Clasifica un núcleo por área con reglas explicables.

    Retorna:
        dict con claves:
        - es_valida (bool): Si el área entra en rango analizable.
        - clasificacion (str): descartada|normal|sospechosa
        - es_frontera (bool): Si cae en la zona ±10% alrededor del umbral.
        - umbral_sospechoso (float): Umbral actual usado para la decisión.
        - motivo (str): Explicación legible de la decisión.
    """
    reglas = obtener_reglas_clasificacion(polaridad)
    area_min = reglas["area_minima_nucleo"]
    area_max = reglas["area_maxima_nucleo"]
    umbral = reglas["umbral_sospechoso"]
    lim_inf = reglas["limite_frontera_inferior"]
    lim_sup = reglas["limite_frontera_superior"]

    if area < area_min:
        return {
            "es_valida": False,
            "clasificacion": "descartada",
            "es_frontera": False,
            "umbral_sospechoso": umbral,
            "motivo": "Área menor al mínimo permitido (ruido)",
        }

    if area > area_max:
        return {
            "es_valida": False,
            "clasificacion": "descartada",
            "es_frontera": False,
            "umbral_sospechoso": umbral,
            "motivo": "Área mayor al máximo permitido (artefacto)",
        }

    es_frontera = lim_inf <= area <= lim_sup
    if area >= umbral:
        return {
            "es_valida": True,
            "clasificacion": "sospechosa",
            "es_frontera": es_frontera,
            "umbral_sospechoso": umbral,
            "motivo": f"Área >= umbral de riesgo ({umbral:.1f}px²)",
        }

    return {
        "es_valida": True,
        "clasificacion": "normal",
        "es_frontera": es_frontera,
        "umbral_sospechoso": umbral,
        "motivo": f"Área < umbral de riesgo ({umbral:.1f}px²)",
    }


def analizar_nucleos(imagen_dog, imagen_original, mostrar_debug=False, polaridad='nucleos-claros', metodo_separacion: str = None):
    """
    Analiza una imagen DoG para detectar y clasificar núcleos celulares.
    
    Pipeline de análisis:
    1. Binarización (convertir a blanco/negro)
    2. Detección de contornos (encontrar núcleos individuales)
    3. Filtrado de ruido (eliminar artefactos)
    4. Clasificación según regla del 3x
    5. Opcional: Separación de núcleos superpuestos usando watershed
    6. Anotación visual (semáforo verde/rojo)
    
    Args:
        imagen_dog (numpy.ndarray): Imagen procesada con filtro DoG (8-bit)
        imagen_original (numpy.ndarray): Imagen RGB original para anotar
        mostrar_debug (bool): Si True, incluye información de depuración
        polaridad (str): 'nucleos-claros' o 'nucleos-oscuros' (default: 'nucleos-claros')
        metodo_separacion: Método de separación de núcleos superpuestos.
            - None: Sin separación (comportamiento original)
            - 'watershed': Separación usando watershed (transformada de distancia)
            - 'maximos_locales': Detección de máximos locales
    
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
        "frontera": 0,
        "porcentaje_riesgo": 0.0,
        "imagen_procesada": imagen_original.copy(),
        "areas": [],
        "criterios_clasificacion": [],
        "contornos_normales": [],
        "contornos_sospechosos": []
    }
    
    # 3. SEPARACIÓN DE NÚCLEOS SUPERPUestos (opcional)
    if metodo_separacion == 'watershed':
        contornos, areas = watershed_separar_nucleos(imagen_dog, metodo='distancia')
        # Reconstruir resultados a partir de la separación watershed
        for i, (contorno, area) in enumerate(zip(contornos, areas)):
            decision = clasificar_nucleo_por_area(area, polaridad)
            if not decision["es_valida"]:
                continue
            
            # Es un núcleo válido
            resultados["total_celulas"] += 1
            resultados["areas"].append(area)
            
            if decision["clasificacion"] == "sospechosa":
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
            
            resultados["criterios_clasificacion"].append({
                "area": area,
                "es_frontera": decision["es_frontera"],
                "motivo": decision["motivo"],
            })
    
    elif metodo_separacion == 'maximos_locales':
        # Usar detección de máximos locales
        maximos = _maximos_locales(imagen_dog, umbral=UMBRAL_DOG)
        
        # Para cada máximo, obtener el área usando contour area del área alrededor
        for (cx, cy) in maximos:
            # Crear una máscara pequeña alrededor del máximo
            mask = np.zeros(imagen_dog.shape, dtype=np.uint8)
            cv2.circle(mask, (cx, cy), 15, 255, -1)
            masked_dog = cv2.bitwise_and(imagen_dog, imagen_dog, mask=mask)
            _, thresh = cv2.threshold(masked_dog, UMBRAL_DOG, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                
                decision = clasificar_nucleo_por_area(area, polaridad)
                if not decision["es_valida"]:
                    continue
                
                # Es un núcleo válido
                resultados["total_celulas"] += 1
                resultados["areas"].append(area)
                
                if decision["clasificacion"] == "sospechosa":
                    color = (0, 0, 255)  # ROJO en BGR
                    etiqueta = "RIESGO"
                    resultados["sospechosas"] += 1
                    resultados["contornos_sospechosos"].append(largest_contour)
                else:
                    # --- CÉLULA NORMAL ---
                    color = (0, 255, 0)  # VERDE en BGR
                    etiqueta = "NORMAL"
                    resultados["normales"] += 1
                    resultados["contornos_normales"].append(largest_contour)
                
                resultados["criterios_clasificacion"].append({
                    "area": area,
                    "es_frontera": decision["es_frontera"],
                    "motivo": decision["motivo"],
                })
    
    else:
        # Sin separación: comportamiento original (contornos detectados directamente)
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            
            # Filtrar por circularidad y aspecto para eliminar ruido
            # (solo para polaridad nucleos-oscuros donde hay más ruido)
            if polaridad == 'nucleos-oscuros':
                perimetro = cv2.arcLength(contorno, True)
                if perimetro > 0:
                    circularidad = 4 * np.pi * area / (perimetro ** 2)
                    if circularidad < 0.3:  # Filtrar formas muy irregulares (ruido)
                        continue
                
                # Filtrar por aspecto (relación ancho/alto)
                x, y, w, h = cv2.boundingRect(contorno)
                if w > 0 and h > 0:
                    aspecto = max(w, h) / min(w, h)
                    if aspecto > 3.0:  # Filtrar formas muy alargadas (artefactos)
                        continue
                
                # Filtrar por tamaño (artefactos muy pequeños o grandes)
                # Área mínima: evita detectar ruido de fondo
                # Área máxima: evita detectar manchas de tinción grandes o polvo
                area = cv2.contourArea(contorno)
                if area < AREA_MINIMA_NUCLEO[polaridad] * 0.1:
                    continue
                if area > AREA_MAXIMA_NUCLEO[polaridad] * 5:
                    continue
            
            area = cv2.contourArea(contorno)
            
            decision = clasificar_nucleo_por_area(area, polaridad)
            if not decision["es_valida"]:
                continue
    
    # 4. CLASSIFICATION (continuación del comportamiento original)
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        
        decision = clasificar_nucleo_por_area(area, polaridad)
        if not decision["es_valida"]:
            continue
        
        # Es un núcleo válido
        resultados["total_celulas"] += 1
        resultados["areas"].append(area)
        
        if decision["clasificacion"] == "sospechosa":
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
        
        resultados["criterios_clasificacion"].append({
            "area": area,
            "es_frontera": decision["es_frontera"],
            "motivo": decision["motivo"],
        })
        
        # Es un núcleo válido
        resultados["total_celulas"] += 1
        resultados["areas"].append(area)
        
        # Obtener caja delimitadora (bounding box)
        x, y, w, h = cv2.boundingRect(contorno)
        
        if decision["es_frontera"]:
            resultados["frontera"] += 1

        if decision["clasificacion"] == "sospechosa":
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

        resultados["criterios_clasificacion"].append({
            "area": float(area),
            "clasificacion": decision["clasificacion"],
            "es_frontera": decision["es_frontera"],
            "umbral_sospechoso": decision["umbral_sospechoso"],
            "motivo": decision["motivo"],
        })
        
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
    reporte.append(f"  • Casos frontera (±10%):    {resultados.get('frontera', 0)}")
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
