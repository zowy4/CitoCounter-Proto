#!/usr/bin/env python3
"""Calcula métricas de CITO-23 a partir del CSV de revisión manual.

Formato esperado por CSV:
image_id,reference_status,tp,fp,fn,precision,recall,f1,IoU,notes
MUESTRA_001.jpg,manual_review_done,10,2,1,0.8333,0.9091,0.8696,0.7692,ok

Si precision/recall/f1/IoU están vacíos, el script las calcula automáticamente.
"""

import csv
from pathlib import Path

INPUT_PATH = Path('data/results/CITO-23-metricas-template.csv')
OUTPUT_PATH = Path('data/results/CITO-23-metricas-resumen.txt')


def safe_float(value):
    value = (value or '').strip()
    if value == '':
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


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
            tp = int(safe_float(row.get('tp', 0)))
            fp = int(safe_float(row.get('fp', 0)))
            fn = int(safe_float(row.get('fn', 0)))

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
    lines.append('')
    lines.append('Detalle por imagen:')
    for r in rows:
        lines.append(
            f"{r['image_id']}: tp={r['tp']} fp={r['fp']} fn={r['fn']} "
            f"P={r['precision']:.4f} R={r['recall']:.4f} F1={r['f1']:.4f} IoU={r['IoU']:.4f}"
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))
    print(f'\nResumen guardado en: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
