#!/usr/bin/env python3
"""
Script para organizar dataset según dataset_index.csv (CITO-96).
Mueve imágenes Y labels a los splits correctos según el índice.
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

def mover_a_split_correcto():
    """Mueve imágenes y labels a su split correcto según dataset_index.csv."""
    asignaciones = leer_asignaciones()
    print(f"📋 Asignaciones en dataset_index.csv: {len(asignaciones)}")
    
    movidos = {'train': 0, 'val': 0, 'test': 0}
    errores = []
    
    for split_origen in ['train', 'val', 'test']:
        img_dir_origen = IMAGES_SPLITS[split_origen]
        lbl_dir_origen = LABELS_SPLITS[split_origen]
        
        if not img_dir_origen.exists():
            continue
            
        for img_file in img_dir_origen.glob('*.jpg'):
            id_imagen = img_file.stem
            split_correcto = asignaciones.get(id_imagen)
            
            if not split_correcto:
                errores.append(f"Imagen {id_imagen} no está en dataset_index.csv")
                continue
            
            if split_correcto == split_origen:
                continue  # Ya está en el split correcto
            
            # Mover imagen
            dst_img_dir = IMAGES_SPLITS[split_correcto]
            dst_img = dst_img_dir / f"{id_imagen}.jpg"
            shutil.move(str(img_file), str(dst_img))
            
            # Mover label si existe
            lbl_file_origen = lbl_dir_origen / f"{id_imagen}.txt"
            lbl_file_destino = LABELS_SPLITS[split_correcto] / f"{id_imagen}.txt"
            
            if lbl_file_origen.exists():
                shutil.move(str(lbl_file_origen), str(lbl_file_destino))
                movidos[split_correcto] += 1
            else:
                errores.append(f"Label no encontrado para {id_imagen} en {split_origen}")
    
    print(f"\n✅ Movidos: train={movidos['train']}, val={movidos['val']}, test={movidos['test']}")
    
    if errores:
        print(f"\n❌ Errores ({len(errores)}):")
        for e in errores[:20]:
            print(f"   {e}")
    
    return movidos, errores

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
    
    # Paso 1: Mover imágenes y labels a splits correctos
    print("📋 PASO 1: Moviendo imágenes y labels a splits correctos")
    movidos, errores_mover = mover_a_split_correcto()
    
    # Paso 2: Verificar integridad
    print("\n📋 PASO 2: Verificando integridad imagen-label")
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