#!/usr/bin/env python3
"""
Script para limpiar duplicados en ground truth YOLO (CITO-23).
Elimina líneas duplicadas en archivos de etiquetas.
"""

from pathlib import Path

LABELS_DIR = Path('CitoDataset_v1/labels')

def limpiar_duplicados_en_archivo(label_path):
    """Elimina líneas duplicadas en un archivo de etiquetas."""
    if not label_path.exists():
        return 0
    
    with open(label_path, 'r') as f:
        lineas = f.readlines()
    
    # Eliminar duplicados manteniendo el orden
    lineas_unicas = []
    vistos = set()
    duplicados = 0
    
    for linea in lineas:
        linea_limpia = linea.strip()
        if linea_limpia and linea_limpia not in vistos:
            vistos.add(linea_limpia)
            lineas_unicas.append(linea)
        elif linea_limpia:
            duplicados += 1
    
    if duplicados > 0:
        with open(label_path, 'w') as f:
            f.writelines(lineas_unicas)
        print(f"  Limpiado {label_path.name}: {duplicados} duplicados eliminados")
    
    return duplicados

def main():
    print("=" * 70)
    print("🧹 LIMPIEZA DE DUPLICADOS EN GROUND TRUTH - CITO-23")
    print("=" * 70)
    
    splits = ['train', 'val', 'test']
    total_duplicados = 0
    
    for split in splits:
        split_dir = LABELS_DIR / split
        if not split_dir.exists():
            print(f"⚠️  Directorio no existe: {split_dir}")
            continue
        
        print(f"\n📁 Procesando split: {split}")
        archivos = list(split_dir.glob('*.txt'))
        print(f"   Archivos a revisar: {len(archivos)}")
        
        for label_path in archivos:
            duplicados = limpiar_duplicados_en_archivo(label_path)
            total_duplicados += duplicados
    
    print("\n" + "=" * 70)
    print(f"✅ LIMPIEZA COMPLETADA")
    print(f"   Total duplicados eliminados: {total_duplicados}")
    print("=" * 70)

if __name__ == '__main__':
    main()