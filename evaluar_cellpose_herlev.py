"""Evalúa Cellpose zero-shot sobre el split test de Herlev."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np
from cellpose import models

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", type=Path, default=Path("data/raw/im_Dyskeratotic"))
    parser.add_argument("--masks-dir", type=Path, default=Path("data/ground_truth/herlev/masks"))
    parser.add_argument("--splits", type=Path, default=Path("data/ground_truth/herlev/splits/test.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/results/CITO-95-cellpose-zeroshot.csv"))
    parser.add_argument("--match-distance", type=float, default=30.0)
    parser.add_argument("--limit", type=int, default=None, help="Límite de imágenes en orden del manifiesto")
    parser.add_argument("--gpu", action="store_true", help="Solicita GPU en lugar de CPU")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit debe ser mayor que cero")

    with args.splits.open(newline="", encoding="utf-8") as archivo:
        ids = [fila["image_id"] for fila in csv.DictReader(archivo)]
    if args.limit is not None:
        ids = ids[: args.limit]
    if not ids:
        parser.error("El manifiesto no contiene imágenes para evaluar")

    modelo = models.CellposeModel(gpu=args.gpu, pretrained_model="cpsam_v2")
    filas: List[Dict[str, object]] = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporal = args.output.with_suffix(args.output.suffix + ".tmp")

    try:
        for numero, image_id in enumerate(ids, 1):
            ruta_imagen = args.images_dir / f"{image_id}.bmp"
            imagen = cv2.imread(str(ruta_imagen), cv2.IMREAD_COLOR)
            if imagen is None:
                raise ValueError(f"No se pudo leer {ruta_imagen}")
            rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            mascaras, *_ = modelo.eval(rgb, channels=[0, 0], diameter=None, min_size=15)
            pred = centroides_predichos(mascaras)
            gt = centroides_gt(args.masks_dir / f"{image_id}_nuc_mask.png")
            tp, fp, fn = calcular_tp_fp_fn_por_emparejamiento(
                pred, gt, args.match_distance
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
            print(
                f"[{numero}/{len(ids)}] {image_id}: GT={len(gt)} "
                f"pred={len(pred)} F1={filas[-1]['f1']:.4f}",
                flush=True,
            )

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
        temporal.replace(args.output)
    except BaseException:
        temporal.unlink(missing_ok=True)
        raise

    print(
        f"GLOBAL test={len(filas)} TP={tp} FP={fp} FN={fn} "
        f"P={precision:.4f} R={recall:.4f} "
        f"F1={calcular_f1(precision, recall):.4f} "
        f"IoU={calcular_jaccard(tp, fp, fn):.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
