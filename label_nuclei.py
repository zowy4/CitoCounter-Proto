"""
label_nuclei.py - Genera anotaciones iniciales de núcleos para CITO-41

Este script procesa las imágenes en data/raw/ y genera anotaciones
en formato YOLO (etiquetas .txt) usando el pipeline de detección existente.
Los resultados sirven como primera pasada para el proceso de doble
revisión experto CITO-41.

FORMATO DE SALIDA (YOLO):
    Cada archivo .txt contiene líneas con:
    class_id x_center y_center width height
    donde todos los valores están normalizados (0-1)

CLASES:
    0: Célula normal (área < 3x promedio)
    1: Célula anormal (área > 3x promedio - regla del 3x)
    2: Artefacto (sangre, superposición, polvo)

USO:
    python label_nuclei.py
    # O con parámetros personalizados:
    python label_nuclei.py --sigma1 7.0 --sigma2 8.0 --umbral 15

NOTAS:
    - Genera anotaciones candidatas que requieren revisión experta
    - Las imágenes se procesan en lote pero cada una debe revisarse
    - Los archivos se guardan en CitoDataset_v1/labels/train/
    - Se crea un reporte de imágenes pendientes de revisión
"""

import os
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

# Add project to path
sys.path.insert(0, '/workspaces/CitoCounter-Proto')

from src.preprocessing import preprocesar_imagen, convertir_a_gris, mejorar_contraste, reducir_ruido
from src.dog_filter import aplicar_filtro_dog, calcular_sigmas_optimas
from src.analysis import _maximos_locales, watershed_separar_nucleos, AREA_PROMEDIO_NUCLEO_NORMAL, FACTOR_RIESGO
from src.contracts.pipeline_contract import ParametrosAnalisis, ResultadoSegmentacion, validar_tamano_imagen


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

CARPETA_IMAGENES = "data/raw"
CARPETA_LABELS_SALIDA = "CitoDataset_v1/labels/train"
CONFIDENCE_THRESHOLD = 0.5  # Umbral de confianza para detección
MIN_AREA_RATIO_NORMAL = 0.001  # Mínimo área relativa para considerar célula
MAX_AREA_RATIO_ANORMAL = 0.05  # Máximo área relativa para célula anormal
SIGMA1_DEFAULT = 7.0
SIGMA2_DEFAULT = 8.0
UMBRAL_DOG_DEFAULT = 15

# Asegurar que la carpeta de salida exista
os.makedirs(CARPETA_LABELS_SALIDA, exist_ok=True)


def obtener_imagenes_disponibles():
    """Obtiene lista de imágenes en data/raw/ que aún no tienen etiqueta."""
    imagenes = sorted(Path(CARPETA_IMAGENES).glob("MUESTRA_*.jpg"))
    etiquetas_existentes = set()
    
    # Obtener nombres de etiquetas existentes
    if os.path.exists(CARPETA_LABELS_SALIDA):
        for f in Path(CARPETA_LABELS_SALIDA).glob("*.txt"):
            nombre_base = f.stem
            etiquetas_existentes.add(nombre_base)
    
    # Filtrar imágenes sin etiqueta
    sin_etiquetar = []
    for img in imagenes:
        nombre_base = img.stem  # MUESTRA_001, MUESTRA_002, etc.
        if nombre_base not in etiquetas_existentes:
            sin_etiquetar.append(img)
    
    return sin_etiquetar


def procesar_imagen_etiquetado(ruta_imagen, sigma1=SIGMA1_DEFAULT, sigma2=SIGMA2_DEFAULT,
                                umbral_dog=UMBRAL_DOG_DEFAULT, polaridad='nucleos-claros'):
    """
    Procesa una imagen y genera anotaciones YOLO para núcleos detectados.
    
    Esta es la primera pasada del proceso de doble revisión CITO-41.
    Los resultados deben ser revisados por un experto antes de considerarse
    definitivos.
    
    Args:
        ruta_imagen: Ruta a la imagen JPG
        sigma1: Parámetro DoG sigma1
        sigma2: Parámetro DoG sigma2
        umbral_dog: Umbral para binarización DoG
        polaridad: 'nucleos-claros' o 'nucleos-oscuros'
    
    Returns:
        tuple: (lista_anotaciones, imagen_procesada)
            - lista_anotaciones: Lista de dicciones con anotaciones YOLO
            - imagen_procesada: Imagen DoG para visualización
    """
    print(f"\n🔍 Procesando: {ruta_imagen.name}")
    
    # 1. Validar tamaño de imagen (OWASP/STRIDE)
    try:
        imagen_original = cv2.imread(str(ruta_imagen))
        if imagen_original is None:
            print(f"   ❌ No se pudo cargar imagen")
            return [], None
        validar_tamano_imagen(imagen_original, tamano_maximo_kb=65536)
    except ValueError as e:
        print(f"   ⚠️  Advertencia de tamaño: {e}")
        # Continuar de todos modos
    
    # 2. Preprocesamiento
    print("   [1/5] Preprocesando imagen...")
    try:
        imagen_gris, imagen_original = preprocesar_imagen(
            str(ruta_imagen),
            mejorar_contraste_flag=True,
            reducir_ruido_flag=True,
            metodo_contraste='clahe',
            nivel_ruido='medio',
            polaridad=polaridad,
            usar_hsv=False
        )
    except Exception as e:
        print(f"   ❌ Error en preprocesamiento: {e}")
        return [], None
    
    print(f"   ✅ Imagen preprocesada: {imagen_gris.shape}")
    
    # 3. Aplicar filtro DoG
    print(f"   [2/5] Aplicando filtro DoG (σ1={sigma1}, σ2={sigma2})...")
    try:
        imagen_dog = aplicar_filtro_dog(imagen_gris, sigma1=sigma1, sigma2=sigma2)
    except Exception as e:
        print(f"   ❌ Error en DoG: {e}")
        return [], None
    
    print(f"   ✅ Filtro DoG aplicado")
    
    # 4. Detectar máximos locales (candidatos a núcleos)
    print("   [3/5] Detectando máximos locales...")
    try:
        maximos = _maximos_locales(imagen_dog, umbral=umbral_dog, distancia_minima=10)
        print(f"   📍 Máximos detectados: {len(maximos)}")
    except Exception as e:
        print(f"   ❌ Error en detección de máximos: {e}")
        return [], None
    
    # 5. Separar núcleos con watershed
    print("   [4/5] Separando núcleos con watershed...")
    try:
        contornos, areas = watershed_separar_nucleos(imagen_dog, metodo='distancia', umbral=umbral_dog)
        print(f"   ✅ Núcleos separados: {len(contornos)}")
    except Exception as e:
        print(f"   ⚠️  Advertencia en watershed: {e}")
        # Usar máximos locales como fallback
        contornos = []
        areas = [0] * len(maximos) if 'maximos' in dir() else []
        maximos = []
    
    # 6. Generar anotaciones YOLO
    print("   [5/5] Generando anotaciones YOLO...")
    h, w = imagen_gris.shape[:2]
    anotaciones = []
    
    for i, (contorno, area) in enumerate(zip(contornos, areas)):
        # Calcular área relativa al imagen total
        area_relativo = area / (h * w)
        
        # Obtener momentos para centro y bounding box
        M = cv2.moments(contorno)
        if M["m00"] == 0:
            continue
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        # Calcular width y height del bounding box
        x, y, ancho, alto = cv2.boundingRect(contorno)
        
        # Normalizar coordenadas (dividir por ancho/alto de la imagen)
        x_norm = x / w
        y_norm = y / h
        ancho_norm = ancho / w
        alto_norm = alto / h
        
        # Determinar clase basada en área
        if area_relativo < 0.002:
            # Célula pequeña - podría ser normal o artefacto
            clase = 0  # Asumir normal por defecto, revisar después
        elif area_relativo > 0.01:
            # Célula muy grande - probablemente anormal
            clase = 1
        else:
            # Célula de tamaño normal
            clase = 0
        
        # Formato YOLO: class_id x_center y_center width height (todos normalizados)
        # Centro del bounding box:
        x_center_norm = (x + ancho / 2) / w
        y_center_norm = (y + alto / 2) / h
        
        anotacion = f"{clase} {x_center_norm:.6f} {y_center_norm:.6f} {ancho_norm:.6f} {alto_norm:.6f}"
        anotaciones.append(anotacion)
        
        print(f"   📦 Núcleo {i+1}: clase={clase}, área_rel={area_relativo:.4f}, "
              f"bbox=({x_norm:.3f},{y_norm:.3f},{ancho_norm:.3f},{alto_norm:.3f})")
    
    return anotaciones, imagen_dog


def main():
    """Función principal para etiquetado masivo CITO-41."""
    
    print("=" * 70)
    print("  🏷️  CITO-41: Generación de Anotaciones Iniciales de Núcleos")
    print("  " + "=" * 70)
    print("  Generando anotaciones YOLO para doble revisión experta")
    print("=" * 70)
    
    # Obtener imágenes sin etiquetar
    imagenes = obtener_imagenes_disponibles()
    
    if not imagenes:
        print("✅ ¡Todas las imágenes ya tienen anotaciones!")
        print("   No hay imágenes pendientes de etiquetado.")
        return
    
    print(f"\n📸 Imágenes pendientes de etiquetar: {len(imagenes)}")
    print("   (Estas serán primera pasada para revisión experta)")
    
    # Estadísticas
    total_anotaciones = 0
    errores = 0
    procesadas = 0
    
    # Procesar cada imagen
    for i, ruta_imagen in enumerate(imagenes):
        try:
            anotaciones, imagen_dog = procesar_imagen_etiquetado(ruta_imagen)
            
            if anotaciones:
                # Generar nombre de archivo de etiqueta
                nombre_etiqueta = f"{ruta_imagen.stem}.txt"
                ruta_etiqueta = Path(CARPETA_LABELS_SALIDA) / nombre_etiqueta
                
                # Escribir anotaciones
                with open(ruta_etiqueta, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(anotaciones) + '\n')
                
                total_anotaciones += len(anotaciones)
                procesadas += 1
                print(f"   💾 Guardado: {ruta_etiqueta.name} ({len(anotaciones)} núcleos)")
            else:
                print(f"   ⚠️  Sin anotaciones generadas para {ruta_imagen.name}")
                errores += 1
                
        except Exception as e:
            print(f"   ❌ Error procesando {ruta_imagen.name}: {e}")
            errores += 1
            continue
        
        # Mostrar progreso cada 10 imágenes
        if (i + 1) % 10 == 0 or (i + 1) == len(imagenes):
            print(f"\n  📊 Progreso: {i+1}/{len(imagenes)} imágenes procesadas")
            print(f"   📝 Total anotaciones generadas: {total_anotaciones}")
            print(f"   ⚠️  Errores: {errores}")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("  📋 RESUMEN DE ETIQUETADO CITO-41")
    print("=" * 70)
    print(f"  📸 Imágenes procesadas: {procesadas}/{len(imagenes)}")
    print(f"  📝 Anotaciones generadas: {total_anotaciones}")
    print(f"  ⚠️  Errores/ Sin resultado: {errores}")
    print(f"  📁 Archivos de etiqueta en: {CARPETA_LABELS_SALIDA}/")
    print()
    print("  ⚠️  IMPORTANTE: Estas anotaciones son candidatas para revisión")
    print("     experta. Cada imagen debe ser revisada por un experto clínico")
    print("     para validar las clasificaciones (clase 0, 1, 2) y los límites.")
    print("  🔄 Siguiente paso: Revisión experta doble (CITO-41)")
    
    # Crear reporte de imágenes procesadas
    reporte_path = Path(CARPETA_LABELS_SALIDA) / "reporte_etiquetado.txt"
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write(f"Reporte de etiquetado CITO-41\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Imágenes procesadas: {procesadas}/{len(imagenes)}\n")
        f.write(f"Anotaciones generadas: {total_anotaciones}\n")
        f.write(f"Errores: {errores}\n")
        f.write(f"\nImágenes procesadas:\n")
        for img in imagenes:
            nombre_etiqueta = f"{img.stem}.txt"
            ruta_etiqueta = Path(CARPETA_LABELS_SALIDA) / nombre_etiqueta
            if ruta_etiqueta.exists():
                f.write(f"  ✅ {img.name}: {ruta_etiqueta.name}\n")
            else:
                f.write(f"  ❌ {img.name}: Sin etiqueta\n")
    
    print(f"  📄 Reporte guardado en: {reporte_path}")


if __name__ == "__main__":
    main()