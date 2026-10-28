#!/usr/bin/env python3
"""
Evaluación CITO-23 en validation split (400 imágenes).
"""

import argparse
import csv
import math
from pathlib import Path
import cv2
import numpy as np

from src.preprocessing import preprocesar_imagen
from src.dog_filter import aplicar_filtro_dog
from src.analysis import analizar_nucleos


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

VAL_IMAGES_DIR = Path('data/raw/val')
VAL_LABELS_DIR = Path('CitoDataset_v1/labels/val')
DEFAULT_MATCH_DISTANCE = 10.0

# Parámetros calibrados CITO-74 (mejores para imágenes sintéticas)
# Para imágenes reales se usa polaridad 'nucleos-oscuros' con parámetros específicos
from src.analysis import (
    AREA_MINIMA_NUCLEO, AREA_MAXIMA_NUCLEO, UMBRAL_DOG,
    AREA_PROMEDIO_NUCLEO_NORMAL, FACTOR_RIESGO
)

# Parámetros calibrados CITO-74
CALIBRATED_SIGMA1 = 7.0
CALIBRATED_SIGMA2 = 8.0
CALIBRATED_UMBRAL_DOG = UMBRAL_DOG  # 5
CALIBRATED_AREA_MIN_CLAROS = AREA_MINIMA_NUCLEO['nucleos-claros']  # 10
CALIBRATED_AREA_MAX_CLAROS = AREA_MAXIMA_NUCLEO['nucleos-claros']  # 500
CALIBRATED_AREA_MIN_OSCUROS = AREA_MINIMA_NUCLEO['nucleos-oscuros']  # 100
CALIBRATED_AREA_MAX_OSCUROS = AREA_MAXIMA_NUCLEO['nucleos-oscuros']  # 300000

# Parámetros optimizados para imágenes reales (CITO-97)
REAL_UMBRAL_DOG = 50  # Umbral más alto para imágenes reales
REAL_AREA_MIN_OSCUROS = 100  # Mismo mínimo
REAL_AREA_MAX_OSCUROS = 300000  # Mismo máximo


def yolo_to_centroids(label_path, image_shape):
    h, w = image_shape[:2]
    centroids = []
    
    if not label_path.exists():
        return centroids
    
    with open(label_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 5:
                continue
            try:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                x_px = x_center * w
                y_px = y_center * h
                centroids.append((x_px, y_px))
            except ValueError:
                continue
    
    return centroids


def extract_predicted_centroids(resultados):
    centroids = []
    
    for contorno in resultados.get('contornos_normales', []) + resultados.get('contornos_sospechosos', []):
        M = cv2.moments(contorno)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroids.append((cx, cy))
    
    return centroids


def calcular_tp_fp_fn_por_emparejamiento(pred_centroids, gt_centroids, distancia_max):
    if not pred_centroids and not gt_centroids:
        return 0, 0, 0

    if distancia_max <= 0:
        return 0, len(pred_centroids), len(gt_centroids)

    candidatos = []
    for pred_idx, (px, py) in enumerate(pred_centroids):
        for gt_idx, (gx, gy) in enumerate(gt_centroids):
            distancia = math.hypot(px - gx, py - gy)
            if distancia <= distancia_max:
                candidatos.append((distancia, pred_idx, gt_idx))

    candidatos.sort(key=lambda item: item[0])
    pred_usados = set()
    gt_usados = set()
    tp = 0

    for _, pred_idx, gt_idx in candidatos:
        if pred_idx in pred_usados or gt_idx in gt_usados:
            continue
        pred_usados.add(pred_idx)
        gt_usados.add(gt_idx)
        tp += 1

    fp = len(pred_centroids) - tp
    fn = len(gt_centroids) - tp
    return tp, fp, fn


def calcular_precision(tp, fp):
    total = tp + fp
    if total == 0:
        return 0.0
    return tp / total


def calcular_recall(tp, fn):
    total = tp + fn
    if total == 0:
        return 0.0
    return tp / total


def calcular_f1(p, r):
    if p + r == 0:
        return 0.0
    return 2 * (p * r) / (p + r)


def calcular_jaccard(tp, fp, fn):
    total = tp + fp + fn
    if total == 0:
        return 0.0
    return tp / total


def detectar_tipo_imagen(image_path):
    """Detecta si la imagen es real (2048x1536) o sintética (100x100)."""
    imagen = cv2.imread(str(image_path))
    if imagen is None:
        return 'sintetica'
    h, w = imagen.shape[:2]
    if w > 1000:
        return 'real'
    return 'sintetica'


def evaluar_imagen(image_path, label_path, match_distance):
    imagen = cv2.imread(str(image_path))
    if imagen is None:
        return None
    
    h, w = imagen.shape[:2]
    gt_centroids = yolo_to_centroids(label_path, (h, w))
    
    # Detectar tipo de imagen y elegir polaridad
    tipo = detectar_tipo_imagen(image_path)
    polaridad = 'nucleos-oscuros' if tipo == 'real' else 'nucleos-claros'
    
    try:
        imagen_gris, imagen_original = preprocesar_imagen(
            str(image_path),
            mejorar_contraste_flag=True,
            reducir_ruido_flag=False,
            metodo_contraste='clahe',
            polaridad=polaridad
        )
        
        imagen_dog = aplicar_filtro_dog(
            imagen_gris,
            sigma1=CALIBRATED_SIGMA1,
            sigma2=CALIBRATED_SIGMA2
        )
        
        import src.analysis as analysis_module
        old_umbral = analysis_module.UMBRAL_DOG
        old_area_min = analysis_module.AREA_MINIMA_NUCLEO
        old_area_max = analysis_module.AREA_MAXIMA_NUCLEO
        
        # Usar parámetros específicos según el tipo de imagen
        if tipo == 'real':
            analysis_module.UMBRAL_DOG = REAL_UMBRAL_DOG
            analysis_module.AREA_MINIMA_NUCLEO = {'nucleos-claros': CALIBRATED_AREA_MIN_CLAROS, 'nucleos-oscuros': REAL_AREA_MIN_OSCUROS}
            analysis_module.AREA_MAXIMA_NUCLEO = {'nucleos-claros': CALIBRATED_AREA_MAX_CLAROS, 'nucleos-oscuros': REAL_AREA_MAX_OSCUROS}
        else:
            analysis_module.UMBRAL_DOG = CALIBRATED_UMBRAL_DOG
            analysis_module.AREA_MINIMA_NUCLEO = {'nucleos-claros': CALIBRATED_AREA_MIN_CLAROS, 'nucleos-oscuros': CALIBRATED_AREA_MIN_OSCUROS}
            analysis_module.AREA_MAXIMA_NUCLEO = {'nucleos-claros': CALIBRATED_AREA_MAX_CLAROS, 'nucleos-oscuros': CALIBRATED_AREA_MAX_OSCUROS}
        
        resultados = analizar_nucleos(
            imagen_dog, 
            imagen_original, 
            polaridad=polaridad,
            usar_mascara_borde=True,
            ancho_borde=50
        )
        
        analysis_module.UMBRAL_DOG = old_umbral
        analysis_module.AREA_MINIMA_NUCLEO = old_area_min
        analysis_module.AREA_MAXIMA_NUCLEO = old_area_max
        
        pred_centroids = extract_predicted_centroids(resultados)
        
        tp, fp, fn = calcular_tp_fp_fn_por_emparejamiento(
            pred_centroids, gt_centroids, match_distance
        )
        
        precision = calcular_precision(tp, fp)
        recall = calcular_recall(tp, fn)
        f1 = calcular_f1(precision, recall)
        jaccard = calcular_jaccard(tp, fp, fn)
        
        return {
            'image_id': image_path.name,
            'tipo': tipo,
            'polaridad': polaridad,
            'tp': tp,
            'fp': fp,
            'fn': fn,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'jaccard': jaccard,
            'pred_count': len(pred_centroids),
            'gt_count': len(gt_centroids),
            'pred_centroids': pred_centroids,
            'gt_centroids': gt_centroids,
        }
        
    except Exception as e:
        print(f"   ❌ Error procesando {image_path.name}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Evaluación CITO-23 en validation split')
    parser.add_argument('--match-distance', type=float, default=DEFAULT_MATCH_DISTANCE)
    parser.add_argument('--output-dir', type=Path, default=Path('data/results'))
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()
    
    if args.match_distance <= 0:
        raise ValueError('La distancia de emparejamiento debe ser mayor que cero.')
    
    val_images = sorted(VAL_IMAGES_DIR.glob('*.jpg'))
    if args.limit:
        val_images = val_images[:args.limit]
    
    print(f"🔬 EVALUACIÓN CITO-23 - Validation Split (400 imágenes)")
    print(f"   Imágenes a evaluar: {len(val_images)}")
    print(f"   Parámetros: σ1=7.0, σ2=8.0, UMBRAL_DOG={CALIBRATED_UMBRAL_DOG} (sintéticas) / {REAL_UMBRAL_DOG} (reales), AREA_MIN={CALIBRATED_AREA_MIN_CLAROS}/{REAL_AREA_MIN_OSCUROS}, AREA_MAX={CALIBRATED_AREA_MAX_CLAROS}/{REAL_AREA_MAX_OSCUROS}")
    print(f"   Distancia de emparejamiento: {args.match_distance} px")
    print(f"   Polaridad: nucleos-claros (sintéticas), nucleos-oscuros (reales)")
    print()
    
    results = []
    total_tp = total_fp = total_fn = 0
    synth_tp = synth_fp = synth_fn = 0
    real_tp = real_fp = real_fn = 0
    
    for i, image_path in enumerate(val_images, 1):
        label_path = VAL_LABELS_DIR / f"{image_path.stem}.txt"
        
        if not label_path.exists():
            print(f"   [{i}/{len(val_images)}] {image_path.name}: ⚠️ Sin ground truth")
            continue
        
        print(f"   [{i}/{len(val_images)}] {image_path.name}...", end=' ')
        
        result = evaluar_imagen(image_path, label_path, args.match_distance)
        
        if result is None:
            print("❌ Error")
            continue
        
        results.append(result)
        total_tp += result['tp']
        total_fp += result['fp']
        total_fn += result['fn']
        
        if result['tipo'] == 'sintetica':
            synth_tp += result['tp']
            synth_fp += result['fp']
            synth_fn += result['fn']
        else:
            real_tp += result['tp']
            real_fp += result['fp']
            real_fn += result['fn']
        
        print(f"TP={result['tp']} FP={result['fp']} FN={result['fn']} "
              f"P={result['precision']:.3f} R={result['recall']:.3f} F1={result['f1']:.3f} J={result['jaccard']:.3f}")
    
    precision_global = calcular_precision(total_tp, total_fp)
    recall_global = calcular_recall(total_tp, total_fn)
    f1_global = calcular_f1(precision_global, recall_global)
    jaccard_global = calcular_jaccard(total_tp, total_fp, total_fn)
    
    # Métricas por tipo
    synth_precision = calcular_precision(synth_tp, synth_fp)
    synth_recall = calcular_recall(synth_tp, synth_fn)
    synth_f1 = calcular_f1(synth_precision, synth_recall)
    synth_jaccard = calcular_jaccard(synth_tp, synth_fp, synth_fn)
    
    real_precision = calcular_precision(real_tp, real_fp)
    real_recall = calcular_recall(real_tp, real_fn)
    real_f1 = calcular_f1(real_precision, real_recall)
    real_jaccard = calcular_jaccard(real_tp, real_fp, real_fn)
    
    print()
    print("=" * 70)
    print("📊 RESUMEN GLOBAL CITO-23 - VALIDATION SPLIT")
    print("=" * 70)
    print(f"Imágenes evaluadas: {len(results)}")
    print(f"TP total: {total_tp}")
    print(f"FP total: {total_fp}")
    print(f"FN total: {total_fn}")
    print(f"Precision: {precision_global:.4f}")
    print(f"Recall / Sensitivity: {recall_global:.4f}")
    print(f"F1-Score: {f1_global:.4f}")
    print(f"Jaccard / IoU detección: {jaccard_global:.4f}")
    print()
    print("📊 POR TIPO DE IMAGEN:")
    print(f"  Sintéticas (375): TP={synth_tp} FP={synth_fp} FN={synth_fn} "
          f"P={synth_precision:.4f} R={synth_recall:.4f} F1={synth_f1:.4f} J={synth_jaccard:.4f}")
    print(f"  Reales 2048x1536 (25): TP={real_tp} FP={real_fp} FN={real_fn} "
          f"P={real_precision:.4f} R={real_recall:.4f} F1={real_f1:.4f} J={real_jaccard:.4f}")
    print("=" * 70)
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / 'CITO-23-evaluacion-val-original.csv'
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'image_id', 'tipo', 'polaridad', 'tp', 'fp', 'fn', 'precision', 'recall', 'f1', 'jaccard',
            'pred_count', 'gt_count', 'pred_centroids', 'gt_centroids', 'match_distance_px'
        ])
        for r in results:
            pred_str = ';'.join(f"{x}:{y}" for x, y in r['pred_centroids'])
            gt_str = ';'.join(f"{x}:{y}" for x, y in r['gt_centroids'])
            writer.writerow([
                r['image_id'], r['tipo'], r['polaridad'], r['tp'], r['fp'], r['fn'],
                f"{r['precision']:.6f}", f"{r['recall']:.6f}", f"{r['f1']:.6f}", f"{r['jaccard']:.6f}",
                r['pred_count'], r['gt_count'], pred_str, gt_str, args.match_distance
            ])
    
    txt_path = args.output_dir / 'CITO-23-evaluacion-val-original-resumen.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"CITO-23 - Evaluación en validation split (400 imágenes)\n")
        f.write(f"========================================================\n")
        f.write(f"Parámetros: σ1=7.0, σ2=8.0, UMBRAL_DOG={CALIBRATED_UMBRAL_DOG} (sintéticas) / {REAL_UMBRAL_DOG} (reales), AREA_MIN={CALIBRATED_AREA_MIN_CLAROS}/{REAL_AREA_MIN_OSCUROS}, AREA_MAX={CALIBRATED_AREA_MAX_CLAROS}/{REAL_AREA_MAX_OSCUROS}\n")
        f.write(f"Distancia de emparejamiento: {args.match_distance} px\n")
        f.write(f"Máscara de borde: SÍ (adaptativa)\n")
        f.write(f"Polaridad: nucleos-claros (sintéticas), nucleos-oscuros (reales)\n")
        f.write(f"\n")
        f.write(f"Imágenes evaluadas: {len(results)}\n")
        f.write(f"TP total: {total_tp}\n")
        f.write(f"FP total: {total_fp}\n")
        f.write(f"FN total: {total_fn}\n")
        f.write(f"Precision: {precision_global:.4f}\n")
        f.write(f"Recall / Sensitivity: {recall_global:.4f}\n")
        f.write(f"F1-Score: {f1_global:.4f}\n")
        f.write(f"Jaccard / IoU detección: {jaccard_global:.4f}\n")
        f.write(f"\n")
        f.write(f"POR TIPO DE IMAGEN:\n")
        f.write(f"  Sintéticas (375): TP={synth_tp} FP={synth_fp} FN={synth_fn} "
                f"P={synth_precision:.4f} R={synth_recall:.4f} F1={synth_f1:.4f} J={synth_jaccard:.4f}\n")
        f.write(f"  Reales 2048x1536 (25): TP={real_tp} FP={real_fp} FN={real_fn} "
                f"P={real_precision:.4f} R={real_recall:.4f} F1={real_f1:.4f} J={real_jaccard:.4f}\n")
        f.write(f"\n")
        f.write(f"Detalle por imagen:\n")
        for r in results:
            f.write(f"{r['image_id']} ({r['tipo']}, {r['polaridad']}): tp={r['tp']} fp={r['fp']} fn={r['fn']} "
                    f"P={r['precision']:.4f} R={r['recall']:.4f} F1={r['f1']:.4f} J={r['jaccard']:.4f}\n")
    
    print(f"\n✅ Resultados guardados en:")
    print(f"   CSV: {csv_path}")
    print(f"   TXT: {txt_path}")
    
    if total_tp == 0 and (total_fp > 0 or total_fn > 0):
        estado = 'EN CURSO - Sin verdaderos positivos'
    elif total_tp == 0 and total_fp == 0 and total_fn == 0:
        estado = 'EN CURSO - Sin detecciones ni referencias'
    else:
        estado = 'EN REVISION - Métricas calculadas con detecciones válidas'
    
    print(f"\nEstado recomendado: {estado}")
    
    return {
        'total_tp': total_tp,
        'total_fp': total_fp,
        'total_fn': total_fn,
        'precision': precision_global,
        'recall': recall_global,
        'f1': f1_global,
        'jaccard': jaccard_global,
        'images_evaluated': len(results),
        'estado': estado,
    }


if __name__ == '__main__':
    main()