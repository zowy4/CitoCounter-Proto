#!/usr/bin/env python3
"""
Script CLI para congelar el baseline DoG sobre el dataset Herlev (CITO-95, J-41).
Ejecuta DoG con sigma1=7.0, sigma2=8.0 sobre las imágenes completas de data/raw/im_Dyskeratotic
y compara contra las anotaciones en data/ground_truth/herlev/cells/.
Genera la evidencia en data/results/CITO-95-baseline-dog.csv.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List

from src.herlev_evaluation import evaluar_imagen_herlev


def main() -> int:
    parser = argparse.ArgumentParser(description="Congelar baseline DoG sobre Herlev (CITO-95)")
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=Path("data/raw/im_Dyskeratotic"),
        help="Directorio con imágenes completas de Herlev",
    )
    parser.add_argument(
        "--gt-dir",
        type=Path,
        default=Path("data/ground_truth/herlev/cells"),
        help="Directorio con CSVs de ground truth por imagen",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("data/results/CITO-95-baseline-dog.csv"),
        help="Ruta al CSV de salida con métricas",
    )
    parser.add_argument(
        "--sigma1",
        type=float,
        default=7.0,
        help="Sigma 1 para DoG (default: 7.0)",
    )
    parser.add_argument(
        "--sigma2",
        type=float,
        default=8.0,
        help="Sigma 2 para DoG (default: 8.0)",
    )
    parser.add_argument(
        "--match-distance",
        type=float,
        default=10.0,
        help="Distancia máxima de emparejamiento en píxeles",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limitar número de imágenes a evaluar",
    )
    args = parser.parse_args()

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(args.images_dir.glob("*.bmp"))
    if not image_paths:
        print(f"⚠️ No se encontraron imágenes BMP en {args.images_dir}")
        return 1

    print(f"🔬 CONGELANDO BASELINE DoG (sigma1={args.sigma1}, sigma2={args.sigma2})")
    print(f"   Imágenes a evaluar: {len(image_paths)}")

    resultados: List[dict] = []
    total_tp = 0
    total_fp = 0
    total_fn = 0

    for img_path in image_paths:
        image_id = img_path.stem
        cells_csv = args.gt_dir / f"{image_id}_cells.csv"
        if not cells_csv.exists():
            print(f"   ⚠️ Falta GT para {image_id}: {cells_csv}")
            continue

        res = evaluar_imagen_herlev(
            img_path,
            cells_csv,
            sigma1=args.sigma1,
            sigma2=args.sigma2,
            distancia_max=args.match_distance,
        )
        if res:
            resultados.append(res)
            total_tp += res["tp"]
            total_fp += res["fp"]
            total_fn += res["fn"]
            print(f"   • {image_id}: TP={res['tp']}, FP={res['fp']}, FN={res['fn']}, F1={res['f1']:.4f}")

    # Guardar CSV
    fieldnames = [
        "image_id",
        "tp",
        "fp",
        "fn",
        "precision",
        "recall",
        "f1",
        "jaccard",
        "pred_count",
        "gt_count",
    ]
    with args.output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in resultados:
            writer.writerow(r)

    print(f"\n💾 Baseline guardado en: {args.output_csv}")
    p_global = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    r_global = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1_global = 2 * (p_global * r_global) / (p_global + r_global) if (p_global + r_global) > 0 else 0.0

    print("=" * 60)
    print("RESUMEN GLOBAL BASELINE DoG (Herlev)")
    print(f"  TP total: {total_tp}")
    print(f"  FP total: {total_fp}")
    print(f"  FN total: {total_fn}")
    print(f"  Precision global: {p_global:.4f}")
    print(f"  Recall global:    {r_global:.4f}")
    print(f"  F1-Score global:  {f1_global:.4f}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
