#!/usr/bin/env python3
"""
split_dataset.py - Script para dividir el dataset CitoDataset_v1 en splits train/val/test (70/20/10)

Este script:
1. Escanea todas las imágenes en data/raw/
2. Las divide en 70% train, 20% val, 10% test con seed=42 para reproducibilidad
3. Copia las imágenes a data/raw/train, data/raw/val, data/raw/test
4. Copia las etiquetas correspondientes a CitoDataset_v1/labels/train, val, test
5. Actualiza clinical_data_synthetic.csv con todas las imágenes
6. Crea dataset_index.csv con columna Split
7. Limpia archivos problemáticos (reporte_etiquetado.txt, etiquetas vacías)
"""

import os
import shutil
import random
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Configuración
SEED = 42
SPLIT_RATIOS = {'train': 0.70, 'val': 0.20, 'test': 0.10}

# Rutas
RAW_DIR = Path('data/raw')
RAW_TRAIN = RAW_DIR / 'train'
RAW_VAL = RAW_DIR / 'val'
RAW_TEST = RAW_DIR / 'test'

LABELS_DIR = Path('CitoDataset_v1/labels')
LABELS_TRAIN = LABELS_DIR / 'train'
LABELS_VAL = LABELS_DIR / 'val'
LABELS_TEST = LABELS_DIR / 'test'

METADATA_CSV = Path('CitoDataset_v1/metadata/clinical_data_synthetic.csv')
DATASET_INDEX_CSV = Path('CitoDataset_v1/dataset_index.csv')
CLASSES_FILE = Path('CitoDataset_v1/classes.txt')

# Extensiones válidas
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}


def get_all_images():
    """Obtiene todas las imágenes válidas en data/raw/"""
    images = []
    for ext in VALID_EXTENSIONS:
        images.extend(RAW_DIR.glob(f'*{ext}'))
        images.extend(RAW_DIR.glob(f'*{ext.upper()}'))
    return sorted(images, key=lambda x: x.name.lower())


def split_images(images, seed=SEED):
    """Divide las imágenes en train/val/test con seed fijo"""
    random.seed(seed)
    shuffled = images.copy()
    random.shuffle(shuffled)
    
    n_total = len(shuffled)
    n_train = int(n_total * SPLIT_RATIOS['train'])
    n_val = int(n_total * SPLIT_RATIOS['val'])
    n_test = n_total - n_train - n_val
    
    train = shuffled[:n_train]
    val = shuffled[n_train:n_train + n_val]
    test = shuffled[n_train + n_val:]
    
    print(f"Total imágenes: {n_total}")
    print(f"Train: {len(train)} ({len(train)/n_total*100:.1f}%)")
    print(f"Val: {len(val)} ({len(val)/n_total*100:.1f}%)")
    print(f"Test: {len(test)} ({len(test)/n_total*100:.1f}%)")
    
    return train, val, test


def copy_images_to_splits(train_imgs, val_imgs, test_imgs):
    """Copia las imágenes a los directorios de splits"""
    splits = {
        'train': (train_imgs, RAW_TRAIN),
        'val': (val_imgs, RAW_VAL),
        'test': (test_imgs, RAW_TEST)
    }
    
    for split_name, (images, dest_dir) in splits.items():
        dest_dir.mkdir(parents=True, exist_ok=True)
        for img in images:
            dest = dest_dir / img.name
            shutil.copy2(img, dest)
        print(f"Copiadas {len(images)} imágenes a {dest_dir}")


def copy_labels_to_splits(train_imgs, val_imgs, test_imgs):
    """Copia las etiquetas correspondientes a los directorios de splits"""
    # Mapear nombre de imagen (sin extensión) a split
    img_to_split = {}
    for img in train_imgs:
        img_to_split[img.stem] = 'train'
    for img in val_imgs:
        img_to_split[img.stem] = 'val'
    for img in test_imgs:
        img_to_split[img.stem] = 'test'
    
    # Procesar etiquetas existentes
    labels_copied = {'train': 0, 'val': 0, 'test': 0}
    labels_skipped = 0
    
    for label_file in LABELS_TRAIN.glob('*.txt'):
        stem = label_file.stem
        if stem in img_to_split:
            split = img_to_split[stem]
            dest_dir = {'train': LABELS_TRAIN, 'val': LABELS_VAL, 'test': LABELS_TEST}[split]
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / label_file.name
            
            # Leer contenido y verificar si está vacío o es reporte_etiquetado
            content = label_file.read_text().strip()
            if label_file.name == 'reporte_etiquetado.txt':
                print(f"  Saltando reporte_etiquetado.txt")
                labels_skipped += 1
                continue
            if not content:
                print(f"  Saltando etiqueta vacía: {label_file.name}")
                labels_skipped += 1
                continue
            
            # Verificar formato YOLO válido
            lines = content.split('\n')
            valid = True
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) != 5:
                        valid = False
                        break
                    try:
                        cls = int(parts[0])
                        coords = [float(p) for p in parts[1:]]
                        if cls not in {0, 1, 2} or any(c < 0 or c > 1 for c in coords):
                            valid = False
                            break
                    except ValueError:
                        valid = False
                        break
            
            if not valid:
                print(f"  Saltando etiqueta con formato inválido: {label_file.name}")
                labels_skipped += 1
                continue
            
            # Evitar copiar si origen y destino son el mismo
            if label_file.resolve() != dest.resolve():
                shutil.copy2(label_file, dest)
            labels_copied[split] += 1
        else:
            print(f"  Advertencia: Etiqueta sin imagen correspondiente: {label_file.name}")
    
    print(f"Etiquetas copiadas - Train: {labels_copied['train']}, Val: {labels_copied['val']}, Test: {labels_copied['test']}")
    print(f"Etiquetas saltadas: {labels_skipped}")
    
    return img_to_split


def update_metadata_csv(img_to_split):
    """Actualiza clinical_data_synthetic.csv con todas las imágenes"""
    # Leer CSV existente
    if METADATA_CSV.exists():
        df = pd.read_csv(METADATA_CSV)
    else:
        df = pd.DataFrame(columns=[
            'ID_Imagen', 'ID_Paciente_Sintetico', 'Fecha_Toma', 'Edad',
            'Estado_Hormonal', 'Metodo_Toma', 'Calidad_Muestra',
            'Diagnostico_Ref_Bethesda', 'VPH_Test', 'Observaciones'
        ])
    
    # Obtener IDs existentes
    existing_ids = set(df['ID_Imagen'].values) if 'ID_Imagen' in df.columns else set()
    
    # Generar datos sintéticos para nuevas imágenes
    import uuid
    from datetime import datetime, timedelta
    
    new_rows = []
    for stem, split in img_to_split.items():
        if stem not in existing_ids:
            # Generar ID de paciente sintético
            patient_id = str(uuid.uuid4())[:8].upper()
            
            # Fecha aleatoria en los últimos 2 años
            start_date = datetime(2023, 1, 1)
            end_date = datetime(2025, 12, 31)
            random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
            
            # Edad aleatoria 20-80
            edad = random.randint(20, 80)
            
            # Estado hormonal
            estados = ['Pre-menopáusica', 'Post-menopáusica', 'Peri-menopáusica']
            estado = random.choice(estados)
            
            # Método de toma
            metodos = ['Base Líquida (ThinPrep)', 'Convencional', 'SurePath']
            metodo = random.choice(metodos)
            
            # Calidad
            calidades = ['Satisfactoria', 'Insatisfactoria', 'Limitada']
            calidad = random.choice(calidades)
            
            # Diagnóstico (mayoría negativos)
            diagnosticos = ['NEGATIVO', 'LSIL', 'HSIL', 'ASC-US', 'ASC-H']
            diagnostico = random.choices(diagnosticos, weights=[0.7, 0.1, 0.05, 0.1, 0.05])[0]
            
            # VPH
            vph = random.choice(['Positivo', 'Negativo', 'No realizado'])
            
            new_rows.append({
                'ID_Imagen': stem,
                'ID_Paciente_Sintetico': patient_id,
                'Fecha_Toma': random_date.strftime('%Y-%m-%d'),
                'Edad': edad,
                'Estado_Hormonal': estado,
                'Metodo_Toma': metodo,
                'Calidad_Muestra': calidad,
                'Diagnostico_Ref_Bethesda': diagnostico,
                'VPH_Test': vph,
                'Observaciones': ''
            })
    
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(METADATA_CSV, index=False)
        print(f"Actualizado {METADATA_CSV}: {len(new_rows)} nuevas filas añadidas")
    else:
        print(f"No hay nuevas imágenes para añadir a {METADATA_CSV}")


def create_dataset_index(img_to_split):
    """Crea dataset_index.csv con columna Split"""
    rows = []
    for stem, split in img_to_split.items():
        # Buscar la extensión original
        img_path = None
        for ext in VALID_EXTENSIONS:
            for case_ext in [ext, ext.upper()]:
                p = RAW_DIR / f"{stem}{case_ext}"
                if p.exists():
                    img_path = p
                    break
            if img_path:
                break
        
        if img_path:
            rows.append({
                'ID_Imagen': stem,
                'Archivo': img_path.name,
                'Split': split,
                'Ruta': str(img_path.relative_to(RAW_DIR.parent))
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(DATASET_INDEX_CSV, index=False)
    print(f"Creado {DATASET_INDEX_CSV} con {len(rows)} entradas")


def clean_labels_directory():
    """Limpia archivos problemáticos en labels"""
    # Eliminar reporte_etiquetado.txt
    reporte = LABELS_TRAIN / 'reporte_etiquetado.txt'
    if reporte.exists():
        reporte.unlink()
        print(f"Eliminado: {reporte}")
    
    # Eliminar etiquetas vacías en train
    for label_file in LABELS_TRAIN.glob('*.txt'):
        content = label_file.read_text().strip()
        if not content:
            label_file.unlink()
            print(f"Eliminada etiqueta vacía: {label_file.name}")


def main():
    print("=" * 70)
    print("🔄 DIVISIÓN DE DATASET CITOCOUNTER - SPLITS 70/20/10")
    print("=" * 70)
    print()
    
    # 1. Obtener todas las imágenes
    print("1️⃣  Escaneando imágenes en data/raw/...")
    images = get_all_images()
    print(f"   Encontradas {len(images)} imágenes")
    print()
    
    # 2. Dividir en splits
    print("2️⃣  Dividiendo en splits (seed=42)...")
    train_imgs, val_imgs, test_imgs = split_images(images)
    print()
    
    # 3. Copiar imágenes
    print("3️⃣  Copiando imágenes a splits...")
    copy_images_to_splits(train_imgs, val_imgs, test_imgs)
    print()
    
    # 4. Copiar etiquetas
    print("4️⃣  Copiando etiquetas a splits...")
    img_to_split = copy_labels_to_splits(train_imgs, val_imgs, test_imgs)
    print()
    
    # 5. Limpiar labels
    print("5️⃣  Limpiando directorio de etiquetas...")
    clean_labels_directory()
    print()
    
    # 6. Actualizar CSV metadata
    print("6️⃣  Actualizando metadata CSV...")
    update_metadata_csv(img_to_split)
    print()
    
    # 7. Crear dataset_index.csv
    print("7️⃣  Creando dataset_index.csv...")
    create_dataset_index(img_to_split)
    print()
    
    print("=" * 70)
    print("✅ DIVISIÓN DE DATASET COMPLETADA")
    print("=" * 70)
    print()
    print("Resumen:")
    print(f"  Train: {len(train_imgs)} imágenes")
    print(f"  Val: {len(val_imgs)} imágenes")
    print(f"  Test: {len(test_imgs)} imágenes")
    print(f"  Total: {len(images)} imágenes")
    print()
    print("Próximos pasos:")
    print("  1. Ejecutar: python validar_consistencia_dataset.py")
    print("  2. Verificar que todas las validaciones pasen")


if __name__ == '__main__':
    main()