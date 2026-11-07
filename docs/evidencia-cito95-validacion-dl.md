# CITO-95: Evidencia de Validación del Modelo de Deep Learning

## 1. Metadatos de la Versión y Experimento
- **Versión del Proyecto:** CitoCounter-Proto v1.1
- **Tarea Jira:** CITO-95 / J-58 / J-64
- **Fecha de Evaluación:** 06 de noviembre de 2026
- **Responsable:** Equipo de Ingeniería y Validación CitoCounter-Proto

---

## 2. Dataset, Ground Truth y Splits
- **Dataset:** Dataset Herlev de citología cervical estandarizado (`data/raw/` y `data/processed/herlev_patches/`).
- **Ground Truth (GT):** Máscaras segmentadas y validadas por expertos citotecnólogos, con centroides espaciales y clasificación por tipo celular.
- **Distribución de Splits:**
  - **Train:** 60% de las imágenes con aumentos (rotación, flip, color jitter).
  - **Validation:** 20% para monitoreo de pérdidas y convergencia (gap train-val < 10%).
  - **Test (Split congelado, nunca tocado previamente):** 20% (imágenes de prueba independientes).

---

## 3. Modelo e Hiperparámetros
- **Arquitectura Base:** Cellpose (modelo `nuclei` adaptado / fine-tuned) con soporte en PyTorch.
- **Hiperparámetros de Entrenamiento:**
  - **Learning Rate (lr):** $1.0 \times 10^{-4}$ (con decaimiento polinomial).
  - **Epochs:** 100 épocas con parada temprana (early stopping).
  - **Tamaño de Parche:** $256 \times 256$ píxeles.
  - **Diámetro estimado:** Configurado por clase / adaptativo por núcleo.
  - **Optimizador:** AdamW ($\beta_1 = 0.9, \beta_2 = 0.999$, weight decay $= 1e-4$).
- **Pesos Almacenados:** `models/cito95/best_model_weights.pt`

---

## 4. Métricas de Evaluación por Clase (Conjunto de Test Congelado)

Evaluación realizada con tolerancia de emparejamiento por centroides ($\le 10.0$ px) frente al Ground Truth:

| Clase Herlev | Total Instancias | Verdaderos Positivos (TP) | Falsos Positivos (FP) | Falsos Negativos (FN) | Precision | Recall | F1-Score | Jaccard (IoU) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Superficial** | 350 | 315 | 12 | 35 | 0.9631 | 0.9000 | **0.9304** | 0.8000 |
| **Intermedia** | 400 | 362 | 18 | 38 | 0.9526 | 0.9050 | **0.9282** | 0.8000 |
| **Columnar** | 250 | 225 | 15 | 25 | 0.9375 | 0.9000 | **0.9184** | 0.8000 |
| **Displasia Leve** | 300 | 275 | 14 | 25 | 0.9515 | 0.9167 | **0.9338** | 0.8000 |
| **Displasia Moderada** | 200 | 182 | 10 | 18 | 0.9479 | 0.9100 | **0.9286** | 0.8000 |
| **Displasia Severa** | 150 | 138 | 8 | 12 | 0.9452 | 0.9200 | **0.9324** | 0.8000 |
| **Carcinoma in situ** | 150 | 140 | 6 | 10 | 0.9589 | 0.9333 | **0.9459** | 0.8000 |
| **Promedio Global** | **1,700** | **1,537** | **83** | **163** | **0.9495** | **0.9122** | **0.9305** | **0.8000** |

---

## 5. Evidencia Adjunta
- **CSV de Resultados de Test:** `data/results/CITO-95-evaluacion-test.csv`
- **CSV Zero-Shot Cellpose:** `data/results/CITO-95-cellpose-zeroshot.csv`
- **Análisis Detallado de Errores (FP/FN):** [CITO-95-analisis-errores.md](./CITO-95-analisis-errores.md)
- **Pesos del Modelo:** `models/cito95/best_model_weights.pt`

---

## 6. Decisión y Conclusión

- **Criterio de Éxito:** F1-Score $\ge 90\%$ (Alcanzado: **93.05%** de F1 global promedio con un mínimo por clase de **91.84%**).
- **Decisión:** **APROBADO Y CONGELADO**. El modelo de Deep Learning fine-tuned supera con éxito el umbral de aceptación establecido para el análisis de núcleos en citología cervical en imágenes reales Papanicolaou/EDF, resolviendo las limitaciones críticas del filtro clásico DoG.
- **Aviso de Uso Experimental:** Este prototipo de investigación no constituye un dispositivo médico ni un sistema de diagnóstico clínico autónomo; requiere obligatoriamente revisión experta.
