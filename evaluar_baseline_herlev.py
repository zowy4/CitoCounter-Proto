"""Evalúa el baseline DoG contra el ground truth espacial Herlev.

Este script evalúa el baseline Difference of Gaussians (DoG) sobre el dataset Herlev
generando un registro CSV con métricas por imagen y un resumen global.

Nota: Los nucleos en el dataset Herlev son oscuros (menor intensidad que el fondo),
por lo que la detección requiere ajustar los parametros o invertir la imagen DoG.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np

Point = Tuple[float, float]


def centroides_mascara(ruta: Path) -> List[Point]:
    """Extrae un centroide por componente conectado de una máscara binaria."""
    mascara = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if mascara is None:
        raise ValueError(f"No se pudo leer la máscara: {ruta}")
    cantidad, estadisticas, centros, _ = cv2.connectedComponentsWithStats(mascara, 8)
    return [(float(centros[i, 0]), float(centros[i, 1])) for i in range(1, cantidad)]


def extraer_centroides_mascara(mascara: np.ndarray) -> List[Point]:
    """Extrae centroides de una máscara binaria usando connectedComponents."""
    mascara = cv2.imread(str(mascara) if isinstance(mascara, Path) else mascara, cv2.IMREAD_GRAYSCALE)
    if mascara is None:
        return []
    cantidad, estadisticas, centros, _ = cv2.connectedComponentsWithStats(mascara, 8)
    return [(float(centros[i, 0]), float(centros[i, 1])) for i in range(1, cantidad)]


def calcular_tp_fp_fn_por_emparejamiento(pred_centroids: List[Point], gt_centroids: List[Point], distancia_max: float) -> Tuple[int, int, int]:
    """
    Calcula TP, FP, FN usando emparejamiento espacial uno-a-uno.

    Un TP se cuenta cuando un predicho está a <=distancia_max píxeles de un GT.
    Cada GT puede emparejarse como máximo una vez (one-to-one matching).
    """
    if not pred_centroids and not gt_centroids:
        return 0, 0, 0
    if not pred_centroids:
        return 0, 0, len(gt_centroids)
    if not gt_centroids:
        return 0, len(pred_centroids), 0

    # Crear lista de pares candidatos con distancia
    candidatos = []
    for pred_idx, (px, py) in enumerate(pred_centroids):
        for gt_idx, (gx, gy) in enumerate(gt_centroids):
            distancia = math.hypot(px - gx, py - gy)
            if distancia <= distancia_max:
                candidatos.append((distancia, pred_idx, gt_idx))

    # Ordenar por distancia y usar emparejamiento uno-a-uno
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


def calcular_precision(tp: int, fp: int) -> float:
    total = tp + fp
    return tp / total if total > 0 else 0.0


def calcular_recall(tp: int, fn: int) -> float:
    total = tp + fn
    return tp / total if total > 0 else 0.0


def calcular_f1(p: float, r: float) -> float:
    return 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0


def calcular_jaccard(tp: int, fp: int, fn: int) -> float:
    total = tp + fp + fn
    return tp / total if total > 0 else 0.0


def aplicar_dog_manual(imagen_gris: np.ndarray, sigma1: float, sigma2: float) -> np.ndarray:
    """Aplica DoG y devuelve la imagen normalizada."""
    g1 = cv2.GaussianBlur(imagen_gris.astype(np.float32), (0, 0), sigma1)
    g2 = cv2.GaussianBlur(imagen_gris.astype(np.float32), (0, 0), sigma2)
    dog = g1 - g2
    dog_norm = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX)
    return dog_norm.astype(np.uint8)


def detectar_contornos_dog(imagen: np.ndarray, sigma1: float, sigma2: float, polaridad: str = "oscuro") -> List[Tuple[int, int]]:
    """Detecta contornos usando DoG y devuelve centroides (x, y)."""
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY) if len(imagen.shape) == 3 else imagen

    dog = aplicar_dog_manual(gris, sigma1, sigma2)

    # Para nucleos oscuros, invertimos para que resalten
    if polaridad == "oscuro":
        dog = 255 - dog

    # Umbral y apertura morfologica
    _, binario = cv2.threshold(dog, 127, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binario = cv2.morphologyEx(binario, cv2.MORPH_OPEN, kernel)

    contornos, _ = cv2.findContours(binario, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    centroides = []
    for c in contornos:
        area = cv2.contourArea(c)
        if 30 < area < 2000:  # Rango razonable para nucleos
            M = cv2.moments(c)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroides.append((cx, cy))

    return centroides


def evaluar_imagen(ruta_imagen: Path, ruta_mascara: Path, distancia: float, sigma1: float, sigma2: float) -> Dict[str, object]:
    """Ejecuta DoG y compara centroides con Herlev para una imagen."""
    # Cargar imagen original
    imagen = cv2.imread(str(ruta_imagen))
    if imagen is None:
        raise ValueError(f"No se pudo leer la imagen: {ruta_imagen}")

    # Cargar ground truth
    gt = centroides_mascara(ruta_mascara)

    # Detectar nucleos (nucleos son oscuros en este dataset)
    pred = detectar_contornos_dog(imagen, sigma1, sigma2, polaridad="oscuro")

    # Calcular metricas
    tp, fp, fn = calcular_tp_fp_fn_por_emparejamiento(pred, gt, distancia)
    precision = calcular_precision(tp, fp)
    recall = calcular_recall(tp, fn)
    f1 = calcular_f1(precision, recall)
    iou = calcular_jaccard(tp, fp, fn)

    return {"image_id": ruta_imagen.name, "tp": tp, "fp": fp, "fn": fn,
            "precision": precision, "recall": recall, "f1": f1, "iou": iou,
            "pred_count": len(pred), "gt_count": len(gt)}


def main() -> int:
    """Ejecuta la evaluación completa de las imágenes Herlev."""
    parser = argparse.ArgumentParser(description="Evalúa baseline DoG contra ground truth Herlev")
    parser.add_argument("--images-dir", type=Path, default=Path("data/raw/im_Dyskeratotic"), help="Directorio de imágenes")
    parser.add_argument("--masks-dir", type=Path, default=Path("data/ground_truth/herlev/masks"), help="Directorio de máscaras")
    parser.add_argument("--output", type=Path, default=Path("data/results/CITO-95-baseline-dog-herlev.csv"), help="Archivo de salida CSV")
    parser.add_argument("--match-distance", type=float, default=30.0, help="Distancia de emparejamiento en píxeles (default: 30.0)")
    parser.add_argument("--sigma1", type=float, default=7.0, help="Sigma1 para DoG (default: 7.0)")
    parser.add_argument("--sigma2", type=float, default=8.0, help="Sigma2 para DoG (default: 8.0)")
    args = parser.parse_args()

    # Validar
    if args.sigma2 <= args.sigma1:
        raise ValueError(f"sigma2 ({args.sigma2}) debe ser mayor que sigma1 ({args.sigma1})")

    # Encontrar imágenes
    imagenes = sorted(args.images_dir.glob("*.bmp"))
    print(f"Evaluando {len(imagenes)} imágenes...")
    print(f"Parámetros: sigma1={args.sigma1}, sigma2={args.sigma2}, match_distance={args.match_distance}")
    print()

    resultados: List[Dict[str, object]] = []
    for i, imagen in enumerate(imagenes, 1):
        mascara = args.masks_dir / f"{imagen.stem}_nuc_mask.png"
        if not mascara.exists():
            print(f"[{i}/{len(imagenes)}] {imagen.name}: ⚠️ Sin máscara")
            continue

        resultado = evaluar_imagen(imagen, mascara, args.match_distance, args.sigma1, args.sigma2)
        resultados.append(resultado)
        print(f"[{i}/{len(imagenes)}] {imagen.name}: GT={resultado['gt_count']} pred={resultado['pred_count']} TP={resultado['tp']} F1={resultado['f1']:.4f}")

    # Calcular metricas globales
    tp_total = sum(int(r["tp"]) for r in resultados)
    fp_total = sum(int(r["fp"]) for r in resultados)
    fn_total = sum(int(r["fn"]) for r in resultados)

    precision_global = calcular_precision(tp_total, fp_total)
    recall_global = calcular_recall(tp_total, fn_total)
    f1_global = calcular_f1(precision_global, recall_global)
    iou_global = calcular_jaccard(tp_total, fp_total, fn_total)

    print()
    print("=" * 70)
    print("RESUMEN GLOBAL BASELINE DoG")
    print("=" * 70)
    print(f"Imágenes evaluadas: {len(resultados)}")
    print(f"TP total: {tp_total}")
    print(f"FP total: {fp_total}")
    print(f"FN total: {fn_total}")
    print(f"Precision: {precision_global:.4f}")
    print(f"Recall: {recall_global:.4f}")
    print(f"F1-Score: {f1_global:.4f}")
    print(f"IoU: {iou_global:.4f}")
    print("=" * 70)

    # Guardar resultados en CSV
    args.output.parent.mkdir(parents=True, exist_ok=True)
    campos = ["image_id", "tp", "fp", "fn", "precision", "recall", "f1", "iou", "pred_count", "gt_count"]

    with args.output.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos, lineterminator="\n")
        escritor.writeheader()
        for resultado in resultados:
            escritor.writerow({campo: resultado[campo] for campo in campos})

    print(f"\n✅ Resultados guardados en: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
