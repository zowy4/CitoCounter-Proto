"""
visualization.py - Visualización y Generación de Reportes

Este módulo maneja toda la presentación visual de resultados:
1. Anotación de imágenes (círculos, cajas, etiquetas)
2. Creación de paneles comparativos (antes/después)
3. Generación de gráficos estadísticos
4. Exportación de imágenes procesadas
"""

import cv2
import numpy as np
import os
from datetime import datetime


def crear_panel_comparativo(imagenes_dict, titulos_dict, filas=2, columnas=2):
    """
    Crea un panel comparativo tipo mosaico con múltiples imágenes.
    
    Útil para mostrar el pipeline completo:
    - Original | Escala de Grises
    - Filtro DoG | Resultado Final
    
    Args:
        imagenes_dict (dict): Diccionario {clave: imagen_numpy}
        titulos_dict (dict): Diccionario {clave: titulo_texto}
        filas (int): Número de filas en el mosaico
        columnas (int): Número de columnas en el mosaico
    
    Returns:
        numpy.ndarray: Imagen compuesta con todas las vistas
    
    Ejemplo:
        imagenes = {
            'original': img_original,
            'gris': img_gris,
            'dog': img_dog,
            'resultado': img_resultado
        }
        titulos = {
            'original': 'Original',
            'gris': 'Escala de Grises',
            'dog': 'Filtro DoG',
            'resultado': 'Detección'
        }
        panel = crear_panel_comparativo(imagenes, titulos, 2, 2)
    """
    
    claves = list(imagenes_dict.keys())[:filas * columnas]
    
    # Determinar tamaño común para todas las imágenes
    altura_ref, ancho_ref = list(imagenes_dict.values())[0].shape[:2]
    
    # Preparar imágenes (redimensionar y convertir a BGR si es necesario)
    imagenes_procesadas = []
    for clave in claves:
        img = imagenes_dict[clave]
        
        # Redimensionar si es necesario
        if img.shape[:2] != (altura_ref, ancho_ref):
            img = cv2.resize(img, (ancho_ref, altura_ref))
        
        # Convertir a BGR si es escala de grises
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
        # Agregar título
        img_con_titulo = img.copy()
        cv2.putText(
            img_con_titulo,
            titulos_dict[clave],
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        cv2.putText(
            img_con_titulo,
            titulos_dict[clave],
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 0),
            1,
            cv2.LINE_AA
        )
        
        imagenes_procesadas.append(img_con_titulo)
    
    # Crear filas
    filas_img = []
    for i in range(filas):
        inicio = i * columnas
        fin = inicio + columnas
        fila_imagenes = imagenes_procesadas[inicio:fin]
        
        # Rellenar con imágenes negras si faltan
        while len(fila_imagenes) < columnas:
            fila_imagenes.append(np.zeros_like(imagenes_procesadas[0]))
        
        fila_concatenada = np.hstack(fila_imagenes)
        filas_img.append(fila_concatenada)
    
    # Concatenar todas las filas
    panel_final = np.vstack(filas_img)
    
    return panel_final


def dibujar_estadisticas_en_imagen(imagen, resultados, posicion='inferior'):
    """
    Agrega un cuadro de texto con estadísticas sobre la imagen.
    
    Args:
        imagen (numpy.ndarray): Imagen BGR donde dibujar
        resultados (dict): Diccionario de resultados de analysis.py
        posicion (str): 'superior' o 'inferior'
    
    Returns:
        numpy.ndarray: Imagen con estadísticas dibujadas
    """
    
    img_anotada = imagen.copy()
    altura, ancho = img_anotada.shape[:2]
    
    # Crear rectángulo semitransparente para el texto
    overlay = img_anotada.copy()
    
    # Definir posición del cuadro de estadísticas
    margen = 10
    altura_cuadro = 120
    
    if posicion == 'inferior':
        y1 = altura - altura_cuadro - margen
        y2 = altura - margen
    else:  # superior
        y1 = margen
        y2 = margen + altura_cuadro
    
    cv2.rectangle(overlay, (margen, y1), (ancho - margen, y2), 
                  (0, 0, 0), -1)
    
    # Mezclar con transparencia
    alpha = 0.7
    cv2.addWeighted(overlay, alpha, img_anotada, 1 - alpha, 0, img_anotada)
    
    # Agregar texto
    lineas_texto = [
        f"Total Celulas: {resultados['total_celulas']}",
        f"Normales: {resultados['normales']} (VERDE)",
        f"Sospechosas: {resultados['sospechosas']} (ROJO)",
        f"% Riesgo: {resultados['porcentaje_riesgo']:.1f}%"
    ]
    
    y_texto = y1 + 25
    for linea in lineas_texto:
        cv2.putText(
            img_anotada,
            linea,
            (margen + 10, y_texto),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        y_texto += 28
    
    return img_anotada


def guardar_imagen_resultado(imagen, nombre_archivo, carpeta_salida='data/results'):
    """
    Guarda una imagen procesada con timestamp.
    
    Args:
        imagen (numpy.ndarray): Imagen a guardar
        nombre_archivo (str): Nombre base del archivo
        carpeta_salida (str): Carpeta donde guardar
    
    Returns:
        str: Ruta completa del archivo guardado
    """
    
    # Crear carpeta si no existe
    os.makedirs(carpeta_salida, exist_ok=True)
    
    # Agregar timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base, extension = os.path.splitext(nombre_archivo)
    nombre_completo = f"{nombre_base}_{timestamp}{extension}"
    
    ruta_completa = os.path.join(carpeta_salida, nombre_completo)
    
    cv2.imwrite(ruta_completa, imagen)
    
    return ruta_completa


def crear_vista_deteccion(imagen_original, contornos_normales, 
                          contornos_sospechosos, dibujar_contornos=True):
    """
    Crea una visualización detallada de las detecciones.
    
    Args:
        imagen_original (numpy.ndarray): Imagen BGR original
        contornos_normales (list): Lista de contornos de células normales
        contornos_sospechosos (list): Lista de contornos de células sospechosas
        dibujar_contornos (bool): Si True, dibuja contornos; si False, solo cajas
    
    Returns:
        numpy.ndarray: Imagen con visualización de detecciones
    """
    
    img_deteccion = imagen_original.copy()
    
    # Dibujar células normales (VERDE)
    for contorno in contornos_normales:
        if dibujar_contornos:
            cv2.drawContours(img_deteccion, [contorno], -1, (0, 255, 0), 2)
        else:
            x, y, w, h = cv2.boundingRect(contorno)
            cv2.rectangle(img_deteccion, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Dibujar células sospechosas (ROJO)
    for contorno in contornos_sospechosos:
        if dibujar_contornos:
            cv2.drawContours(img_deteccion, [contorno], -1, (0, 0, 255), 3)
        else:
            x, y, w, h = cv2.boundingRect(contorno)
            cv2.rectangle(img_deteccion, (x, y), (x+w, y+h), (0, 0, 255), 3)
        
        # Agregar marcador de alerta para sospechosas
        x, y, w, h = cv2.boundingRect(contorno)
        cv2.putText(
            img_deteccion,
            "!",
            (x + w - 15, y + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )
    
    return img_deteccion


def mostrar_ventanas_analisis(imagenes_dict, esperar_tecla=True):
    """
    Muestra múltiples ventanas para análisis interactivo.
    
    Args:
        imagenes_dict (dict): Diccionario {nombre_ventana: imagen}
        esperar_tecla (bool): Si True, espera a que se presione una tecla
    
    Ejemplo:
        ventanas = {
            'Original': img_original,
            'DoG Filter': img_dog,
            'Resultado': img_resultado
        }
        mostrar_ventanas_analisis(ventanas)
    """
    
    for nombre_ventana, imagen in imagenes_dict.items():
        cv2.imshow(nombre_ventana, imagen)
    
    if esperar_tecla:
        print("Presiona cualquier tecla para cerrar las ventanas...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def crear_mapa_calor_areas(imagen_original, lista_contornos, lista_areas):
    """
    Crea un mapa de calor donde el color indica el tamaño del núcleo.
    
    Azul = pequeño, Verde = normal, Amarillo = grande, Rojo = muy grande
    
    Args:
        imagen_original (numpy.ndarray): Imagen BGR de fondo
        lista_contornos (list): Lista de todos los contornos detectados
        lista_areas (list): Lista de áreas correspondientes
    
    Returns:
        numpy.ndarray: Imagen con mapa de calor
    """
    
    img_calor = imagen_original.copy()
    
    if len(lista_areas) == 0:
        return img_calor
    
    # Normalizar áreas al rango 0-1
    areas_array = np.array(lista_areas)
    area_min = np.min(areas_array)
    area_max = np.max(areas_array)
    
    if area_max == area_min:
        areas_norm = np.ones_like(areas_array) * 0.5
    else:
        areas_norm = (areas_array - area_min) / (area_max - area_min)
    
    # Dibujar cada contorno con color según su área
    for contorno, area_norm in zip(lista_contornos, areas_norm):
        # Convertir área normalizada a color (usando HSV)
        # Hue: 120 (verde) para pequeño, 0 (rojo) para grande
        hue = int(120 * (1 - area_norm))  # 120 -> 0 (verde -> rojo)
        color_hsv = np.uint8([[[hue, 255, 255]]])
        color_bgr = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2BGR)[0][0]
        color_bgr = (int(color_bgr[0]), int(color_bgr[1]), int(color_bgr[2]))
        
        cv2.drawContours(img_calor, [contorno], -1, color_bgr, -1)  # Relleno
        cv2.drawContours(img_calor, [contorno], -1, (255, 255, 255), 1)  # Borde
    
    # Agregar leyenda
    cv2.putText(img_calor, "Mapa de Calor - Tamano Nucleos", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(img_calor, "Azul=Pequeno | Verde=Normal | Rojo=Grande", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return img_calor


def agregar_escala_referencia(imagen, pixeles_por_micron, longitud_barra_um=50):
    """
    Agrega una barra de escala a la imagen (si se conoce la calibración).
    
    Args:
        imagen (numpy.ndarray): Imagen donde agregar la escala
        pixeles_por_micron (float): Factor de conversión px/μm
        longitud_barra_um (int): Longitud de la barra en micrómetros
    
    Returns:
        numpy.ndarray: Imagen con barra de escala
    """
    
    img_con_escala = imagen.copy()
    altura, ancho = img_con_escala.shape[:2]
    
    # Calcular longitud en píxeles
    longitud_barra_px = int(longitud_barra_um * pixeles_por_micron)
    
    # Posición de la barra (esquina inferior derecha)
    margen = 20
    x1 = ancho - longitud_barra_px - margen
    x2 = ancho - margen
    y = altura - margen - 10
    
    # Dibujar barra
    cv2.line(img_con_escala, (x1, y), (x2, y), (255, 255, 255), 3)
    cv2.line(img_con_escala, (x1, y), (x2, y), (0, 0, 0), 1)
    
    # Agregar etiqueta
    texto = f"{longitud_barra_um} um"
    cv2.putText(img_con_escala, texto, (x1, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(img_con_escala, texto, (x1, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    return img_con_escala
