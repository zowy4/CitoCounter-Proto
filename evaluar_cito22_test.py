"""
evaluar_cito22_test.py - Script para evaluar CITO-22 baseline con el test set oficial.

Este script ejecuta la evaluación del baseline DoG sobre las 34 imágenes del test set
oficial del dataset Herlev, usando los parámetros calibrados previamente.

Genera:
- data/results/CITO-22-baseline-dog-test.csv - Resultados por imagen
- Imprime métricas globales para validación en Jira
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any

import cv2
import numpy as np

Point = Tuple[float, float]


def centroides_mascara(ruta: Path) -> List[Point]:
    """
    Extrae un centroide por componente conectado de una máscara binaria.
    
    :param ruta: Ruta al archivo de máscara
    :type ruta: Path
    :return: Lista de centroides (x, y)
    :rtype: List[Point]
    """
    mascara = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if mascara is None:
        raise ValueError(f"No se pudo leer la máscara: {ruta}")
    cantidad, estadisticas, centros, _ = cv2.connectedComponentsWithStats(mascara, 8)
    return [(float(centros[i, 0]), float(centros[i, 1])) for i in range(1, cantidad)]


def calcular_tp_fp_fn_por_emparejamiento(
    pred_centroids: List[Point], 
    gt_centroids: List[Point], 
    distancia_max: float
) -> Tuple[int, int, int]:
    """
    Calcula TP, FP, FN usando emparejamiento espacial uno-a-uno.
    
    Un TP se cuenta cuando un predicho está a <=distancia_max píxeles de un GT.
    Cada GT puede emparejarse como máximo una vez (one-to-one matching).
    
    :param pred_centroids: Lista de centroides predichos
    :type pred_centroids: List[Point]
    :param gt_centroids: Lista de centroides del ground truth
    :type gt_centroids: List[Point]
    :param distancia_max: Distancia máxima de emparejamiento en píxeles
    :type distancia_max: float
    :return: Tupla (TP, FP, FN)
    :rtype: Tuple[int, int, int]
    """
    if not pred_centroids and not gt_centroids:
        return 0, 0, 0
    if not pred_centroids:
        return 0, 0, len(gt_centroids)
    if not gt_centroids:
        return 0, len(pred_centroids), 0

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


def calcular_precision(tp: int, fp: int) -> float:
    """
    Calcula la precisión.
    
    :param tp: Verdaderos positivos
    :type tp: int
    :param fp: Falsos positivos
    :type fp: int
    :return: Precisión (0-1)
    :rtype: float
    """
    total = tp + fp
    return tp / total if total > 0 else 0.0


def calcular_recall(tp: int, fn: int) -> float:
    """
    Calcula el recall.
    
    :param tp: Verdaderos positivos
    :type tp: int
    :param fn: Falsos negativos
    :type fn: int
    :return: Recall (0-1)
    :rtype: float
    """
    total = tp + fn
    return tp / total if total > 0 else 0.0


def calcular_f1(p: float, r: float) -> float:
    """
    Calcula el F1-Score.
    
    :param p: Precisión
    :type p: float
    :param r: Recall
    :type r: float
    :return: F1-Score (0-1)
    :rtype: float
    """
    return 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0


def calcular_jaccard(tp: int, fp: int, fn: int) -> float:
    """
    Calcula el IoU (Intersection over Union).
    
    :param tp: Verdaderos positivos
    :type tp: int
    :param fp: Falsos positivos
    :type fp: int
    :param fn: Falsos negativos
    :type fn: int
    :return: IoU (0-1)
    :rtype: float
    """
    total = tp + fp + fn
    return tp / total if total > 0 else 0.0


def aplicar_dog_manual(imagen_gris: np.ndarray, sigma1: float, sigma2: float) -> np.ndarray:
    """
    Aplica DoG y devuelve la imagen normalizada a uint8.
    
    :param imagen_gris: Imagen en escala de grises
    :type imagen_gris: np.ndarray
    :param sigma1: Sigma del primer kernel gaussiano
    :type sigma1: float
    :param sigma2: Sigma del segundo kernel gaussiano
    :type sigma2: float
    :return: Imagen DoG normalizada en uint8
    :rtype: np.ndarray
    """
    g1 = cv2.GaussianBlur(imagen_gris.astype(np.float32), (0, 0), sigma1)
    g2 = cv2.GaussianBlur(imagen_gris.astype(np.float32), (0, 0), sigma2)
    dog = g1 - g2
    dog_norm = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    return dog_norm


def detectar_contornos_dog(
    imagen: np.ndarray, 
    sigma1: float, 
    sigma2: float, 
    polaridad: str = "oscuro"
) -> List[Tuple[int, int]]:
    """
    Detecta contornos usando DoG y devuelve centroides (x, y).
    
    :param imagen: Imagen de entrada BGR
    :type imagen: np.ndarray
    :param sigma1: Sigma1 para DoG
    :type sigma1: float
    :param sigma2: Sigma2 para DoG
    :type sigma2: float
    :param polaridad: Polaridad de los núcleos ('oscuro' o 'claro')
    :type polaridad: str
    :return: Lista de centroides (x, y)
    :rtype: List[Tuple[int, int]]
    """
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY) if len(imagen.shape) == 3 else imagen

    dog = aplicar_dog_manual(gris, sigma1, sigma2)

    if polaridad == "oscuro":
        dog = 255 - dog

    _, binario = cv2.threshold(dog, 127, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binario = cv2.morphologyEx(binario, cv2.MORPH_OPEN, kernel)

    contornos, _ = cv2.findContours(binario, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    centroides = []
    for c in contornos:
        area = cv2.contourArea(c)
        if 30 < area < 2000:
            M = cv2.moments(c)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroides.append((cx, cy))

    return centroides


def cargar_test_set(ruta_split: Path) -> List[str]:
    """
    Carga la lista de imágenes del archivo de split de test.
    
    :param ruta_split: Ruta al archivo CSV del split
    :type ruta_split: Path
    :return: Lista de nombres de imágenes
    :rtype: List[str]
    """
    nombres = []
    with ruta_split.open("r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            nombres.append(fila["image_name"])
    return nombres


def evaluar_imagen(
    ruta_imagen: Path, 
    ruta_mascara: Path, 
    distancia: float, 
    sigma1: float, 
    sigma2: float
) -> Dict[str, Any]:
    """
    Ejecuta DoG y compara centroides con Herlev para una imagen.
    
    :param ruta_imagen: Ruta a la imagen
    :type ruta_imagen: Path
    :param ruta_mascara: Ruta a la máscara de ground truth
    :type ruta_mascara: Path
    :param distancia: Distancia de emparejamiento
    :type distancia: float
    :param sigma1: Sigma1 para DoG
    :type sigma1: float
    :param sigma2: Sigma2 para DoG
    :type sigma2: float
    :return: Diccionario con métricas por imagen
    :rtype: Dict[str, Any]
    """
    imagen = cv2.imread(str(ruta_imagen))
    if imagen is None:
        raise ValueError(f"No se pudo leer la imagen: {ruta_imagen}")

    gt = centroides_mascara(ruta_mascara)
    pred = detectar_contornos_dog(imagen, sigma1, sigma2, polaridad="oscuro")
    tp, fp, fn = calcular_tp_fp_fn_por_emparejamiento(pred, gt, distancia)
    precision = calcular_precision(tp, fp)
    recall = calcular_recall(tp, fn)
    f1 = calcular_f1(precision, recall)
    iou = calcular_jaccard(tp, fp, fn)

    return {
        "image_id": ruta_imagen.name,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "iou": iou,
        "pred_count": len(pred),
        "gt_count": len(gt)
    }


def main() -> int:
    """
    Ejecuta la evaluación del baseline DoG sobre el test set oficial.
    
    :return: Código de salida
    :rtype: int
    """
    # Configuración
    ruta_imagenes = Path("data/raw/im_Dyskeratotic")
    ruta_masks = Path("data/ground_truth/herlev/masks")
    ruta_test_split = Path("data/ground_truth/herlev/splits/test.csv")
    ruta_salida = Path("data/results/CITO-22-baseline-dog-test.csv")
    
    # Parámetros calibrados previamente
    sigma1 = 7.0
    sigma2 = 8.0
    match_distance = 30.0
    
    # Cargar test set
    imagenes_test = cargar_test_set(ruta_test_split)
    print("=" * 70)
    print("CITO-22: Evaluación Baseline DoG - Test Set Herlev")
    print("=" * 70)
    print(f"Imágenes en test set: {len(imagenes_test)}")
    print(f"Parámetros: sigma1={sigma1}, sigma2={sigma2}, match_distance={match_distance}")
    print()
    
    # Evaluar cada imagen
    resultados: List[Dict[str, Any]] = []
    for i, nombre_imagen in enumerate(imagenes_test, 1):
        ruta_imagen = ruta_imagenes / nombre_imagen
        ruta_mascara = ruta_masks / f"{ruta_imagen.stem}_nuc_mask.png"
        
        if not ruta_imagen.exists():
            print(f"[{i}/{len(imagenes_test)}] {nombre_imagen}: ⚠️ Imagen no encontrada")
            continue
        if not ruta_mascara.exists():
            print(f"[{i}/{len(imagenes_test)}] {nombre_imagen}: ⚠️ Sin máscara")
            continue
        
        resultado = evaluar_imagen(ruta_imagen, ruta_mascara, match_distance, sigma1, sigma2)
        resultados.append(resultado)
        print(f"[{i}/{len(imagenes_test)}] {nombre_imagen}: GT={resultado['gt_count']} pred={resultado['pred_count']} TP={resultado['tp']} F1={resultado['f1']:.4f}")
    
    # Calcular métricas globales
    tp_total = sum(int(r["tp"]) for r in resultados)
    fp_total = sum(int(r["fp"]) for r in resultados)
    fn_total = sum(int(r["fn"]) for r in resultados)
    
    precision_global = calcular_precision(tp_total, fp_total)
    recall_global = calcular_recall(tp_total, fn_total)
    f1_global = calcular_f1(precision_global, recall_global)
    iou_global = calcular_jaccard(tp_total, fp_total, fn_total)
    
    print()
    print("=" * 70)
    print("RESUMEN GLOBAL CITO-22 BASELINE DoG (Test Set)")
    print("=" * 70)
    print(f"Imágenes evaluadas: {len(resultados)}")
    print(f"TP total: {tp_total}")
    print(f"FP total: {fp_total}")
    print(f"FN total: {fn_total}")
    print(f"Precision: {precision_global:.4f} ({precision_global*100:.2f}%)")
    print(f"Recall: {recall_global:.4f} ({recall_global*100:.2f}%)")
    print(f"F1-Score: {f1_global:.4f} ({f1_global*100:.2f}%)")
    print(f"IoU: {iou_global:.4f} ({iou_global*100:.2f}%)")
    print("=" * 70)
    
    # Interpretación
    print()
    print("INTERPRETE PARA JIRA:")
    if f1_global >= 0.90:
        print("✅ CITO-22 CUMPLIDO: Baseline DoG alcanza F1 ≥ 90% en datos reales")
    else:
        print(f"❌ CITO-22 NO CUMPLE: F1={f1_global:.4f} (0.92% actual) << 0.90 (90% objetivo)")
        print("   Recomendación: Migrar a Deep Learning (Cellpose/StarDist/U-Net)")
        print(f"   Problemas: FP excesivos ({fp_total} falsos positivos) invalidan el enfoque DoG")
    
    # Guardar resultados en CSV
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    campos = ["image_id", "tp", "fp", "fn", "precision", "recall", "f1", "iou", "pred_count", "gt_count"]
    
    with ruta_salida.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos, lineterminator="\n")
        escritor.writeheader()
        for resultado in resultados:
            escritor.writerow({campo: resultado[campo] for campo in campos})
    
    print()
    print(f"✅ Resultados guardados en: {ruta_salida}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())