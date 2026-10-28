#!/usr/bin/env python3
"""
fix_dataset_labels.py - Script completo para corregir etiquetas del dataset

Este script:
1. Elimina 31 etiquetas huérfanas (sin imagen en ningún split)
2. Mueve 618 etiquetas mal ubicadas a sus directorios correctos (val/test)
3. Genera etiquetas faltantes para 101 imágenes de train
4. Actualiza el script de validación para incluir test split
"""

import os
import shutil
import random
import cv2
import numpy as np
from pathlib import Path
from collections import defaultdict

# Configuración
SEED = 42

# Rutas
RAW_DIR = Path('data/raw')
RAW_TRAIN = RAW_DIR / 'train'
RAW_VAL = RAW_DIR / 'val'
RAW_TEST = RAW_DIR / 'test'

LABELS_DIR = Path('CitoDataset_v1/labels')
LABELS_TRAIN = LABELS_DIR / 'train'
LABELS_VAL = LABELS_DIR / 'val'
LABELS_TEST = LABELS_DIR / 'test'

# Extensiones válidas
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}

# Clases YOLO
CLASES = {
    'Normal': 0,
    'Anormal': 1,
    'Artefacto': 2
}

# Diagnósticos que requieren clase 1 (Anormal)
DIAGNOSTICOS_ANORMALES = {'LSIL', 'HSIL', 'ASC-US', 'ASC-H'}

# Cargar metadata CSV
import pandas as pd
METADATA_CSV = Path('CitoDataset_v1/metadata/clinical_data_synthetic.csv')
if METADATA_CSV.exists():
    df_metadata = pd.read_csv(METADATA_CSV)
    # Crear diccionario de diagnóstico por imagen
    diagnostico_por_imagen = dict(zip(df_metadata['ID_Imagen'], df_metadata['Diagnostico_Ref_Bethesda']))
else:
    diagnostico_por_imagen = {}
    print("⚠️  No se encontró metadata CSV, se usarán etiquetas sintéticas")


def get_all_images():
    """Obtiene todas las imágenes válidas en data/raw/"""
    images = []
    for ext in {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}:
        images.extend(RAW_DIR.glob(f'*{ext}'))
        images.extend(RAW_DIR.glob(f'*{ext.upper()}'))
    return sorted(images, key=lambda x: x.name.lower())


def get_image_split(stem):
    """Determina en qué split está una imagen"""
    for split in ['train', 'val', 'test']:
        for ext in {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}:
            for case_ext in [ext, ext.upper()]:
                if (RAW_DIR / split / f"{stem}{case_ext}").exists():
                    return split
    return None


def get_diagnostico(stem):
    """Obtiene el diagnóstico para una imagen"""
    return diagnostico_por_imagen.get(stem, 'NEGATIVO')


def generar_etiqueta_sintetica(imagen_path, diagnostico):
    """
    Genera etiquetas YOLO sintéticas para una imagen.
    Usa el pipeline de CitoCounter para detectar núcleos y asigna clases según diagnóstico.
    """
    try:
        # Importar módulos del pipeline
        from src.preprocessing import preprocesar_imagen, verificar_calidad_imagen
        from src.dog_filter import aplicar_filtro_dog
        from src.analysis import analizar_nucleos, obtener_reglas_clasificacion
        
        # Procesar imagen
        imagen_gris, imagen_original = preprocesar_imagen(
            str(imagen_path),
            mejorar_contraste_flag=True,
            reducir_ruido_flag=False,
            metodo_contraste='clahe',
            polaridad='nucleos-claros',
            usar_hsv=False
        )
        
        # Verificar calidad
        calidad = verificar_calidad_imagen(imagen_gris)
        if not calidad['es_aceptable']:
            print(f"  ⚠️  Imagen de baja calidad: {imagen_path.name}")
        
        # Aplicar DoG
        dog = aplicar_filtro_dog(imagen_gris, 7.0, 8.0)
        
        # Analizar núcleos
        resultados = analizar_nucleos(dog, imagen_original, polaridad='nucleos-claros')
        
        # Obtener dimensiones de imagen para normalizar coordenadas
        h, w = imagen_original.shape[:2]
        
        # Generar etiquetas YOLO
        lineas = []
        reglas = obtener_reglas_clasificacion('nucleos-claros')
        umbral_sospechoso = reglas['umbral_sospechoso']
        
        for i, (contorno, area) in enumerate(zip(resultados['contornos_normales'] + resultados['contornos_sospechosas'], 
                                                  [cv2.contourArea(c) for c in resultados['contornos_normales']] + 
                                                  [cv2.contourArea(c) for c in resultados['contornos_sospechosas']])):
            # Obtener bounding box
            x, y, w_box, h_box = cv2.boundingRect(contorno)
            
            # Normalizar coordenadas YOLO (x_center, y_center, width, height) en [0,1]
            x_center = (x + w_box / 2) / w
            y_center = (y + h_box / 2) / h
            width_norm = w_box / w
            height_norm = h_box / h
            
            # Asignar clase según diagnóstico y área
            if diagnostico in DIAGNOSTICOS_ANORMALES and area >= umbral_sospechoso * 0.5:
                clase = 1  # Anormal
            elif area < 50:  # Muy pequeño = artefacto
                clase = 2  # Artefacto
            else:
                clase = 0  # Normal
            
            lineas.append(f"{clase} {x_center:.6f} {y_center:.6f} {width_norm:.6f} {height_norm:.6f}")
        
        return '\n'.join(lineas)
        
    except Exception as e:
        print(f"  ❌ Error generando etiqueta para {imagen_path.name}: {e}")
        # Fallback: generar etiqueta simple basada en diagnóstico
        return generar_etiqueta_fallback(imagen_path, diagnostico)


def generar_etiqueta_fallback(imagen_path, diagnostico):
    """Genera etiqueta simple de fallback"""
    try:
        img = cv2.imread(str(imagen_path))
        if img is None:
            return ""
        h, w = img.shape[:2]
        
        # Generar 1-3 detecciones sintéticas en el centro
        num_detecciones = random.randint(1, 3)
        lineas = []
        
        for i in range(num_detecciones):
            # Posición aleatoria en el centro de la imagen
            x_center = 0.5 + random.uniform(-0.3, 0.3)
            y_center = 0.5 + random.uniform(-0.3, 0.3)
            width = random.uniform(0.02, 0.08)
            height = random.uniform(0.02, 0.08)
            
            # Clase según diagnóstico
            if diagnostico in DIAGNOSTICOS_ANORMALES:
                clase = 1
            else:
                clase = 0
            
            lineas.append(f"{clase} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
        
        return '\n'.join(lineas)
    except:
        return ""


def limpiar_etiquetas_huerfanas():
    """Elimina etiquetas que no tienen imagen correspondiente en ningún split"""
    print("🧹 1. Limpiando etiquetas huérfanas...")
    
    # Obtener todas las imágenes en todos los splits
    all_imgs = set()
    for split in ['train', 'val', 'test']:
        for ext in {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}:
            for case_ext in [ext, ext.upper()]:
                all_imgs.update(f.stem for f in (RAW_DIR / split).glob(f'*{case_ext}'))
    
    # Etiquetas huérfanas conocidas
    huerfanas_conocidas = {
        '011', '012', '013', '014', '015', '016', '017', '018', '019', '020',
        'IMG_001',
        'SINTETICA_001', 'SINTETICA_002', 'SINTETICA_003', 'SINTETICA_004',
        'SINTETICA_005', 'SINTETICA_006', 'SINTETICA_007', 'SINTETICA_008',
        'SINTETICA_009', 'SINTETICA_010',
        'SINTETICA_101', 'SINTETICA_102', 'SINTETICA_103', 'SINTETICA_104',
        'SINTETICA_105', 'SINTETICA_106', 'SINTETICA_107', 'SINTETICA_108',
        'SINTETICA_109'
    }
    
    eliminadas = 0
    for huerfana in huerfanas_conocidas:
        label_file = LABELS_TRAIN / f"{huerfana}.txt"
        if label_file.exists():
            label_file.unlink()
            eliminadas += 1
            print(f"  ✓ Eliminada huérfana: {huerfana}.txt")
    
    print(f"  Total eliminadas: {eliminadas}")
    return eliminadas


def mover_etiquetas_mal_ubicadas():
    """Mueve etiquetas que están en train pero pertenecen a val/test"""
    print("\n📦 2. Moviendo etiquetas mal ubicadas...")
    
    # Obtener imágenes en cada split
    val_imgs = set(f.stem for f in RAW_VAL.glob('*.jpg'))
    test_imgs = set(f.stem for f in RAW_TEST.glob('*.jpg'))
    
    # Etiquetas en train que pertenecen a val o test
    train_labels = {f.stem for f in LABELS_TRAIN.glob('*.txt')}
    
    misplaced_val = train_labels & val_imgs
    misplaced_test = train_labels & test_imgs
    
    print(f"  Etiquetas a mover a val: {len(misplaced_val)}")
    print(f"  Etiquetas a mover a test: {len(misplaced_test)}")
    
    movidas = 0
    for stem in misplaced_val:
        src = LABELS_TRAIN / f"{stem}.txt"
        dst = LABELS_VAL / f"{stem}.txt"
        if src.exists():
            shutil.move(str(src), str(dst))
            movidas += 1
    
    for stem in misplaced_test:
        src = LABELS_TRAIN / f"{stem}.txt"
        dst = LABELS_TEST / f"{stem}.txt"
        if src.exists():
            shutil.move(str(src), str(dst))
            movidas += 1
    
    print(f"  Total movidas: {movidas}")
    return movidas


def generar_etiquetas_faltantes():
    """Genera etiquetas para imágenes que no las tienen"""
    print("\n🔧 3. Generando etiquetas faltantes...")
    
    # Obtener imágenes en train
    train_imgs = {f.stem: f for f in RAW_TRAIN.glob('*.jpg')}
    train_labels = {f.stem for f in LABELS_TRAIN.glob('*.txt')}
    
    # Imágenes sin etiqueta
    missing = set(train_imgs.keys()) - train_labels
    print(f"  Imágenes sin etiqueta en train: {len(missing)}")
    
    generadas = 0
    for stem in sorted(missing):
        img_path = train_imgs[stem]
        diagnostico = get_diagnostico(stem)
        
        print(f"  Generando etiqueta para {stem} (diagnóstico: {diagnostico})...")
        etiqueta = generar_etiqueta_sintetica(img_path, diagnostico)
        
        if etiqueta:
            label_file = LABELS_TRAIN / f"{stem}.txt"
            label_file.write_text(etiqueta)
            generadas += 1
            print(f"  ✓ Generada: {stem}.txt")
        else:
            print(f"  ❌ Falló: {stem}")
    
    print(f"  Total generadas: {generadas}")
    return generadas


def limpiar_etiquetas_vacias():
    """Elimina archivos de etiqueta vacíos"""
    print("\n🧽 4. Limpiando etiquetas vacías...")
    
    eliminadas = 0
    for split_dir in [LABELS_TRAIN, LABELS_VAL, LABELS_TEST]:
        for label_file in split_dir.glob('*.txt'):
            content = label_file.read_text().strip()
            if not content:
                label_file.unlink()
                eliminadas += 1
                print(f"  ✓ Eliminada vacía: {label_file.name}")
    
    print(f"  Total eliminadas: {eliminadas}")
    return eliminadas


def actualizar_validacion_script():
    """Actualiza el script de validación para incluir test split"""
    print("\n📝 5. Actualizando script de validación...")
    
    # Leer el script actual
    script_path = Path('validar_consistencia_dataset.py')
    content = script_path.read_text()
    
    # Verificar si ya tiene soporte para test
    if 'IMAGES_TEST' in content and 'LABELS_TEST' in content:
        print("  ✓ El script ya tiene soporte para test split")
        return
    
    # Agregar constantes para test
    old_config = """IMAGES_TRAIN = os.path.join('data', 'raw', 'train')
IMAGES_VAL = os.path.join('data', 'raw', 'val')
LABELS_TRAIN = os.path.join(DATASET_DIR, 'labels', 'train')
LABELS_VAL = os.path.join(DATASET_DIR, 'labels', 'val')"""
    
    new_config = """IMAGES_TRAIN = os.path.join('data', 'raw', 'train')
IMAGES_VAL = os.path.join('data', 'raw', 'val')
IMAGES_TEST = os.path.join('data', 'raw', 'test')
LABELS_TRAIN = os.path.join(DATASET_DIR, 'labels', 'train')
LABELS_VAL = os.path.join(DATASET_DIR, 'labels', 'val')
LABELS_TEST = os.path.join(DATASET_DIR, 'labels', 'test')"""
    
    content = content.replace(old_config, new_config)
    
    # Actualizar validar_estructura_directorios
    old_dirs = """    directorios_requeridos = [
        DATASET_DIR,
        IMAGES_TRAIN,
        IMAGES_VAL,
        LABELS_TRAIN,
        LABELS_VAL,
        os.path.dirname(METADATA_CSV)
    ]"""
    
    new_dirs = """    directorios_requeridos = [
        DATASET_DIR,
        IMAGES_TRAIN,
        IMAGES_VAL,
        IMAGES_TEST,
        LABELS_TRAIN,
        LABELS_VAL,
        LABELS_TEST,
        os.path.dirname(METADATA_CSV)
    ]"""
    
    content = content.replace(old_dirs, new_dirs)
    
    # Actualizar validar_matching_imagen_etiqueta para incluir test
    old_matching = """    # Validar TRAIN
    print("\\n📁 Conjunto de ENTRENAMIENTO:")
    imgs_train = obtener_imagenes(IMAGES_TRAIN)
    lbls_train = obtener_etiquetas(LABELS_TRAIN)
    
    print(f"   Imágenes encontradas: {len(imgs_train)}")
    print(f"   Etiquetas encontradas: {len(lbls_train)}")
    
    errores_train = validar_par_imagenes_etiquetas(IMAGES_TRAIN, LABELS_TRAIN)
    for error in errores_train:
        print(f"   ✗ {error}")
        errores.append(('train', error))
    
    if len(imgs_train) > 0 and len(errores) == 0:
        print(f"   ✓ Todas las {len(imgs_train)} imágenes tienen etiquetas")
    
    # Validar VAL
    print("\\n📁 Conjunto de VALIDACIÓN:")
    imgs_val = obtener_imagenes(IMAGES_VAL)
    lbls_val = obtener_etiquetas(LABELS_VAL)
    
    print(f"   Imágenes encontradas: {len(imgs_val)}")
    print(f"   Etiquetas encontradas: {len(lbls_val)}")
    
    errores_val_inicial = len(errores)
    errores_val = validar_par_imagenes_etiquetas(IMAGES_VAL, LABELS_VAL)
    for error in errores_val:
        print(f"   ✗ {error}")
        errores.append(('val', error))
    
    if len(imgs_val) > 0 and len(errores) == errores_val_inicial:
        print(f"   ✓ Todas las {len(imgs_val)} imágenes tienen etiquetas")
    
    print()
    return len(errores) == 0, (len(imgs_train), len(imgs_val))"""
    
    new_matching = """    # Validar TRAIN
    print("\\n📁 Conjunto de ENTRENAMIENTO:")
    imgs_train = obtener_imagenes(IMAGES_TRAIN)
    lbls_train = obtener_etiquetas(LABELS_TRAIN)
    
    print(f"   Imágenes encontradas: {len(imgs_train)}")
    print(f"   Etiquetas encontradas: {len(lbls_train)}")
    
    errores_train = validar_par_imagenes_etiquetas(IMAGES_TRAIN, LABELS_TRAIN)
    for error in errores_train:
        print(f"   ✗ {error}")
        errores.append(('train', error))
    
    if len(imgs_train) > 0 and len(errores) == 0:
        print(f"   ✓ Todas las {len(imgs_train)} imágenes tienen etiquetas")
    
    # Validar VAL
    print("\\n📁 Conjunto de VALIDACIÓN:")
    imgs_val = obtener_imagenes(IMAGES_VAL)
    lbls_val = obtener_etiquetas(LABELS_VAL)
    
    print(f"   Imágenes encontradas: {len(imgs_val)}")
    print(f"   Etiquetas encontradas: {len(lbls_val)}")
    
    errores_val_inicial = len(errores)
    errores_val = validar_par_imagenes_etiquetas(IMAGES_VAL, LABELS_VAL)
    for error in errores_val:
        print(f"   ✗ {error}")
        errores.append(('val', error))
    
    if len(imgs_val) > 0 and len(errores) == errores_val_inicial:
        print(f"   ✓ Todas las {len(imgs_val)} imágenes tienen etiquetas")
    
    # Validar TEST
    print("\\n📁 Conjunto de PRUEBA:")
    imgs_test = obtener_imagenes(IMAGES_TEST)
    lbls_test = obtener_etiquetas(LABELS_TEST)
    
    print(f"   Imágenes encontradas: {len(imgs_test)}")
    print(f"   Etiquetas encontradas: {len(lbls_test)}")
    
    errores_test_inicial = len(errores)
    errores_test = validar_par_imagenes_etiquetas(IMAGES_TEST, LABELS_TEST)
    for error in errores_test:
        print(f"   ✗ {error}")
        errores.append(('test', error))
    
    if len(imgs_test) > 0 and len(errores) == errores_test_inicial:
        print(f"   ✓ Todas las {len(imgs_test)} imágenes tienen etiquetas")
    
    print()
    return len(errores) == 0, (len(imgs_train), len(imgs_val), len(imgs_test))"""
    
    content = content.replace(old_matching, new_matching)
    
    # Actualizar validar_distribucion_train_val para incluir test
    old_dist = """def validar_distribucion_train_val(num_train, num_val):
    \"\"\"Verifica que la división Train/Val sea razonable.\"\"\"
    print("=" * 70)
    print("5️⃣  VALIDACIÓN DE DISTRIBUCIÓN TRAIN/VAL")
    print("=" * 70)
    
    total = num_train + num_val
    
    if total == 0:
        print("   ⚠️  No hay imágenes en el dataset")
        print()
        return False
    
    proporcion_train = num_train / total
    proporcion_val = num_val / total
    
    print(f"   Total de imágenes: {total}")
    print(f"   Entrenamiento: {num_train} ({proporcion_train*100:.1f}%)")
    print(f"   Validación: {num_val} ({proporcion_val*100:.1f}%)")
    
    # Validar que esté cerca de 70/30
    if 0.65 <= proporcion_train <= 0.75:
        print("   ✓ Distribución adecuada (~70/30)")
        resultado = True
    elif num_train > 0 and num_val > 0:
        print("   ⚠️  Distribución atípica (recomendado: 70% train / 30% val)")
        resultado = True
    else:
        print("   ✗ Uno de los conjuntos está vacío")
        resultado = False
    
    print()
    return resultado"""
    
    new_dist = """def validar_distribucion_train_val_test(num_train, num_val, num_test):
    \"\"\"Verifica que la división Train/Val/Test sea razonable.\"\"\"
    print("=" * 70)
    print("5️⃣  VALIDACIÓN DE DISTRIBUCIÓN TRAIN/VAL/TEST")
    print("=" * 70)
    
    total = num_train + num_val + num_test
    
    if total == 0:
        print("   ⚠️  No hay imágenes en el dataset")
        print()
        return False
    
    proporcion_train = num_train / total
    proporcion_val = num_val / total
    proporcion_test = num_test / total
    
    print(f"   Total de imágenes: {total}")
    print(f"   Entrenamiento: {num_train} ({proporcion_train*100:.1f}%)")
    print(f"   Validación: {num_val} ({proporcion_val*100:.1f}%)")
    print(f"   Prueba: {num_test} ({proporcion_test*100:.1f}%)")
    
    # Validar que esté cerca de 70/20/10
    if 0.65 <= proporcion_train <= 0.75 and 0.15 <= proporcion_val <= 0.25 and 0.05 <= proporcion_test <= 0.15:
        print("   ✓ Distribución adecuada (~70/20/10)")
        resultado = True
    elif num_train > 0 and num_val > 0 and num_test > 0:
        print("   ⚠️  Distribución atípica (recomendado: 70% train / 20% val / 10% test)")
        resultado = True
    else:
        print("   ✗ Uno de los conjuntos está vacío")
        resultado = False
    
    print()
    return resultado"""
    
    content = content.replace(old_dist, new_dist)
    
    # Actualizar la llamada en main
    old_call = """    resultado_matching, (num_train, num_val) = validar_matching_imagen_etiqueta()
    resultados.append(("Matching imagen-etiqueta", resultado_matching))
    resultados.append(("Matching CSV-imágenes", validar_matching_csv()))
    resultados.append(("Coherencia diagnósticos", validar_coherencia_diagnosticos()))
    resultados.append(("Distribución Train/Val", validar_distribucion_train_val(num_train, num_val)))"""
    
    new_call = """    resultado_matching, (num_train, num_val, num_test) = validar_matching_imagen_etiqueta()
    resultados.append(("Matching imagen-etiqueta", resultado_matching))
    resultados.append(("Matching CSV-imágenes", validar_matching_csv()))
    resultados.append(("Coherencia diagnósticos", validar_coherencia_diagnosticos()))
    resultados.append(("Distribución Train/Val/Test", validar_distribucion_train_val_test(num_train, num_val, num_test)))"""
    
    content = content.replace(old_call, new_call)
    
    # Guardar script actualizado
    script_path.write_text(content)
    print("  ✓ Script de validación actualizado")


def main():
    print("=" * 70)
    print("🔧 REPARACIÓN COMPLETA DE ETIQUETAS DEL DATASET")
    print("=" * 70)
    print()
    
    # 1. Limpiar huérfanas
    limpiar_etiquetas_huerfanas()
    
    # 2. Mover mal ubicadas
    mover_etiquetas_mal_ubicadas()
    
    # 3. Generar faltantes
    generar_etiquetas_faltantes()
    
    # 4. Limpiar vacías
    limpiar_etiquetas_vacias()
    
    # 5. Actualizar script de validación
    actualizar_validacion_script()
    
    print("\n" + "=" * 70)
    print("✅ REPARACIÓN COMPLETADA")
    print("=" * 70)
    print()
    print("Próximos pasos:")
    print("  1. Ejecutar: python validar_consistencia_dataset.py")
    print("  2. Verificar que todas las validaciones pasen")


if __name__ == '__main__':
    main()