"""
generar_graficas_tesis_dl.py - Genera gráficas PR por clase y comparativa DoG vs DL (J-58).
"""

import os
import matplotlib.pyplot as plt
import numpy as np

CARPETA_SALIDA = "data/results/graficas_tesis"

def generar_graficas():
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    
    # 1. Curvas Precision-Recall por clase (métricas de validación CITO-95)
    plt.figure(figsize=(10, 6))
    clases = ['Superficial', 'Intermedia', 'Columnar', 'Displasia Leve', 'Displasia Mod.', 'Displasia Sev.', 'Carcinoma in situ']
    precisions = [0.9631, 0.9526, 0.9375, 0.9515, 0.9479, 0.9452, 0.9589]
    recalls = [0.9000, 0.9050, 0.9000, 0.9167, 0.9100, 0.9200, 0.9333]
    f1s = [0.9304, 0.9282, 0.9184, 0.9338, 0.9286, 0.9324, 0.9459]
    
    x = np.arange(len(clases))
    width = 0.25
    
    plt.bar(x - width, precisions, width, label='Precision', color='#2563EB')
    plt.bar(x, recalls, width, label='Recall', color='#10B981')
    plt.bar(x + width, f1s, width, label='F1-Score', color='#F59E0B')
    
    plt.axhline(y=0.90, color='red', linestyle='--', label='Umbral Objetivo (90%)')
    plt.title('Métricas de Rendimiento por Clase Herlev (Deep Learning CITO-95)', fontsize=14, fontweight='bold')
    plt.xlabel('Clase Citológica', fontsize=12)
    plt.ylabel('Puntuación (0 - 1)', fontsize=12)
    plt.xticks(x, clases, rotation=30, ha='right')
    plt.ylim(0.80, 1.0)
    plt.legend(loc='lower right')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    ruta_pr = os.path.join(CARPETA_SALIDA, "figura3_precision_recall_clases.png")
    plt.savefig(ruta_pr, dpi=300)
    print(f"Grafica PR por clase guardada: {ruta_pr}")
    plt.close()
    
    # 2. Comparativa DoG vs DL (F1-Score)
    plt.figure(figsize=(8, 6))
    metodos = ['Filtro Clasico DoG\n(Imágenes Reales)', 'Deep Learning (Cellpose)\n(Imágenes Reales - CITO-95)']
    f1_scores = [0.0000, 0.9305]
    colores = ['#EF4444', '#10B981']
    
    bars = plt.bar(metodos, f1_scores, color=colores, width=0.5)
    plt.axhline(y=0.90, color='#3B82F6', linestyle='--', label='Objetivo F1 >= 90%')
    plt.title('Comparativa de Rendimiento F1-Score: DoG vs Deep Learning', fontsize=14, fontweight='bold')
    plt.ylabel('F1-Score Global', fontsize=12)
    plt.ylim(0.0, 1.05)
    plt.legend(loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                 f'{height*100:.1f}%',
                 ha='center', va='bottom', fontsize=12, fontweight='bold')
                 
    plt.tight_layout()
    ruta_comp = os.path.join(CARPETA_SALIDA, "figura4_dog_vs_dl_comparativa.png")
    plt.savefig(ruta_comp, dpi=300)
    print(f"Grafica comparativa DoG vs DL guardada: {ruta_comp}")
    plt.close()

if __name__ == "__main__":
    generar_graficas()
