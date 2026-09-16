#!/usr/bin/env python3
"""
CITO-23 - Validador de métricas del detector DoG

Valida las detecciones del algoritmo DoG contra el ground truth en formato YOLO.
Implementa matching basado en IoU y calcula métricas estándar:
- Precision: TP / (TP + FP)
- Recall: TP / (TP + FN)
- F1-Score: 2 * (P * R) / (P + R)
- IoU promedio: intersección / unión de cajas

Formato YOLO esperado en ground truth:
class_id center_x center_y width height (valores normalizados 0-1)
"""

import argparse
import csv
import cv2
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging

from src.analysis import analizar_nucleos
from src.dog_filter import aplicar_filtro_dog
from src.preprocessing import preprocesar_imagen

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class BoundingBox:
    """Caja delimitadora con operaciones IoU."""

    def __init__(self, x_min: float, y_min: float, x_max: float, y_max: float):
        """
        Args:
            x_min, y_min, x_max, y_max: coordenadas en píxeles (absoluto)
        """
        self.x_min = min(x_min, x_max)
        self.y_min = min(y_min, y_max)
        self.x_max = max(x_min, x_max)
        self.y_max = max(y_min, y_max)

    @classmethod
    def from_yolo(cls, cx: float, cy: float, w: float, h: float,
                   img_width: int, img_height: int) -> 'BoundingBox':
        """Convierte de formato YOLO normalizado a coordenadas absolutas.

        Args:
            cx, cy: centro normalizado (0-1)
            w, h: ancho/alto normalizado (0-1)
            img_width, img_height: dimensiones de la imagen en píxeles
        """
        abs_w = w * img_width
        abs_h = h * img_height
        abs_cx = cx * img_width
        abs_cy = cy * img_height

        x_min = abs_cx - abs_w / 2
        y_min = abs_cy - abs_h / 2
        x_max = abs_cx + abs_w / 2
        y_max = abs_cy + abs_h / 2

        return cls(x_min, y_min, x_max, y_max)

    @classmethod
    def from_contour_area(cls, x_center: float, y_center: float,
                          area: float) -> 'BoundingBox':
        """Crea una caja cuadrada a partir del área detectada.

        Asume que el núcleo es aproximadamente circular/cuadrado.
        """
        side = (area) ** 0.5
        return cls(x_center - side/2, y_center - side/2,
                   x_center + side/2, y_center + side/2)

    @property
    def area(self) -> float:
        """Calcula el área de la caja."""
        return max(0, (self.x_max - self.x_min) * (self.y_max - self.y_min))

    def iou(self, other: 'BoundingBox') -> float:
        """Calcula Intersection over Union (IoU) con otra caja."""
        if not isinstance(other, BoundingBox):
            return 0.0

        x_min_inter = max(self.x_min, other.x_min)
        y_min_inter = max(self.y_min, other.y_min)
        x_max_inter = min(self.x_max, other.x_max)
        y_max_inter = min(self.y_max, other.y_max)

        if x_max_inter <= x_min_inter or y_max_inter <= y_min_inter:
            return 0.0

        inter_area = (x_max_inter - x_min_inter) * (y_max_inter - y_min_inter)
        union_area = self.area + other.area - inter_area

        if union_area == 0:
            return 0.0

        return inter_area / union_area

    def __repr__(self):
        return f"BBox({self.x_min:.1f},{self.y_min:.1f},{self.x_max:.1f},{self.y_max:.1f})"


class MetricsCalculator:
    """Calcula métricas de detección."""

    def __init__(self, iou_threshold: float = 0.5):
        """
        Args:
            iou_threshold: umbral mínimo de IoU para considerar un match
        """
        self.iou_threshold = iou_threshold
        self.matches = []  # (detection, reference, iou)

    def match_detections(self, detections: List[BoundingBox],
                        references: List[BoundingBox]) -> Dict:
        """Empareja detecciones con referencias usando greedy matching.

        Args:
            detections: cajas detectadas por el algoritmo
            references: cajas de ground truth

        Returns:
            dict con TP, FP, FN, matches y métricas
        """
        self.matches = []
        matched_refs = set()

        # Greedy matching: por cada detección, buscar mejor referencia
        for det_idx, det in enumerate(detections):
            best_iou = self.iou_threshold
            best_ref_idx = None

            for ref_idx, ref in enumerate(references):
                if ref_idx in matched_refs:
                    continue

                iou = det.iou(ref)
                if iou > best_iou:
                    best_iou = iou
                    best_ref_idx = ref_idx

            if best_ref_idx is not None:
                matched_refs.add(best_ref_idx)
                self.matches.append({
                    'det_idx': det_idx,
                    'ref_idx': best_ref_idx,
                    'iou': best_iou,
                    'det': det,
                    'ref': references[best_ref_idx]
                })

        tp = len(self.matches)
        fp = len(detections) - tp
        fn = len(references) - tp

        iou_scores = [m['iou'] for m in self.matches] if self.matches else [0.0]
        mean_iou = sum(iou_scores) / len(iou_scores) if iou_scores else 0.0

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            'tp': tp,
            'fp': fp,
            'fn': fn,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'mean_iou': mean_iou,
            'matches': self.matches,
            'unmatched_dets': [i for i in range(len(detections)) if i not in [m['det_idx'] for m in self.matches]],
            'unmatched_refs': [i for i in range(len(references)) if i not in matched_refs],
        }


def load_dataset_index(csv_path: Path) -> Dict[str, str]:
    """Carga el mapping de imagen con el nombre original del dataset."""
    index = {}
    if not csv_path.exists():
        return index

    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            imagen_id = row.get('ID_Imagen', '').strip()
            original_name = row.get('Nombre_Original', '').strip()
            if imagen_id and original_name:
                index[imagen_id] = original_name

    return index


def load_yolo_annotations(label_file: Path, img_width: int, img_height: int) -> List[BoundingBox]:
    """Carga anotaciones en formato YOLO.

    Args:
        label_file: archivo con líneas "class cx cy w h"
        img_width, img_height: dimensiones de la imagen

    Returns:
        lista de BoundingBox
    """
    boxes = []
    if not label_file.exists():
        return boxes

    with label_file.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            try:
                class_id = int(parts[0])
                cx = float(parts[1])
                cy = float(parts[2])
                w = float(parts[3])
                h = float(parts[4])

                box = BoundingBox.from_yolo(cx, cy, w, h, img_width, img_height)
                boxes.append(box)
            except (ValueError, IndexError) as e:
                logger.warning(f"Error parsing YOLO line: {line} -> {e}")
                continue

    return boxes


def obtener_etiquetas_faltantes(image_ids: List[str], labels_dir: Path,
                                dataset_index: Dict[str, str]) -> List[Tuple[str, Path]]:
    """Devuelve las etiquetas que faltan para las imágenes solicitadas."""
    faltantes = []
    for image_id in image_ids:
        original_name = dataset_index.get(image_id, image_id)
        label_file = labels_dir / f"{Path(original_name).stem}.txt"
        if not label_file.is_file():
            faltantes.append((image_id, label_file))
    return faltantes


def ejecutar_detector(image_path: Path, sigma1: float = 7.0,
                      sigma2: float = 8.0) -> Tuple[List[Dict], int, int]:
    """Ejecuta el pipeline y devuelve detecciones con centro y área."""
    imagen_gris, imagen_original = preprocesar_imagen(str(image_path))
    imagen_dog = aplicar_filtro_dog(imagen_gris, sigma1=sigma1, sigma2=sigma2)
    resultados = analizar_nucleos(imagen_dog, imagen_original)

    detecciones = []
    contornos = (
        resultados['contornos_normales'] + resultados['contornos_sospechosos']
    )
    for contorno in contornos:
        x, y, ancho, alto = cv2.boundingRect(contorno)
        detecciones.append({
            'x_center': x + ancho / 2,
            'y_center': y + alto / 2,
            'area': cv2.contourArea(contorno),
        })

    alto, ancho = imagen_original.shape[:2]
    return detecciones, ancho, alto


def validate_single_image(image_id: str, detections: List[Dict],
                         labels_dir: Path, dataset_index: Dict,
                         img_width: int = 2048, img_height: int = 1536) -> Dict:
    """Valida una imagen comparando detecciones con ground truth.

    Args:
        image_id: ID de la imagen (ej: MUESTRA_001.jpg)
        detections: lista con {'x_center', 'y_center', 'area'} de detecciones
        labels_dir: carpeta donde están las anotaciones YOLO
        dataset_index: mapeo de image_id a nombre original
        img_width, img_height: dimensiones de la imagen

    Returns:
        dict con resultados de validación
    """
    # Encontrar archivo de etiquetas
    original_name = dataset_index.get(image_id, image_id)
    label_stem = Path(original_name).stem  # IMG_001 de 078.bmp
    label_file = labels_dir / f"{label_stem}.txt"

    # Cargar ground truth
    reference_boxes = load_yolo_annotations(label_file, img_width, img_height)

    # Convertir detecciones a BoundingBox
    detection_boxes = []
    for det in detections:
        try:
            box = BoundingBox.from_contour_area(
                det.get('x_center', 0),
                det.get('y_center', 0),
                det.get('area', 100)
            )
            detection_boxes.append(box)
        except (TypeError, KeyError) as e:
            logger.warning(f"Error converting detection: {det} -> {e}")
            continue

    # Calcular métricas
    calc = MetricsCalculator(iou_threshold=0.5)
    metrics = calc.match_detections(detection_boxes, reference_boxes)

    # Matches serializables a JSON (BoundingBox -> coordenadas)
    matches_json = [
        {
            'det_idx': m['det_idx'],
            'ref_idx': m['ref_idx'],
            'iou': m['iou'],
            'det_box': [m['det'].x_min, m['det'].y_min, m['det'].x_max, m['det'].y_max],
            'ref_box': [m['ref'].x_min, m['ref'].y_min, m['ref'].x_max, m['ref'].y_max],
        }
        for m in metrics['matches']
    ]

    return {
        'image_id': image_id,
        'label_file': str(label_file),
        'label_exists': label_file.exists(),
        'num_detections': len(detection_boxes),
        'num_references': len(reference_boxes),
        **{k: v for k, v in metrics.items() if k != 'matches'},
        'matches': matches_json,
    }


def main():
    """Script principal de validación."""
    parser = argparse.ArgumentParser(
        description='Valida métricas del detector DoG contra anotaciones YOLO.'
    )
    parser.add_argument('--images-dir', default='data/raw',
                        help='Carpeta con las imágenes a evaluar (default: data/raw)')
    parser.add_argument('--labels-dir', default='CitoDataset_v1/labels/train',
                        help='Carpeta con las etiquetas YOLO '
                             '(default: CitoDataset_v1/labels/train)')
    parser.add_argument('--index', default='data/dataset_index.csv',
                        help='CSV con columnas ID_Imagen y Nombre_Original '
                             '(default: data/dataset_index.csv)')
    parser.add_argument('--output-prefix',
                        default='data/results/CITO-23-validacion-mejorada',
                        help='Prefijo de los reportes .txt/.json de salida')
    parser.add_argument('--sigma1', type=float, default=7.0,
                        help='Sigma menor del filtro DoG (default: 7.0)')
    parser.add_argument('--sigma2', type=float, default=8.0,
                        help='Sigma mayor del filtro DoG (default: 8.0)')
    parser.add_argument('--images', nargs='*', default=None,
                        help='Subconjunto explícito de nombres de imagen. Por defecto: '
                             'todas las imágenes del índice con etiqueta disponible.')
    args = parser.parse_args()

    images_dir = Path(args.images_dir)
    labels_dir = Path(args.labels_dir)
    dataset_index_path = Path(args.index)
    output_path = Path(args.output_prefix + '.txt')
    output_json = Path(args.output_prefix + '.json')

    # Verificar que existen las rutas
    if not dataset_index_path.exists():
        logger.error(f"No existe: {dataset_index_path}")
        return 1

    if not labels_dir.exists():
        logger.error(f"No existe: {labels_dir}")
        return 1

    if not images_dir.exists():
        logger.error(f"No existe: {images_dir}")
        return 1

    logger.info("Cargando dataset index...")
    dataset_index = load_dataset_index(dataset_index_path)
    logger.info(f"Se cargaron {len(dataset_index)} imágenes del índice")

    logger.info(f"Buscando etiquetas YOLO en: {labels_dir}")
    label_files = list(labels_dir.glob("*.txt"))
    logger.info(f"Se encontraron {len(label_files)} archivos de etiquetas")

    if args.images:
        # Subconjunto explícito: exige etiquetas para todas las imágenes
        test_images = list(args.images)
        etiquetas_faltantes = obtener_etiquetas_faltantes(
            test_images, labels_dir, dataset_index
        )
        if etiquetas_faltantes:
            logger.error(
                "No se calcularon métricas: faltan anotaciones para %d imágenes.",
                len(etiquetas_faltantes),
            )
            for image_id, label_file in etiquetas_faltantes:
                logger.error("  %s: %s", image_id, label_file)
            return 1
    else:
        # Modo automático: todas las imágenes del índice con etiqueta disponible
        test_images = []
        omitidas = []
        for image_id in dataset_index:
            if not (images_dir / image_id).is_file():
                omitidas.append((image_id, 'imagen no encontrada'))
                continue
            original_name = dataset_index.get(image_id, image_id)
            label_file = labels_dir / f"{Path(original_name).stem}.txt"
            if not label_file.is_file():
                omitidas.append((image_id, 'etiqueta no encontrada'))
                continue
            test_images.append(image_id)
        for image_id, motivo in omitidas:
            logger.warning("Omitida %s: %s", image_id, motivo)
        if not test_images:
            logger.error("No hay imágenes con etiqueta disponible para validar.")
            return 1

    logger.info(f"\nValidando {len(test_images)} imágenes "
                f"(sigma1={args.sigma1:.2f}, sigma2={args.sigma2:.2f})...")

    results = []
    total_tp = total_fp = total_fn = 0
    total_iou = []

    for image_id in test_images:
        logger.info(f"\nProcesando: {image_id}")

        image_path = images_dir / image_id
        if not image_path.is_file():
            logger.error("No existe la imagen de entrada: %s", image_path)
            return 1

        detections, img_width, img_height = ejecutar_detector(
            image_path, sigma1=args.sigma1, sigma2=args.sigma2
        )

        result = validate_single_image(
            image_id,
            detections,
            labels_dir,
            dataset_index,
            img_width=img_width,
            img_height=img_height,
        )

        results.append(result)
        total_tp += result['tp']
        total_fp += result['fp']
        total_fn += result['fn']
        if result['mean_iou'] > 0:
            total_iou.append(result['mean_iou'])

        logger.info(f"  Detecciones: {result['num_detections']}")
        logger.info(f"  Referencias (GT): {result['num_references']}")
        logger.info(f"  TP={result['tp']} FP={result['fp']} FN={result['fn']}")
        logger.info(f"  P={result['precision']:.4f} R={result['recall']:.4f} F1={result['f1']:.4f}")

    # Resumen total
    total_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    total_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    total_f1 = 2 * total_precision * total_recall / (total_precision + total_recall) \
        if (total_precision + total_recall) > 0 else 0.0
    mean_iou = sum(total_iou) / len(total_iou) if total_iou else 0.0

    # Generar reporte
    logger.info("\n" + "="*60)
    logger.info("RESUMEN DE VALIDACIÓN")
    logger.info("="*60)
    logger.info(f"Imágenes evaluadas: {len(results)}")
    logger.info(f"Umbral IoU: 0.50")
    logger.info(f"\nMétricas totales:")
    logger.info(f"  TP total:   {total_tp}")
    logger.info(f"  FP total:   {total_fp}")
    logger.info(f"  FN total:   {total_fn}")
    logger.info(f"  Precision:  {total_precision:.4f}")
    logger.info(f"  Recall:     {total_recall:.4f}")
    logger.info(f"  F1-Score:   {total_f1:.4f}")
    logger.info(f"  Mean IoU:   {mean_iou:.4f}")

    # Guardar resultados
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open('w', encoding='utf-8') as f:
        f.write("CITO-23 - Validación de métricas del detector DoG (mejorada)\n")
        f.write("="*70 + "\n\n")
        f.write(f"Imágenes evaluadas: {len(results)}\n")
        f.write(f"Umbral IoU: 0.50\n")
        f.write(f"Sigma DoG: sigma1={args.sigma1:.2f}, sigma2={args.sigma2:.2f}\n")
        f.write(f"Imágenes: {images_dir}\n")
        f.write(f"Etiquetas: {labels_dir}\n\n")
        f.write("MÉTRICAS TOTALES:\n")
        f.write("-"*70 + "\n")
        f.write(f"TP total:   {total_tp}\n")
        f.write(f"FP total:   {total_fp}\n")
        f.write(f"FN total:   {total_fn}\n")
        f.write(f"Precision:  {total_precision:.4f}\n")
        f.write(f"Recall:     {total_recall:.4f}\n")
        f.write(f"F1-Score:   {total_f1:.4f}\n")
        f.write(f"Mean IoU:   {mean_iou:.4f}\n\n")
        f.write("DETALLE POR IMAGEN:\n")
        f.write("-"*70 + "\n")

        for r in results:
            f.write(f"\n{r['image_id']}:\n")
            f.write(f"  Label file: {r['label_file']}\n")
            f.write(f"  Exists: {r['label_exists']}\n")
            f.write(f"  Detections: {r['num_detections']}\n")
            f.write(f"  References: {r['num_references']}\n")
            f.write(f"  TP={r['tp']} FP={r['fp']} FN={r['fn']}\n")
            f.write(f"  P={r['precision']:.4f} R={r['recall']:.4f} F1={r['f1']:.4f} IoU={r['mean_iou']:.4f}\n")

    # Guardar JSON para análisis posterior
    with output_json.open('w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'script': 'validar_metricas_cito23.py',
                'version': '1.1',
                'iou_threshold': 0.5,
                'sigma1': args.sigma1,
                'sigma2': args.sigma2,
                'images_dir': str(images_dir),
                'labels_dir': str(labels_dir),
                'images_evaluated': len(results),
            },
            'summary': {
                'tp': total_tp,
                'fp': total_fp,
                'fn': total_fn,
                'precision': total_precision,
                'recall': total_recall,
                'f1': total_f1,
                'mean_iou': mean_iou,
            },
            'results': results
        }, f, indent=2)

    logger.info(f"\n✅ Resultados guardados:")
    logger.info(f"   - {output_path}")
    logger.info(f"   - {output_json}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
