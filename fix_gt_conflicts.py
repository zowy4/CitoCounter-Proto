#!/usr/bin/env python3
"""
Script para corregir conflictos en ground truth YOLO (CITO-23).
Cuando hay clase 0 y clase 1 en el mismo centroide, mantener solo clase 1 (Anormal).
"""

from pathlib import Path

LABELS_DIR = Path('CitoDataset_v1/labels')

def corregir_conflictos_centroide(label_path):
    """Corrige conflictos donde clase 0 y 1 comparten el mismo centroide."""
    if not label_path.exists():
        return 0
    
    with open(label_path, 'r') as f:
        lineas = f.readlines()
    
    # Parsear líneas
    anotaciones = []
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
        partes = linea.split()
        if len(partes) >= 5:
            clase = int(partes[0])
            x_center = float(partes[1])
            y_center = float(partes[2])
            ancho = float(partes[3])
            alto = float(partes[4])
            anotaciones.append({
                'clase': clase,
                'x': x_center,
                'y': y_center,
                'w': ancho,
                'h': alto,
                'original': linea
            })
    
    # Detectar conflictos: mismo centroide, clases diferentes
    centroides = {}
    for ann in anotaciones:
        key = (round(ann['x'], 6), round(ann['y'], 6))
        if key not in centroides:
            centroides[key] = []
        centroides[key].append(ann)
    
    # Resolver conflictos: mantener solo clase 1 (Anormal) en centroides conflictivos
    lineas_finales = []
    conflictos_resueltos = 0
    
    for key, anns in centroides.items():
        if len(anns) == 1:
            lineas_finales.append(anns[0]['original'])
        else:
            # Hay conflicto: múltiples clases en mismo centroide
            # Mantener solo clase 1 (Anormal) que es la más importante para detección
            clase_1 = [a for a in anns if a['clase'] == 1]
            if clase_1:
                lineas_finales.append(clase_1[0]['original'])
                conflictos_resueltos += len(anns) - 1
                print(f"  Conflicto resuelto en {label_path.name}: centroide {key} - mantenida clase 1, eliminadas {len(anns)-1} anotaciones")
            else:
                # Si no hay clase 1, mantener la primera
                lineas_finales.append(anns[0]['original'])
                conflictos_resueltos += len(anns) - 1
    
    if conflictos_resueltos > 0:
        with open(label_path, 'w') as f:
            for linea in lineas_finales:
                f.write(linea + '\n')
    
    return conflictos_resueltos

def main():
    print("=" * 70)
    print("🔧 CORRECCIÓN DE CONFLICTOS EN GROUND TRUTH - CITO-23")
    print("=" * 70)
    print("Regla: Cuando clase 0 y 1 comparten centroide, mantener solo clase 1 (Anormal)")
    print()
    
    splits = ['train', 'val', 'test']
    total_conflictos = 0
    
    for split in splits:
        split_dir = LABELS_DIR / split
        if not split_dir.exists():
            continue
        
        print(f"\n📁 Procesando split: {split}")
        archivos = list(split_dir.glob('*.txt'))
        
        for label_path in archivos:
            conflictos = corregir_conflictos_centroide(label_path)
            total_conflictos += conflictos
    
    print("\n" + "=" * 70)
    print(f"✅ CORRECCIÓN COMPLETADA")
    print(f"   Total conflictos resueltos: {total_conflictos}")
    print("=" * 70)

if __name__ == '__main__':
    main()