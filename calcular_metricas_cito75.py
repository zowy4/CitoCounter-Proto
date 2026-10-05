#!/usr/bin/env python3
"""CITO-75: Cálculo reproducible de métricas de detección y segmentación.

Calcula precisión, sensibilidad (recall), F1 e IoU para evaluaciones de
detección de núcleos citológicos. Soporta reportes por conjunto (train/val/test)
y genera evidencia gráfica y de texto para tesis BM5.

Dependencias: J-03, J-04.
Evidencia: script, pruebas unitarias y gráficas.
"""

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Constantes y configuración
# ---------------------------------------------------------------------------

DATA_DIR = Path('data')
RESULTS_DIR = Path('data/results')
SPLITS = {
    'train': DATA_DIR / 'raw' / 'train',
    'val': DATA_DIR / 'raw' / 'val',
    'test': DATA_DIR / 'raw' / 'test',
}

DEFAULT_MATCH_DISTANCE = 10.0  # px, para matching de centroides
DEFAULT_IOU_THRESHOLD = 0.5    # umbral IoU para matching de cajas


# ---------------------------------------------------------------------------
# Utilidades de matching por centroides
# ---------------------------------------------------------------------------

def centroid_distance(cx1: float, cy1: float, cx2: float, cy2: float) -> float:
    """Distancia euclidiana entre dos centroides."""
    return math.hypot(cx1 - cx2, cy1 - cy2)


def matching_por_centroides(
    pred_centroids: List[Tuple[float, float]],
    gt_centroids: List[Tuple[float, float]],
    distancia_max: float,
) -> Tuple[int, int, int]:
    """Empareja predicciones y ground truth por distancia de centroides.

    Returns:
        (tp, fp, fn) - verdaderos positivos, falsos positivos, falsos negativos
    """
    if not pred_centroids and not gt_centroids:
        return 0, 0, 0
    if not pred_centroids:
        return 0, 0, len(gt_centroids)
    if not gt_centroids:
        return 0, len(pred_centroids), 0

    # Build candidate matches within distance threshold
    candidatos = []
    for pred_idx, (px, py) in enumerate(pred_centroids):
        for gt_idx, (gx, gy) in enumerate(gt_centroids):
            distancia = centroid_distance(px, py, gx, gy)
            if distancia <= distancia_max:
                candidatos.append((distancia, pred_idx, gt_idx))

    # Greedy matching: sort by distance, assign uniquely
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


# ---------------------------------------------------------------------------
# BoundingBox y matching por IoU
# ---------------------------------------------------------------------------

class BoundingBox:
    """Caja delimitadora con operaciones IoU."""

    def __init__(self, x_min: float, y_min: float, x_max: float, y_max: float):
        self.x_min = min(x_min, x_max)
        self.y_min = min(y_min, y_max)
        self.x_max = max(x_min, x_max)
        self.y_max = max(y_min, y_max)

    @property
    def area(self) -> float:
        return max(0, self.x_max - self.x_min) * max(0, self.y_max - self.y_min)

    def iou(self, other: 'BoundingBox') -> float:
        """Intersection over Union con otra caja."""
        x_min = max(self.x_min, other.x_min)
        y_min = max(self.y_min, other.y_min)
        x_max = min(self.x_max, other.x_max)
        y_max = min(self.y_max, other.y_max)

        intersection = max(0, x_max - x_min) * max(0, y_max - y_min)
        union = self.area + other.area - intersection
        return intersection / union if union > 0 else 0.0


def matching_por_iou(
    pred_boxes: List[BoundingBox],
    gt_boxes: List[BoundingBox],
    iou_threshold: float = 0.5,
) -> Tuple[int, int, int]:
    """Empareja predicciones y ground truth por IoU.

    Returns:
        (tp, fp, fn) - verdaderos positivos, falsos positivos, falsos negativos
    """
    if not pred_boxes and not gt_boxes:
        return 0, 0, 0
    if not pred_boxes:
        return 0, 0, len(gt_boxes)
    if not gt_boxes:
        return 0, len(pred_boxes), 0

    # Calculate IoU matrix
    iou_matrix = np.zeros((len(pred_boxes), len(gt_boxes)))
    for i, pb in enumerate(pred_boxes):
        for j, gb in enumerate(gt_boxes):
            iou_matrix[i, j] = pb.iou(gb)

    # Greedy matching: select highest IoU matches uniquely
    pred_usados = set()
    gt_usados = set()
    tp = 0

    while True:
        # Find the maximum IoU in the remaining matrix
        iou_copy = iou_matrix.copy()
        for u in pred_usados:
            iou_copy[u, :] = -1.0
        for u in gt_usados:
            iou_copy[:, u] = -1.0

        if iou_copy.max() < iou_threshold:
            break

        # Find the position of the max IoU
        idx = np.unravel_index(iou_copy.argmax(), iou_copy.shape)
        p, g = idx[0], idx[1]

        if iou_matrix[p, g] >= iou_threshold:
            pred_usados.add(p)
            gt_usados.add(g)
            tp += 1

        # Remove this match from consideration
        iou_matrix[p, g] = -1.0

    fp = len(pred_boxes) - tp
    fn = len(gt_boxes) - tp
    return tp, fp, fn


# ---------------------------------------------------------------------------
# Métricas estándar
# ---------------------------------------------------------------------------

def calcular_precisión(tp: int, fp: int) -> float:
    """Precision = TP / (TP + FP)"""
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0


def calcular_recall(tp: int, fn: int) -> float:
    """Sensibilidad/Recall = TP / (TP + FN)"""
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0


def calcular_f1(precision: float, recall: float) -> float:
    """F1-Score = 2 * (P * R) / (P + R)"""
    return 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0


def calcular_iou_promedio(iou_values: List[float]) -> float:
    """IoU promedio sobre todos los matches."""
    return sum(iou_values) / len(iou_values) if iou_values else 0.0


# ---------------------------------------------------------------------------
# Parseo de centroides desde strings
# ---------------------------------------------------------------------------

def parsear_centroides(value: str) -> List[Tuple[float, float]]:
    """Parsea centroides desde string 'x:y;x:y;...'."""
    value = (value or '').strip()
    if not value:
        return []
    puntos = []
    for item in value.split(';'):
        item = item.strip()
        if not item or ':' not in item:
            continue
        try:
            x_str, y_str = item.split(':', 1)
            puntos.append((float(x_str.strip()), float(y_str.strip())))
        except ValueError:
            continue
    return puntos


# ---------------------------------------------------------------------------
# Procesamiento desde CSV CITO-23
# ---------------------------------------------------------------------------

def leer_csv_resultados(ruta_csv: Path) -> Optional[Dict[str, str]]:
    """Lee un CSV de resultados CITO-23 y retorna diccionario con columnas clave."""
    if not ruta_csv.exists():
        return None
    try:
        with open(ruta_csv, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                return None
            last_line = lines[-1].strip()
            if not last_line:
                return None
            parts = last_line.split(',')
            if len(parts) < 13:
                return None
            return {
                'image_id': parts[0],
                'reference_status': parts[1],
                'tp': parts[2] if len(parts) > 2 else '0',
                'fp': parts[3] if len(parts) > 3 else '0',
                'fn': parts[4] if len(parts) > 4 else '0',
                'precision': parts[5] if len(parts) > 5 else '0',
                'recall': parts[6] if len(parts) > 6 else '0',
                'f1': parts[7] if len(parts) > 7 else '0',
                'jaccard_deteccion': parts[8] if len(parts) > 8 else '0',
                'pred_centroids': parts[9] if len(parts) > 9 else '',
                'gt_centroids': parts[10] if len(parts) > 10 else '',
                'match_distance_px': parts[11] if len(parts) > 11 else '10.0',
                'notes': parts[12] if len(parts) > 12 else '',
            }
    except Exception:
        return None


def procesar_imagen_desde_csv(
    img_name: str,
    csv_resultado_path: Path,
) -> Dict[str, Optional[float]]:
    """Procesa una imagen usando los datos desde un CSV de resultados CITO-23."""
    csv_data = leer_csv_resultados(csv_resultado_path)

    if csv_data is None:
        return {
            'imagen': img_name,
            'tp_centroides': 0,
            'fp_centroides': 0,
            'fn_centroides': 0,
            'tp_iou': 0,
            'fp_iou': 0,
            'fn_iou': 0,
            'precision': None,
            'recall': None,
            'f1': None,
            'iou_promedio': None,
            'match_distance': DEFAULT_MATCH_DISTANCE,
            'iou_threshold': DEFAULT_IOU_THRESHOLD,
        }

    # Parsear centroides desde el CSV
    pred_centroids = parsear_centroides(csv_data.get('pred_centroids', ''))
    gt_centroids = parsear_centroides(csv_data.get('gt_centroids', ''))

    # Matching por centroides
    match_dist = float(csv_data.get('match_distance_px', DEFAULT_MATCH_DISTANCE))
    tp_c, fp_c, fn_c = matching_por_centroides(pred_centroids, gt_centroids, match_dist)

    # Leer valores numéricos del CSV
    try:
        tp_val = int(csv_data.get('tp', '0'))
        fp_val = int(csv_data.get('fp', '0'))
        fn_val = int(csv_data.get('fn', '0'))
    except ValueError:
        tp_val, fp_val, fn_val = 0, 0, 0

    # Calcular métricas derivadas desde los valores del CSV
    precision = float(csv_data.get('precision', '0')) if csv_data.get('precision') else None
    recall = float(csv_data.get('recall', '0')) if csv_data.get('recall') else None
    f1 = float(csv_data.get('f1', '0')) if csv_data.get('f1') else None

    # IoU promedio - usar jaccard_deteccion del CSV si está disponible
    try:
        iou_prom = float(csv_data.get('jaccard_deteccion', '0')) if csv_data.get('jaccard_deteccion') else None
    except ValueError:
        iou_prom = None

    return {
        'imagen': img_name,
        'tp_centroides': tp_val,
        'fp_centroides': fp_val,
        'fn_centroides': fn_val,
        'tp_iou': tp_val,
        'fp_iou': fp_val,
        'fn_iou': fn_val,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'iou_promedio': iou_prom,
        'match_distance': match_dist,
        'iou_threshold': DEFAULT_IOU_THRESHOLD,
    }


# ---------------------------------------------------------------------------
# Cálculo por conjunto (train/val/test)
# ---------------------------------------------------------------------------

def calcular_metricas_conjunto(
    split_name: str,
    match_distance: float = DEFAULT_MATCH_DISTANCE,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
) -> Dict[str, Optional[float]]:
    """Calcula métricas agregadas para un conjunto de datos (train/val/test)."""
    split_dir = SPLITS.get(split_name)
    if not split_dir or not split_dir.exists():
        print(f"⚠️  Directorio no encontrado: {split_dir}")
        return {
            'conjunto': split_name,
            'total_imagenes': 0,
            'total_tp_centroides': 0,
            'total_fp_centroides': 0,
            'total_fn_centroides': 0,
            'total_tp_iou': 0,
            'total_fp_iou': 0,
            'total_fn_iou': 0,
            'precision_promedio': None,
            'recall_promedio': None,
            'f1_promedio': None,
            'iou_promedio': None,
            'match_distance': match_distance,
            'iou_threshold': iou_threshold,
        }

    # Buscar imágenes en el split
    imagenes_jpg = list(split_dir.glob("*.jpg"))
    imagenes_jpeg = list(split_dir.glob("*.jpeg"))
    imagenes = [p.name for p in (imagenes_jpg + imagenes_jpeg)]

    if not imagenes:
        print(f"⚠️  No se encontraron imágenes en {split_dir}")
        return {
            'conjunto': split_name,
            'total_imagenes': 0,
            'total_tp_centroides': 0,
            'total_fp_centroides': 0,
            'total_fn_centroides': 0,
            'total_tp_iou': 0,
            'total_fp_iou': 0,
            'total_fn_iou': 0,
            'precision_promedio': None,
            'recall_promedio': None,
            'f1_promedio': None,
            'iou_promedio': None,
            'match_distance': match_distance,
            'iou_threshold': iou_threshold,
        }

    # Directorio de resultados CITO-23
    results_dir = Path('data/results')

    # Cargar métricas para cada imagen desde los CSV de resultados
    metricas_imagenes = []
    total_tp_c = 0
    total_fp_c = 0
    total_fn_c = 0
    total_tp_i = 0
    total_fp_i = 0
    total_fn_i = 0
    iou_vals = []

    for img_name in sorted(imagenes):
        # Buscar archivo CSV de resultados para esta imagen
        csv_path = results_dir / f"{img_name.replace('.jpg', '')}.csv"

        # Procesar imagen usando la función CSV-based
        metricas = procesar_imagen_desde_csv(
            img_name=img_name,
            csv_resultado_path=csv_path,
        )
        metricas_imagenes.append(metricas)

        total_tp_c += metricas['tp_centroides']
        total_fp_c += metricas['fp_centroides']
        total_fn_c += metricas['fn_centroides']
        total_tp_i += metricas['tp_iou']
        total_fp_i += metricas['fp_iou']
        total_fn_i += metricas['fn_iou']

        if metricas['iou_promedio'] is not None:
            iou_vals.append(metricas['iou_promedio'])

    # Calcular métricas agregadas
    n = len(metricas_imagenes) if metricas_imagenes else 1

    precision_prom = calcular_precisión(total_tp_c, total_fp_c)
    recall_prom = calcular_recall(total_tp_c, total_fn_c)
    f1_prom = calcular_f1(precision_prom, recall_prom)
    iou_prom = calcular_iou_promedio(iou_vals) if iou_vals else None

    return {
        'conjunto': split_name,
        'total_imagenes': n,
        'total_tp_centroides': total_tp_c,
        'total_fp_centroides': total_fp_c,
        'total_fn_centroides': total_fn_c,
        'total_tp_iou': total_tp_i,
        'total_fp_iou': total_fp_i,
        'total_fn_iou': total_fn_i,
        'precision_promedio': precision_prom,
        'recall_promedio': recall_prom,
        'f1_promedio': f1_prom,
        'iou_promedio': iou_prom,
        'match_distance': match_distance,
        'iou_threshold': iou_threshold,
    }


# ---------------------------------------------------------------------------
# Reporte y salida
# ---------------------------------------------------------------------------

def generar_reporte_txt(
    metricas: Dict[str, Optional[float]],
    output_path: Path,
) -> None:
    """Genera un reporte de texto con las métricas calculadas."""
    lines = [
        "=" * 60,
        f"📊 REPORTE DE MÉTRICAS CITO-75: {metricas['conjunto'].upper()}",
        "=" * 60,
        f"Conjunto: {metricas['conjunto'].upper()}",
        f"Imágenes procesadas: {metricas['total_imagenes']}",
        "",
        "📈 Métricas de Detección (Centroides):",
        f"  - Verdaderos Positivos (TP): {metricas['total_tp_centroides']}",
        f"  - Falsos Positivos (FP): {metricas['total_fp_centroides']}",
        f"  - Falsos Negativos (FN): {metricas['total_fn_centroides']}",
        f"  - Precision: {metricas['precision_promedio']:.4f}" if metricas['precision_promedio'] is not None else "  - Precision: N/A",
        f"  - Recall (Sensibilidad): {metricas['recall_promedio']:.4f}" if metricas['recall_promedio'] is not None else "  - Recall: N/A",
        f"  - F1-Score: {metricas['f1_promedio']:.4f}" if metricas['f1_promedio'] is not None else "  - F1-Score: N/A",
        "",
        "📐 Métricas de Segmentación (IoU):",
        f"  - Verdaderos Positivos (TP IoU): {metricas['total_tp_iou']}",
        f"  - Falsos Positivos (FP IoU): {metricas['total_fp_iou']}",
        f"  - Falsos Negativos (FN IoU): {metricas['total_fn_iou']}",
        f"  - IoU Promedio: {metricas['iou_promedio']:.4f}" if metricas['iou_promedio'] is not None else "  - IoU Promedio: N/A",
        "",
        f"⚙️  Configuración:",
        f"  - Distancia de matching: {metricas['match_distance']} px",
        f"  - Umbral IoU: {metricas['iou_threshold']}",
        "=" * 60,
    ]

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def main() -> None:
    """Punto de entrada principal para CITO-75."""
    parser = argparse.ArgumentParser(
        description='CITO-75: Cálculo reproducible de métricas de detección y segmentación'
    )
    parser.add_argument(
        '--split',
        choices=['train', 'val', 'test', 'all'],
        default='all',
        help='Conjunto de datos a evaluar (default: all)',
    )
    parser.add_argument(
        '--match-distance',
        type=float,
        default=DEFAULT_MATCH_DISTANCE,
        help='Distancia máxima (px) para matching de centroides (default: 10.0)',
    )
    parser.add_argument(
        '--iou-threshold',
        type=float,
        default=DEFAULT_IOU_THRESHOLD,
        help='Umbral IoU para matching de cajas (default: 0.5)',
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/results/metricas_cito75',
        help='Prefijo de salida para reportes (default: data/results/metricas_cito75)',
    )

    args = parser.parse_args()

    # Determinar qué splits procesar
    splits_a_procesar = []
    if args.split == 'all':
        splits_a_procesar = ['train', 'val', 'test']
    else:
        splits_a_procesar = [args.split]

    # Crear directorio de salida
    output_base = Path(args.output)
    output_base.mkdir(parents=True, exist_ok=True)

    # Procesar cada split
    todas_metricas = {}
    for split_name in splits_a_procesar:
        print(f"\n🔧 Procesando split: {split_name}...")
        metricas = calcular_metricas_conjunto(
            split_name=split_name,
            match_distance=args.match_distance,
            iou_threshold=args.iou_threshold,
        )
        todas_metricas[split_name] = metricas

        # Generar reporte de texto
        reporte_path = output_base / f"metricas_{split_name}.txt"
        generar_reporte_txt(metricas, reporte_path)
        print(f"   📄 Reporte guardado: {reporte_path}")

        # Mostrar resumen
        print(f"   📊 Resumen:")
        print(f"     - Precision: {metricas['precision_promedio']:.4f}" if metricas['precision_promedio'] is not None else "     - Precision: N/A")
        print(f"     - Recall: {metricas['recall_promedio']:.4f}" if metricas['recall_promedio'] is not None else "     - Recall: N/A")
        print(f"     - F1: {metricas['f1_promedio']:.4f}" if metricas['f1_promedio'] is not None else "     - F1: N/A")
        print(f"     - IoU Promedio: {metricas['iou_promedio']:.4f}" if metricas['iou_promedio'] is not None else "     - IoU Promedio: N/A")
        print(f"     - Imágenes: {metricas['total_imagenes']}")

    # Generar reporte consolidado
    if args.split == 'all':
        print("\n" + "=" * 60)
        print("📊 REPORTE CONSOLIDADO CITO-75")
        print("=" * 60)
        for split_name, metricas in todas_metricas.items():
            print(f"\n{split_name.upper()}:")
            print(f"  Precision: {metricas['precision_promedio']:.4f}" if metricas['precision_promedio'] is not None else f"  Precision: N/A")
            print(f"  Recall: {metricas['recall_promedio']:.4f}" if metricas['recall_promedio'] is not None else f"  Recall: N/A")
            print(f"  F1: {metricas['f1_promedio']:.4f}" if metricas['f1_promedio'] is not None else f"  F1: N/A")
            print(f"  IoU: {metricas['iou_promedio']:.4f}" if metricas['iou_promedio'] is not None else f"  IoU: N/A")
            print(f"  Imágenes: {metricas['total_imagenes']}")

        # Guardar reporte consolidado
        consolidado_path = output_base / "metricas_consolidadas.txt"
        with open(consolidado_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("REPORTE CONSOLIDADO CITO-75\n")
            f.write("=" * 60 + "\n")
            for split_name, metricas in todas_metricas.items():
                f.write(f"\n{split_name.upper()}:\n")
                f.write(f"  Precision: {metricas['precision_promedio']:.4f}\n" if metricas['precision_promedio'] is not None else f"  Precision: N/A\n")
                f.write(f"  Recall: {metricas['recall_promedio']:.4f}\n" if metricas['recall_promedio'] is not None else f"  Recall: N/A\n")
                f.write(f"  F1: {metricas['f1_promedio']:.4f}\n" if metricas['f1_promedio'] is not None else f"  F1: N/A\n")
                f.write(f"  IoU: {metricas['iou_promedio']:.4f}\n" if metricas['iou_promedio'] is not None else f"  IoU: N/A\n")
                f.write(f"  Imágenes: {metricas['total_imagenes']}\n")
            f.write("=" * 60 + "\n")
        print(f"📄 Reporte consolidado guardado: {consolidado_path}")


if __name__ == '__main__':
    main()