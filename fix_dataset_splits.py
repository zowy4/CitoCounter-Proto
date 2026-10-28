#!/usr/bin/env python3
"""
Script para corregir duplicados en splits del dataset (CITO-96).
Mantiene cada imagen/label solo en el split asignado en dataset_index.csv.
"""

import os
import shutil
from pathlib import Path

# Configuración
DATASET_INDEX = Path('CitoDataset_v1/dataset_index.csv')
IMAGES_BASE = Path('data/raw')
LABELS_BASE = Path('CitoDataset_v1/labels')

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

def corregir_duplicados():
    """Elimina imágenes y labels de splits incorrectos."""
    asignaciones = leer_asignaciones()
    
    splits = ['train', 'val', 'test']
    eliminados = {'imagenes': 0, 'labels': 0}
    
    for split in splits:
        img_dir = IMAGES_BASE / split
        lbl_dir = LABELS_BASE / split
        
        if not img_dir.exists() or not lbl_dir.exists():
            continue
            
        # Revisar cada imagen en este split
        for img_file in img_dir.glob('*.jpg'):
            id_imagen = img_file.stem
            split_correcto = asignaciones.get(id_imagen)
            
            if split_correcto and split_correcto != split:
                # Esta imagen está en el split incorrecto, eliminarla
                lbl_file = lbl_dir / f"{id_imagen}.txt"
                
                print(f"  Eliminando {id_imagen} de {split} (debe estar en {split_correcto})")
                img_file.unlink()
                eliminados['imagenes'] += 1
                
                if lbl_file.exists():
                    lbl_file.unlink()
                    eliminados['labels'] += 1
    
    return eliminados

def main():
    print("=" * 70)
    print("🔧 CORRECCIÓN DE DUPLICADOS EN SPLITS - CITO-96")
    print("=" * 70)
    print()
    
    # Leer asignaciones correctas
    asignaciones = leer_asignaciones()
    print(f"📋 Asignaciones leídas del dataset_index.csv: {len(asignaciones)} entradas")
    
    # Contar antes
    print("\n📊 Conteo ANTES de la corrección:")
    for split in ['train', 'val', 'test']:
        img_count = len(list((IMAGES_BASE / split).glob('*.jpg'))) if (IMAGES_BASE / split).exists() else 0
        lbl_count = len(list((LABELS_BASE / split).glob('*.txt'))) if (LABELS_BASE / split).exists() else 0
        print(f"   {split}: {img_count} imágenes, {lbl_count} labels")
    
    # Corregir
    print("\n🧹 Eliminando duplicados...")
    eliminados = corregir_duplicados()
    
    # Contar después
    print("\n📊 Conteo DESPUÉS de la corrección:")
    for split in ['train', 'val', 'test']:
        img_count = len(list((IMAGES_BASE / split).glob('*.jpg'))) if (IMAGES_BASE / split).exists() else 0
        lbl_count = len(list((LABELS_BASE / split).glob('*.txt'))) if (LABELS_BASE / split).exists() else 0
        print(f"   {split}: {img_count} imágenes, {lbl_count} labels")
    
    print(f"\n✅ Eliminados: {eliminados['imagenes']} imágenes, {eliminados['labels']} labels")
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()