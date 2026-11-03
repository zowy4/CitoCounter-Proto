#!/usr/bin/env python3
"""
Script para ejecutar la evaluación de Cellpose sobre el test set Herlev
"""
import sys
sys.path.insert(0, 'C:/Users/zowya/OneDrive/Escritorio/zowy/TALLER 1/Software/CitoCounter_Proto/.venv/Lib/site-packages')

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple
import cv2
import numpy as np
from cellpose import models

# Importar funciones de evaluación desde el archivo existente
sys.path.insert(0, 'C:/Users/zowya/OneDrive/Escritorio/zowy/TALLER 1/Software/CitoCounter_Proto')
from evaluar_baseline_herlev import (
    calcular_f1,
    calcular_jaccard,
    calcular_precision,
    calcular_recall,
    calcular_tp_fp_fn_por_emparejamiento,
)

Point = Tuple[float, float]


def centroides_predichos(mascaras: np.ndarray) -> List[Point]:
    """Obtiene centroides de instancias Cellpose excluyendo fondo."""
    etiquetas = np.asarray(mascaras)
    centroides: List[Point] = []
    for etiqueta in np.unique(etiquetas):
        if etiqueta <= 0:
            continue
        yx = np.mean(np.argwhere(etiquetas == etiqueta), axis=0)
        centroides.append((float(yx[1]), float(yx[0])))
    return centroides


def centroides_gt(ruta: Path) -> List[Point]:
    """Obtiene centroides de la máscara binaria Herlev."""
    mascara = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if mascara is None:
        raise ValueError(f"No se pudo leer {ruta}")
    cantidad, _, centros, _ = cv2.connectedComponentsWithStats(mascara, 8)
    return [(float(centros[i, 0]), float(centros[i, 1])) for i in range(1, cantidad)]


def main() -> int:
    """Ejecuta Cellpose y escribe métricas por imagen y resumen global."""
    images_dir = Path("data/raw/im_Dyskeratotic")
    masks_dir = Path("data/ground_truth/herlev/masks")
    splits = Path("data/ground_truth/herlev/splits/test.csv")
    output = Path("data/results/CITO-95-cellpose-zeroshot.csv")
    match_distance = 30.0
    limit = 34  # Process all test images
    gpu = False  # Use CPU
    
    with splits.open(newline="", encoding="utf-8") as archivo:
        ids = [fila["image_id"] for fila in csv.DictReader(archivo)]
    if limit is not None and limit < 1:
        raise ValueError("--limit debe ser mayor que cero")
    
    if not ids:
        raise ValueError("El manifiesto no contiene imágenes para evaluar")
    
    print(f"Loading Cellpose model (cpu)...")
    modelo = models.CellposeModel(gpu=gpu, pretrained_model="cpsam_v2")
    
    filas: List[Dict[str, object]] = []
    output.parent.mkdir(parents=True, exist_ok=True)
    temporal = output.with_suffix(output.suffix + ".tmp")
    
    try:
        for numero, image_id in enumerate(ids, 1):
            ruta_imagen = images_dir / f"{image_id}.bmp"
            imagen = cv2.imread(str(ruta_imagen), cv2.IMREAD_COLOR)
            if imagen is None:
                raise ValueError(f"No se pudo leer {ruta_imagen}")
            rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            
            print(f"Processing image {image_id} ({numero}/{len(ids)})...")
            mascaras, *_ = modelo.eval(rgb, channels=[0, 0], diameter=None, min_size=15)
            pred = centroides_predichos(mascaras)
            gt = centroides_gt(masks_dir / f"{image_id}_nuc_mask.png")
            tp, fp, fn = calcular_tp_fp_fn_por_emparejamiento(
                pred, gt, match_distance
            )
            precision = calcular_precision(tp, fp)
            recall = calcular_recall(tp, fn)
            filas.append(
                {
                    "image_id": image_id,
                    "tp": tp,
                    "fp": fp,
                    "fn": fn,
                    "precision": precision,
                    "recall": recall,
                    "f1": calcular_f1(precision, recall),
                    "iou": calcular_jaccard(tp, fp, fn),
                    "pred_count": len(pred),
                    "gt_count": len(gt),
                }
            )
            print(f"  GT={len(gt)} pred={len(pred)} F1={filas[-1]['f1']:.4f}")
        
        tp, fp, fn = (
            sum(int(fila[clave]) for fila in filas) for clave in ("tp", "fp", "fn")
        )
        precision = calcular_precision(tp, fp)
        recall = calcular_recall(tp, fn)
        
        with temporal.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(
                archivo, fieldnames=list(filas[0]), lineterminator="\n"
            )
            escritor.writeheader()
            escritor.writerows(filas)
        temporal.replace(output)
    except BaseException:
        temporal.unlink(missing_ok=True)
        raise
    
    print("\n" + "="*80)
    print("EVALUACIÓN CELLPOSE - TEST SET HERLEV")
    print("="*80)
    print(f"Total imágenes: {len(filas)}")
    print(f"TP: {tp}, FP: {fp}, FN: {fn}")
    print(f"Precisión: {precision:.6f} ({precision*100:.2f}%)")
    print(f"Recall: {recall:.6f} ({recall*100:.2f}%)")
    f1_score = calcular_f1(precision, recall)
    print(f"F1-Score: {f1_score:.6f} ({f1_score*100:.2f}%)")
    print(f"IoU: {calcular_jaccard(tp, fp, fn):.6f}")
    print("="*80)
    
    if f1_score >= 0.90:
        print("\n✓ CELLPOSE ALCANZA EL OBJETIVO: F1 >= 90%")
    else:
        print(f"\n✗ CELLPOSE NO ALCANZA EL OBJETIVO: F1 = {f1_score*100:.2f}% (requiere >= 90%)")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())