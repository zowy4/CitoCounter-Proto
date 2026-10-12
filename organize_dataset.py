#!/usr/bin/env python3
"""
Script para organizar dataset según dataset_index.csv (CITO-96).
Copia imágenes desde data/raw/ a los splits train/val/test según el índice.
"""

import os
import shutil
from pathlib import Path

# Configuración
DATASET_INDEX = Path('CitoDataset_v1/dataset_index.csv')
IMAGES_ROOT = Path('data/raw')
IMAGES_SPLITS = {
    'train': IMAGES_ROOT / 'train',
    'val': IMAGES_ROOT / 'val',
    'test': IMAGES_ROOT / 'test',
}
LABELS_SPLITS = {
    'train': Path('CitoDataset_v1/labels/train'),
    'val': Path('CitoDataset_v1/labels/val'),
    'test': Path('CitoDataset_v1/labels/test'),
}

def leer_asignaciones():
    """Lee el dataset_index.csv y retorna dict {id_imagen: split}."""
    asignaciones = {}
    with open(DATASET_INDEX, 'r') as f:
        next(f)  # Saltar header
        for linea in f:
            partes = linea.strip().split(',')
            if len(partes) >= 3:
                id_imagen = partes[0]
                split = partes[2]
                asignaciones[id_imagen] = split
    return asignaciones

def organizar_dataset():
    """Organiza imágenes según dataset_index.csv."""
    asignaciones = leer_asignaciones()
    print(f"📋 Asignaciones en dataset_index.csv: {len(asignaciones)}")
    
    # Contar imágenes en raíz
    imagenes_raiz = list(IMAGES_ROOT.glob('*.jpg'))
    print(f"📁 Imágenes en data/raw/: {len(imagenes_raiz)}")
    
    # Crear directorios de splits si no existen
    for split_dir in IMAGES_SPLITS.values():
        split_dir.mkdir(parents=True, exist_ok=True)
    
    # Copiar cada imagen a su split correspondiente
    copiados = {'train': 0, 'val': 0, 'test': 0}
    errores = []
    
    for id_imagen, split in asignaciones.items():
        src = IMAGES_ROOT / f"{id_imagen}.jpg"
        dst_dir = IMAGES_SPLITS[split]
        dst = dst_dir / f"{id_imagen}.jpg"
        
        if not src.exists():
            errores.append(f"Imagen no encontrada en raíz: {id_imagen}.jpg")
            continue
        
        # Copiar si no existe o es diferente
        if not dst.exists():
            shutil.copy2(src, dst)
            copiados[split] += 1
        else:
            # Verificar si son el mismo archivo
            if src.stat().st_size != dst.stat().st_size:
                print(f"  ⚠️  {id_imagen}: archivo en {split} tiene tamaño diferente, sobrescribiendo")
                shutil.copy2(src, dst)
                copiados[split] += 1
    
    print(f"\n✅ Copiados: train={copiados['train']}, val={copiados['val']}, test={copiados['test']}")
    
    if errores:
        print(f"\n❌ Errores ({len(errores)}):")
        for e in errores[:10]:
            print(f"   {e}")
        if len(errores) > 10:
            print(f"   ... y {len(errores) - 10} más")
    
    return copiados, errores

def limpiar_splits_incorrectos():
    """Elimina imágenes de splits donde no deberían estar según dataset_index.csv."""
    asignaciones = leer_asignaciones()
    
    eliminados = {'train': 0, 'val': 0, 'test': 0}
    
    for split in ['train', 'val', 'test']:
        img_dir = IMAGES_SPLITS[split]
        lbl_dir = LABELS_SPLITS[split]
        
        if not img_dir.exists():
            continue
            
        for img_file in img_dir.glob('*.jpg'):
            id_imagen = img_file.stem
            split_correcto = asignaciones.get(id_imagen)
            
            if split_correcto and split_correcto != split:
                lbl_file = lbl_dir / f"{id_imagen}.txt"
                print(f"  Eliminando {id_imagen} de {split} (debe estar en {split_correcto})")
                img_file.unlink()
                eliminados[split] += 1
                if lbl_file.exists():
                    lbl_file.unlink()
    
    print(f"\n🗑️  Eliminados de splits incorrectos: train={eliminados['train']}, val={eliminados['val']}, test={eliminados['test']}")
    return eliminados

def verificar_integridad():
    """Verifica que cada imagen en splits tenga su label y viceversa."""
    print("\n🔍 Verificando integridad imagen-label...")
    errores = []
    
    for split in ['train', 'val', 'test']:
        img_dir = IMAGES_SPLITS[split]
        lbl_dir = LABELS_SPLITS[split]
        
        if not img_dir.exists() or not lbl_dir.exists():
            continue
        
        imagenes = {f.stem for f in img_dir.glob('*.jpg')}
        labels = {f.stem for f in lbl_dir.glob('*.txt')}
        
        # Imágenes sin label
        for img_id in imagenes - labels:
            errores.append(f"{split}: Imagen sin label: {img_id}")
        
        # Labels sin imagen
        for lbl_id in labels - imagenes:
            errores.append(f"{split}: Label sin imagen: {lbl_id}")
    
    if errores:
        print(f"❌ Errores de integridad ({len(errores)}):")
        for e in errores[:20]:
            print(f"   {e}")
    else:
        print("✅ Todas las imágenes tienen su label y viceversa")
    
    return errores

def main():
    print("=" * 70)
    print("📦 ORGANIZACIÓN DE DATASET SEGÚN DATASET_INDEX.CSV - CITO-96")
    print("=" * 70)
    print()
    
    # Paso 1: Copiar imágenes desde raíz a splits
    print("📋 PASO 1: Copiando imágenes a splits según dataset_index.csv")
    copiados, errores_copia = organizar_dataset()
    
    # Paso 2: Limpiar duplicados en splits incorrectos
    print("\n📋 PASO 2: Limpiando duplicados en splits incorrectos")
    eliminados = limpiar_splits_incorrectos()
    
    # Paso 3: Verificar integridad
    print("\n📋 PASO 3: Verificando integridad imagen-label")
    errores_integridad = verificar_integridad()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL")
    print("=" * 70)
    for split in ['train', 'val', 'test']:
        img_count = len(list(IMAGES_SPLITS[split].glob('*.jpg'))) if IMAGES_SPLITS[split].exists() else 0
        lbl_count = len(list(LABELS_SPLITS[split].glob('*.txt'))) if LABELS_SPLITS[split].exists() else 0
        print(f"   {split}: {img_count} imágenes, {lbl_count} labels")
    
    total_imgs = sum(len(list(IMAGES_SPLITS[s].glob('*.jpg'))) for s in ['train', 'val', 'test'] if IMAGES_SPLITS[s].exists())
    total_lbls = sum(len(list(LABELS_SPLITS[s].glob('*.txt'))) for s in ['train', 'val', 'test'] if LABELS_SPLITS[s].exists())
    print(f"\n   TOTAL: {total_imgs} imágenes, {total_lbls} labels")
    print(f"   Esperado (dataset_index.csv): 2000")
    
    if total_imgs == 2000 and total_lbls == 2000 and not errores_integridad:
        print("\n🎉 DATASET ORGANIZADO CORRECTAMENTE - CITO-96 COMPLETADO")
    else:
        print("\n⚠️  REVISAR: Hay discrepancias que requieren atención")
    
    print("=" * 70)

if __name__ == '__main__':
    main()