#!/usr/bin/env python
"""Script para evaluación rápida de Cellpose en conjunto de prueba Herlev."""
import csv
from pathlib import Path
from typing import Dict, List, Tuple
import cv2
import numpy as np
from cellpose import models

Path("C:/Users/zowya/OneDrive/Escritorio/zowy/TALLER 1/Software/CitoCounter_Proto/CITO-95-eval-cellpose.py")

def centroides_predichos(mascaras: np.ndarray) -> List[Tuple[float, float]]:
    """Obtiene centroides de instancias Cellpose excluyendo fondo."""
    etiquetas = np.asarray(mascaras)
    centroides: List[Tuple[float, float]] = []
    for etiqueta in np.unique(etiquetas):
        if etiqueta <= 0:
            continue
        yx = np.mean(np.argwhere(etiquetas == etiqueta), axis=0)
        centroides.append((float(yx[1]), float(yx[0])))
    return centroides

def centroides_gt(ruta: Path) -> List[Tuple[float, float]]:
    """Obtiene centroides de la máscara binaria Herlev."""
    mascara = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if mascara is None:
        raise ValueError(f"No se pudo leer {ruta}")
    cantidad, _, centros, _ = cv2.connectedComponentsWithStats(mascara, 8)
    return [(float(centros[i, 0]), float(centros[i, 1])) for i in range(1, cantidad)]

def calcular_tp_fp_fn_por_emparejamiento(
    pred: List[Tuple[float, float]], 
    gt: List[Tuple[float, float]], 
    match_distance: float
) -> Tuple[int, int, int]:
    """Calcula TP, FP, FN usando emparejamiento Euclídeo."""
    tp, fp, fn = 0, 0, 0
    usados = set()
    for px, py in pred:
        encontrado = False
        for j, (gx, gy) in enumerate(gt):
            if j in usados:
                continue
            if (px - gx)**2 + (py - gy)**2 <= match_distance**2:
                tp += 1
                usados.add(j)
                encontrado = True
                break
        if not encontrado:
            fp += 1
    fn = len(gt) - len(usados)
    return tp, fp, fn

# Configuración
images_dir = Path("data/raw/im_Dyskeratotic")
masks_dir = Path("data/ground_truth/herlev/masks")
splits = Path("data/ground_truth/herlev/splits/test.csv")
output = Path("data/results/CITO-95-cellpose-zeroshot.csv")
match_distance = 30.0
limit = 5  # Very quick test

# Cargar manifest
with splits.open(newline="", encoding="utf-8") as archivo:
    ids = [fila["image_id"] for fila in csv.DictReader(archivo)][:limit]

print(f"Evaluando {len(ids)} imágenes de prueba con Cellpose (zero-shot)...")
modelo = models.CellposeModel(gpu=False, pretrained_model="cpsam_v2")

results: List[Dict[str, object]] = []
output.parent.mkdir(parents=True, exist_ok=True)

for image_id in ids:
    ruta_imagen = images_dir / f"{image_id}.bmp"
    imagen = cv2.imread(str(ruta_imagen), cv2.IMREAD_COLOR)
    if imagen is None:
        print(f"Warning: Could not read {ruta_imagen}")
        continue
    rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    
    # Predicción Cellpose
    mascaras, *_ = modelo.eval(rgb, channels=[0, 0], diameter=None, min_size=15)
    pred = centroides_predichos(mascaras)
    gt = centroides_gt(masks_dir / f"{image_id}_nuc_mask.png")
    
    tp, fp, fn = calcular_tp_fp_fn_por_emparejamiento(pred, gt, match_distance)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    results.append({
        "image_id": image_id, 
        "tp": tp, 
        "fp": fp, 
        "fn": fn,
        "precision": precision, 
        "recall": recall,
        "f1": f1,
        "pred_count": len(pred), 
        "gt_count": len(gt),
    })
    print(f"{image_id}: pred={len(pred)}, gt={len(gt)}, F1={f1:.4f}")

# Guardar resultados
with output.open("w", newline="", encoding="utf-8") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=list(results[0].keys()), lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(results)

# Métricas globales
tp_total = sum(int(f["tp"]) for f in results)
fp_total = sum(int(f["fp"]) for f in results)
fn_total = sum(int(f["fn"]) for f in results)
precision_total = tp_total / (tp_total + fp_total) if (tp_total + fp_total) > 0 else 0
recall_total = tp_total / (tp_total + fn_total) if (tp_total + fn_total) > 0 else 0
f1_total = 2 * precision_total * recall_total / (precision_total + recall_total) if (precision_total + recall_total) > 0 else 0

print("\n" + "="*80)
print("RESULTADOS PRELIMINARES - CELLPOSE (5 imágenes)")
print("="*80)
print(f"TP: {tp_total}, FP: {fp_total}, FN: {fn_total}")
print(f"Precisión: {precision_total:.6f} ({precision_total*100:.2f}%)")
print(f"Recall: {recall_total:.6f} ({recall_total*100:.2f}%)")
print(f"F1-Score: {f1_total:.6f} ({f1_total*100:.2f}%)")
print("="*80)
print(f"\nResultados guardados en: {output}")