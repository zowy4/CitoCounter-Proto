#!/usr/bin/env python3
"""
fix_labels.py - Genera anotaciones correctas para imágenes con diagnósticos anormales

Este script:
1. Usa el pipeline CitoCounter para detectar núcleos en imágenes de validación/test
2. Para imágenes con diagnóstico anormal (LSIL, HSIL, ASC-US, ASC-H), clasifica núcleos grandes como clase 1
3. Para imágenes con diagnóstico NEGATIVO, clasifica todos como clase 0
4. Actualiza los archivos de etiquetas en CitoDataset_v1/labels/val y test
"""

import cv2
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from preprocessing import preprocesar_imagen, verificar_calidad_imagen
from dog_filter import aplicar_filtro_dog
from analysis import analizar_nucleos, obtener_reglas_clasificacion, AREA_PROMEDIO_NUCLEO_NORMAL, FACTOR_RIESGO

# Configuración
RAW_DIR = Path('data/raw')
LABELS_VAL = Path('CitoDataset_v1/labels/val')
LABELS_TEST = Path('CitoDataset_v1/labels/test')
METADATA_CSV = Path('CitoDataset_v1/metadata/clinical_data_synthetic.csv')

# Diagnósticos anormales
DIAGNOSTICOS_ANORMALES = {'LSIL', 'HSIL', 'ASC-US', 'ASC-H'}

# Parámetros del pipeline (usar los calibrados)
SIGMA1 = 3.0
SIGMA2 = 5.0
POLARIDAD = 'nucleos-claros'
USAR_CLAHE = True
REDUCIR_RUIDO = False


def obtener_diagnostico(imagen_id):
    """Obtiene el diagnóstico de una imagen del CSV"""
    df = pd.read_csv(METADATA_CSV)
    row = df[df['ID_Imagen'] == imagen_id]
    if len(row) > 0:
        return row.iloc[0]['Diagnostico_Ref_Bethesda']
    return 'NEGATIVO'


def es_diagnostico_anormal(diagnostico):
    """Verifica si el diagnóstico es anormal"""
    return diagnostico in DIAGNOSTICOS_ANORMALES


def procesar_imagen_y_generar_labels(ruta_imagen, diagnostico):
    """
    Procesa una imagen y genera etiquetas YOLO.
    
    Returns:
        list of (class_id, x_center, y_center, width, height) normalized
    """
    try:
        # Preprocesar
        imagen_gris, imagen_original = preprocesar_imagen(
            str(ruta_imagen),
            mejorar_contraste_flag=USAR_CLAHE,
            reducir_ruido_flag=REDUCIR_RUIDO,
            metodo_contraste='clahe',
            polaridad=POLARIDAD,
            usar_hsv=False
        )
        
        # Verificar calidad
        calidad = verificar_calidad_imagen(imagen_gris)
        if not calidad['es_aceptable']:
            print(f"  ⚠️  Imagen de baja calidad: {calidad['advertencias']}")
        
        # DoG
        imagen_dog = aplicar_filtro_dog(imagen_gris, SIGMA1, SIGMA2)
        
        # Análisis
        resultados = analizar_nucleos(
            imagen_dog, 
            imagen_original, 
            polaridad=POLARIDAD,
            metodo_separacion=None
        )
        
        # Obtener reglas de clasificación
        reglas = obtener_reglas_clasificacion(POLARIDAD)
        umbral_sospechoso = reglas['umbral_sospechoso']
        
        # Generar etiquetas YOLO
        h, w = imagen_original.shape[:2]
        etiquetas = []
        
        for i, (contorno, area) in enumerate(zip(
            resultados['contornos_normales'] + resultados['contornos_sospechosos'],
            resultados['areas']
        )):
            # Obtener bounding box
            x, y, w_box, h_box = cv2.boundingRect(contorno)
            
            # Normalizar coordenadas YOLO
            x_center = (x + w_box / 2) / w
            y_center = (y + h_box / 2) / h
            width_norm = w_box / w
            height_norm = h_box / h
            
            # Clasificar según diagnóstico y área
            if es_diagnostico_anormal(diagnostico) and area >= umbral_sospechoso:
                class_id = 1  # Anormal
            else:
                class_id = 0  # Normal
            
            etiquetas.append((class_id, x_center, y_center, width_norm, height_norm))
        
        return etiquetas
        
    except Exception as e:
        print(f"  ❌ Error procesando {ruta_imagen.name}: {e}")
        return []


def escribir_etiquetas_yolo(ruta_label, etiquetas):
    """Escribe etiquetas en formato YOLO"""
    with open(ruta_label, 'w') as f:
        for class_id, x_center, y_center, width, height in etiquetas:
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")


def main():
    print("=" * 70)
    print("🔧 GENERANDO ETIQUETAS CORRECTAS PARA VALIDACIÓN Y TEST")
    print("=" * 70)
    print()
    
    # Cargar CSV de metadatos
    df = pd.read_csv(METADATA_CSV)
    print(f"Registros en CSV: {len(df)}")
    print()
    
    # Procesar validación
    print("📁 Procesando conjunto de VALIDACIÓN...")
    val_procesadas = 0
    val_actualizadas = 0
    
    for label_file in LABELS_VAL.glob('*.txt'):
        imagen_id = label_file.stem
        
        # Buscar imagen correspondiente
        ruta_imagen = None
        for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            for case_ext in [ext, ext.upper()]:
                p = RAW_DIR / 'val' / f"{imagen_id}{case_ext}"
                if p.exists():
                    ruta_imagen = p
                    break
            if ruta_imagen:
                break
        
        if not ruta_imagen:
            print(f"  ⚠️  Imagen no encontrada para {imagen_id}")
            continue
        
        val_procesadas += 1
        
        # Obtener diagnóstico
        diagnostico = obtener_diagnostico(imagen_id)
        
        # Procesar imagen y generar etiquetas
        etiquetas = procesar_imagen_y_generar_labels(ruta_imagen, diagnostico)
        
        if etiquetas:
            # Verificar si hay cambios respecto al archivo actual
            contenido_actual = label_file.read_text().strip()
            nuevo_contenido = '\n'.join(
                f"{c} {x:.6f} {y:.6f} {w:.6f} {h:.6f}" 
                for c, x, y, w, h in etiquetas
            )
            
            if contenido_actual != nuevo_contenido:
                escribir_etiquetas_yolo(label_file, etiquetas)
                val_actualizadas += 1
                if val_actualizadas <= 10:  # Mostrar solo las primeras 10
                    anormales = sum(1 for c, *_ in etiquetas if c == 1)
                    print(f"  ✅ {imagen_id} ({diagnostico}): {len(etiquetas)} núcleos, {anormales} anormales")
            else:
                if val_actualizadas <= 10:
                    anormales = sum(1 for c, *_ in etiquetas if c == 1)
                    print(f"  ✓ {imagen_id} ({diagnostico}): {len(etiquetas)} núcleos, {anormales} anormales (sin cambios)")
        else:
            print(f"  ⚠️  {imagen_id}: No se detectaron núcleos")
    
    print(f"\nValidación: {val_procesadas} procesadas, {val_actualizadas} actualizadas")
    print()
    
    # Procesar test
    print("📁 Procesando conjunto de TEST...")
    test_procesadas = 0
    test_actualizadas = 0
    
    for label_file in LABELS_TEST.glob('*.txt'):
        imagen_id = label_file.stem
        
        # Buscar imagen correspondiente
        ruta_imagen = None
        for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            for case_ext in [ext, ext.upper()]:
                p = RAW_DIR / 'test' / f"{imagen_id}{ext}"
                if p.exists():
                    ruta_imagen = p
                    break
            if ruta_imagen:
                break
        
        if not ruta_imagen:
            print(f"  ⚠️  Imagen no encontrada para {imagen_id}")
            continue
        
        test_procesadas += 1
        
        # Obtener diagnóstico
        diagnostico = obtener_diagnostico(imagen_id)
        
        # Procesar imagen y generar etiquetas
        etiquetas = procesar_imagen_y_generar_labels(ruta_imagen, diagnostico)
        
        if etiquetas:
            # Verificar si hay cambios respecto al archivo actual
            contenido_actual = label_file.read_text().strip()
            nuevo_contenido = '\n'.join(
                f"{c} {x:.6f} {y:.6f} {w:.6f} {h:.6f}" 
                for c, x, y, w, h in etiquetas
            )
            
            if contenido_actual != nuevo_contenido:
                escribir_etiquetas_yolo(label_file, etiquetas)
                test_actualizadas += 1
                if test_actualizadas <= 10:
                    anormales = sum(1 for c, *_ in etiquetas if c == 1)
                    print(f"  ✅ {imagen_id} ({diagnostico}): {len(etiquetas)} núcleos, {anormales} anormales")
            else:
                if test_actualizadas <= 10:
                    anormales = sum(1 for c, *_ in etiquetas if c == 1)
                    print(f"  ✓ {imagen_id} ({diagnostico}): {len(etiquetas)} núcleos, {anormales} anormales (sin cambios)")
        else:
            print(f"  ⚠️  {imagen_id}: No se detectaron núcleos")
    
    print(f"\nTest: {test_procesadas} procesadas, {test_actualizadas} actualizadas")
    print()
    
    print("=" * 70)
    print("✅ GENERACIÓN DE ETIQUETAS COMPLETADA")
    print("=" * 70)
    print()
    print("Próximo paso: Ejecutar validación completa")
    print("  python validar_consistencia_dataset.py")


if __name__ == '__main__':
    main()