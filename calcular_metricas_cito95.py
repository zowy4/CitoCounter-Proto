"""
Resumen métricas CITO-95 Baseline DoG
"""
import csv
from pathlib import Path

csv_path = Path('data/results/CITO-95-baseline-dog.csv')
with csv_path.open('r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

tp = sum(int(r['tp']) for r in rows)
fp = sum(int(r['fp']) for r in rows)
fn = sum(int(r['fn']) for r in rows)

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

print("=" * 70)
print("RESUMEN MÉTRICAS CITO-95 BASELINE DoG (Herlev 223 imágenes)")
print("=" * 70)
print(f"Imágenes evaluadas: {len(rows)}")
print(f"TP total: {tp}")
print(f"FP total: {fp}")
print(f"FN total: {fn}")
print(f"Precision: {precision:.6f} ({precision*100:.4f}%)")
print(f"Recall: {recall:.6f} ({recall*100:.4f}%)")
print(f"F1-Score: {f1:.6f} ({f1*100:.4f}%)")
print("=" * 70)
print()
print("DECISIÓN: F1 ≈ 0.93% << 90% objetivo")
print("CONCLUSIÓN: Baseline DoG NO funciona en datos reales.")
print("RECOMENDACIÓN: Migrar a Deep Learning (Cellpose/StarDist/U-Net)")