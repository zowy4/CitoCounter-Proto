"""
Evaluación del baseline DoG sobre el dataset Herlev (CITO-95, J-41).
Calcula métricas espaciales (TP, FP, FN, Precision, Recall, F1, IoU)
comparando las detecciones del filtro DoG (sigma1=7.0, sigma2=8.0)
contra las anotaciones de ground truth de Herlev.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np

from src.preprocessing import preprocesar_imagen
from src.dog_filter import aplicar_filtro_dog
from src.analysis import analizar_nucleos


def cargar_celulas_gt(csv_path: Path) -> List[Tuple[float, float]]:
    """
    Carga los centroides de ground truth desde un archivo *_cells.csv de Herlev.

    :param csv_path: Ruta al archivo CSV con las células de ground truth
    :type csv_path: pathlib.Path
    :rtype: list[tuple[float, float]]
    """
    centroids: List[Tuple[float, float]] = []
    if not csv_path.exists():
        return centroids

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                x = float(row["X"])
                y = float(row["Y"])
                centroids.append((x, y))
            except (ValueError, KeyError):
                continue
    return centroids


def extraer_centroides_predichos(resultados: dict) -> List[Tuple[int, int]]:
    """
    Extrae los centroides predichos a partir de los contornos del análisis.

    :param resultados: Diccionario de resultados devuelto por analizar_nucleos()
    :type resultados: dict
    :rtype: list[tuple[int, int]]
    """
    centroids: List[Tuple[int, int]] = []
    contornos = resultados.get("contornos_normales", []) + resultados.get("contornos_sospechosos", [])
    for contorno in contornos:
        M = cv2.moments(contorno)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroids.append((cx, cy))
    return centroids


def calcular_metricas_emparejamiento(
    pred_centroids: List[Tuple[int, int]],
    gt_centroids: List[Tuple[float, float]],
    distancia_max: float = 10.0,
) -> Tuple[int, int, int, float, float, float, float]:
    """
    Calcula TP, FP, FN, Precision, Recall, F1 e IoU mediante emparejamiento espacial.

    :param pred_centroids: Lista de centroides predichos
    :type pred_centroids: list[tuple[int, int]]
    :param gt_centroids: Lista de centroides de ground truth
    :type gt_centroids: list[tuple[float, float]]
    :param distancia_max: Distancia máxima en píxeles para considerar una coincidencia
    :type distancia_max: float
    :rtype: tuple[int, int, int, float, float, float, float]
    """
    if not pred_centroids and not gt_centroids:
        return 0, 0, 0, 0.0, 0.0, 0.0, 0.0

    if not pred_centroids:
        fn = len(gt_centroids)
        return 0, 0, fn, 0.0, 0.0, 0.0, 0.0

    if not gt_centroids:
        fp = len(pred_centroids)
        return 0, fp, 0, 0.0, 0.0, 0.0, 0.0

    candidatos = []
    for p_idx, (px, py) in enumerate(pred_centroids):
        for g_idx, (gx, gy) in enumerate(gt_centroids):
            dist = math.hypot(px - gx, py - gy)
            if dist <= distancia_max:
                candidatos.append((dist, p_idx, g_idx))

    candidatos.sort(key=lambda item: item[0])
    pred_usados = set()
    gt_usados = set()
    tp = 0

    for _, p_idx, g_idx in candidatos:
        if p_idx in pred_usados or g_idx in gt_usados:
            continue
        pred_usados.add(p_idx)
        gt_usados.add(g_idx)
        tp += 1

    fp = len(pred_centroids) - tp
    fn = len(gt_centroids) - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    jaccard = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0

    return tp, fp, fn, precision, recall, f1, jaccard


def evaluar_imagen_herlev(
    imagen_path: Path,
    cells_csv_path: Path,
    sigma1: float = 7.0,
    sigma2: float = 8.0,
    distancia_max: float = 10.0,
) -> Dict[str, any] | None:
    """
    Evalúa una imagen completa de Herlev con el filtro DoG y compara con ground truth.

    :param imagen_path: Ruta a la imagen BMP de Herlev
    :type imagen_path: pathlib.Path
    :param cells_csv_path: Ruta al CSV de ground truth de células
    :type cells_csv_path: pathlib.Path
    :param sigma1: Parámetro sigma1 del DoG
    :type sigma1: float
    :param sigma2: Parámetro sigma2 del DoG
    :type sigma2: float
    :param distancia_max: Distancia máxima de emparejamiento
    :type distancia_max: float
    :rtype: dict or None
    """
    if not imagen_path.exists():
        return None

    gt_centroids = cargar_celulas_gt(cells_csv_path)

    try:
        imagen_gris, imagen_original = preprocesar_imagen(
            str(imagen_path),
            mejorar_contraste_flag=True,
            reducir_ruido_flag=False,
            metodo_contraste="clahe",
            polaridad="nucleos-claros",
        )

        imagen_dog = aplicar_filtro_dog(
            imagen_gris,
            sigma1=sigma1,
            sigma2=sigma2,
        )

        resultados = analizar_nucleos(
            imagen_dog,
            imagen_original,
            polaridad="nucleos-claros",
        )

        pred_centroids = extraer_centroides_predichos(resultados)
        tp, fp, fn, precision, recall, f1, jaccard = calcular_metricas_emparejamiento(
            pred_centroids, gt_centroids, distancia_max
        )

        return {
            "image_id": imagen_path.stem,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "jaccard": jaccard,
            "pred_count": len(pred_centroids),
            "gt_count": len(gt_centroids),
        }
    except Exception as e:
        print(f"Error evaluando {imagen_path.name}: {e}")
        return None
