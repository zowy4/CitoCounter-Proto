#!/usr/bin/env python3
"""
Script para comparar etiquetado entre dos anotadores (CITO-71).

Uso: python comparar_etiquetado.py --imagen IMG_001 --annotator1 annotator1.txt --annotator2 annotator2.txt
"""

import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='Comparar etiquetado entre dos anotadores')
    parser.add_argument('--imagen', required=True, help='Nombre de la imagen (ej. IMG_001)')
    parser.add_argument('--annotator1', required=True, help='Archivo de etiquetado del anotador 1')
    parser.add_argument('--annotator2', required=True, help='Archivo de etiquetado del anotador 2')
    parser.add_argument('--labels-dir', default='/workspaces/CitoCounter-Proto/CitoDataset_v1/labels', 
        help='Directorio de etiquetas (default: CitoDataset_v1/labels)')
    args = parser.parse_args()
    
    # Cargar etiquetas del anotador 1
    annotator1_path = os.path.join(args.labels_dir, f"{args.annotator1}")
    annotator2_path = os.path.join(args.labels_dir, f"{args.annotator2}")
    
    print(f"Comparando: {annotator1_path} vs {annotator2_path}")
    print(f"Imagen: {args.imagen}")
    print("=" * 60)
    
    # Verificar que los archivos existen
    if not os.path.exists(annotator1_path):
        print(f"❌ Error: Archivo del anotador 1 no encontrado: {annotator1_path}")
        sys.exit(1)
    
    if not os.path.exists(annotator2_path):
        print(f"❌ Error: Archivo del anotador 2 no encontrado: {annotator2_path}")
        sys.exit(1)
    
    # Leer etiquetas
    with open(annotator1_path, 'r', encoding='utf-8') as f:
        annotator1_lines = f.readlines()
    
    with open(annotator2_path, 'r', encoding='utf-8') as f:
        annotator2_lines = f.readlines()
    
    print(f"Número de líneas en anotador 1: {len(annotator1_lines)}")
    print(f"Número de líneas en anotador 2: {len(annotator2_lines)}")
    print()
    
    # Parsear etiquetas YOLO (clase x_center y_center width height)
    def parse_yolo_labels(lines):
        labels = []
        for line in lines:
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                    labels.append({
                        'class': class_id,
                        'x_center': x_center,
                        'y_center': y_center,
                        'width': width,
                        'height': height
                    })
        return labels
    
    labels1 = parse_yolo_labels(annotator1_lines)
    labels2 = parse_yolo_labels(annotator2_lines)
    
    print(f"Etiquetas anotador 1: {len(labels1)}")
    print(f"Etiquetas anotador 2: {len(labels2)}")
    print()
    
    # Comparar clases
    print("=== Comparación de clases ===")
    class_matches = 0
    class_mismatches = 0
    
    # Crear diccionario por imagen para el anotador 2
    labels2_by_class = {}
    for label in labels2:
        cls = label['class']
        if cls not in labels2_by_class:
            labels2_by_class[cls] = 0
        labels2_by_class[cls] += 1
    
    for label in labels1:
        cls = label['class']
        if cls in labels2_by_class and labels2_by_class[cls] > 0:
            class_matches += 1
            labels2_by_class[cls] -= 1
        else:
            class_mismatches += 1
    
    print(f"Clases en acuerdo: {class_matches}")
    print(f"Clases en desacuerdo: {class_mismatches}")
    print()
    
    # Comparar ubicaciones (simplificado: misma clase = posible acuerdo)
    # Para un análisis completo, se compararía la posición de las cajas
    
    # Resumen
    total1 = len(labels1)
    total2 = len(labels2)
    agreement = class_matches
    disagreement = class_mismatches
    
    simple_accuracy = agreement / max(total1 + total2 - agreement, 1) * 100 if (total1 + total2 - agreement) > 0 else 0
    
    print("=== Resumen ===")
    print(f"Total etiquetas anotador 1: {total1}")
    print(f"Total etiquetas anotador 2: {total2}")
    print(f"Acuerdo de clases: {agreement}")
    print(f"Desacuerdo de clases: {disagreement}")
    print(f"Exactitud simple: {simple_accuracy:.1f}%")
    print()
    
    # Calcular Kappa de Cohen
    # Para simplificar: proportion agreement - expected agreement / 1 - expected agreement
    # Esto es una simplificación - kappa verdadero requiere tablas de contingencia
    
    po = agreement / max(total1 + total2 - agreement, 1)  # Observed agreement
    
    # Expected agreement by chance (simplificado)
    # Asumimos distribución uniforme para este ejemplo
    if total1 > 0 and total2 > 0:
        pe = (total1 / (total1 + total2)) * (total2 / (total1 + total2)) * 2  # Simplificación
    else:
        pe = 0
    
    kappa = (po - pe) / max(1 - pe, 0.001) if pe < 1 else 0
    
    print("=== Kappa de Cohen ===")
    print(f"Po (acuerdo observado): {po:.4f}")
    print(f"Pe (acuerdo esperado): {pe:.4f}")
    print(f"Kappa de Cohen: {kappa:.4f}")
    print(f"Interpretación: {'Casi perfecta (≥ 0.81)' if kappa >= 0.81 else 'Substantial (0.61-0.80)' if kappa >= 0.61 else 'Moderada (0.41-0.60)' if kappa >= 0.41 else 'Baja (≤ 0.40)'}")
    
    return kappa

if __name__ == '__main__':
    main()