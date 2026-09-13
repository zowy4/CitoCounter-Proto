#!/usr/bin/env python3
"""Calcula métricas de CITO-23 a partir del CSV de revisión manual.

Formato esperado por CSV:
image_id,reference_status,tp,fp,fn,precision,recall,f1,IoU,pred_centroids,gt_centroids,match_distance_px,notes
MUESTRA_001.jpg,manual_review_done,10,2,1,0.8333,0.9091,0.8696,0.7692,,,,ok

Si pred_centroids y gt_centroids tienen datos (x:y;x:y), el script calcula TP/FP/FN por emparejamiento espacial.
Si precision/recall/f1/IoU están vacíos, el script las calcula automáticamente.
"""

import csv
import math
from pathlib import Path

INPUT_PATH = Path('data/results/CITO-23-metricas-template.csv')
OUTPUT_PATH = Path('data/results/CITO-23-metricas-resumen.txt')
DEFAULT_MATCH_DISTANCE = 40.0


def safe_float(value):
    value = (value or '').strip()
    if value == '':
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def parsear_centroides(value):
    value = (value or '').strip()
    if value == '':
        return []

    puntos = []
    for item in value.split(';'):
        item = item.strip()
        if not item:
            continue
        if ':' not in item:
            continue
        x_str, y_str = item.split(':', 1)
        try:
            puntos.append((float(x_str.strip()), float(y_str.strip())))
        except ValueError:
            continue
    return puntos


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


def calcular_iou(tp, fp, fn):
    total = tp + fp + fn
    if total == 0:
        return 0.0
    return tp / total


def evaluar_calidad_resultados(total_tp, total_fp, total_fn, total_imagenes):
    if total_imagenes == 0:
        return (
            'EN CURSO',
            'Sin imágenes válidas para evaluación. Completa el CSV de CITO-23.'
        )

    if total_tp == 0 and (total_fp > 0 or total_fn > 0):
        return (
            'EN CURSO',
            'No hubo verdaderos positivos. Revisar emparejamiento espacial y referencia de verdad antes de cerrar CITO-23.'
        )

    if total_tp == 0 and total_fp == 0 and total_fn == 0:
        return (
            'EN CURSO',
            'No hay detecciones ni referencias útiles. Confirmar datos de entrada y anotaciones.'
        )

    return (
        'EN REVISION',
        'Métricas calculadas con detecciones válidas. Verificar criterios de aceptación en Jira.'
    )


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f'No existe el CSV de entrada: {INPUT_PATH}')

    rows = []
    with INPUT_PATH.open('r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_id = row.get('image_id', '').strip()
            if not image_id:
                continue
            pred_centroids = parsear_centroides(row.get('pred_centroids', ''))
            gt_centroids = parsear_centroides(row.get('gt_centroids', ''))

            if pred_centroids or gt_centroids:
                distancia_max = safe_float(
                    row.get('match_distance_px', DEFAULT_MATCH_DISTANCE)
                )
                if distancia_max == 0:
                    distancia_max = DEFAULT_MATCH_DISTANCE
                tp, fp, fn = calcular_tp_fp_fn_por_emparejamiento(
                    pred_centroids=pred_centroids,
                    gt_centroids=gt_centroids,
                    distancia_max=distancia_max,
                )
                origen_metricas = 'spatial_match'
            else:
                tp = int(safe_float(row.get('tp', 0)))
                fp = int(safe_float(row.get('fp', 0)))
                fn = int(safe_float(row.get('fn', 0)))
                origen_metricas = 'manual_counts'

            p = safe_float(row.get('precision'))
            r = safe_float(row.get('recall'))
            f1 = safe_float(row.get('f1'))
            iou = safe_float(row.get('IoU'))

            if p == 0 and r == 0 and f1 == 0 and iou == 0:
                p = calcular_precision(tp, fp)
                r = calcular_recall(tp, fn)
                f1 = calcular_f1(p, r)
                iou = calcular_iou(tp, fp, fn)

            rows.append({
                'image_id': image_id,
                'tp': tp,
                'fp': fp,
                'fn': fn,
                'precision': p,
                'recall': r,
                'f1': f1,
                'IoU': iou,
                'notes': row.get('notes', '').strip(),
                'origen_metricas': origen_metricas,
            })

    if not rows:
        raise ValueError('No hay filas para evaluar en el CSV.')

    total_tp = sum(r['tp'] for r in rows)
    total_fp = sum(r['fp'] for r in rows)
    total_fn = sum(r['fn'] for r in rows)

    precision = calcular_precision(total_tp, total_fp)
    recall = calcular_recall(total_tp, total_fn)
    f1 = calcular_f1(precision, recall)
    iou = calcular_iou(total_tp, total_fp, total_fn)
    estado, recomendacion = evaluar_calidad_resultados(
        total_tp=total_tp,
        total_fp=total_fp,
        total_fn=total_fn,
        total_imagenes=len(rows),
    )

    lines = []
    lines.append('CITO-23 - Resumen de métricas')
    lines.append('=============================')
    lines.append(f'Imágenes evaluadas: {len(rows)}')
    lines.append(f'TP total: {total_tp}')
    lines.append(f'FP total: {total_fp}')
    lines.append(f'FN total: {total_fn}')
    lines.append(f'Precision: {precision:.4f}')
    lines.append(f'Recall / Sensitivity: {recall:.4f}')
    lines.append(f'F1-Score: {f1:.4f}')
    lines.append(f'IoU: {iou:.4f}')
    lines.append(f'Estado recomendado: {estado}')
    lines.append(f'Recomendación: {recomendacion}')
    lines.append('')
    lines.append('Detalle por imagen:')
    for r in rows:
        lines.append(
            f"{r['image_id']}: tp={r['tp']} fp={r['fp']} fn={r['fn']} "
            f"P={r['precision']:.4f} R={r['recall']:.4f} F1={r['f1']:.4f} IoU={r['IoU']:.4f} "
            f"origen={r['origen_metricas']}"
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))
    print(f'\nResumen guardado en: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
