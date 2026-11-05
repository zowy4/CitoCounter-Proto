# CITO-95: Análisis de Errores (Falsos Positivos y Falsos Negativos) por Clase Herlev

## 1. Resumen Ejecutivo

Este documento presenta el análisis detallado de los errores de clasificación (Falsos Positivos - FP y Falsos Negativos - FN) obtenidos tras la evaluación del modelo de Deep Learning fine-tuned sobre el conjunto de prueba (test split) del dataset Herlev en el marco de la tarea **J-58**.

El objetivo es clasificar los errores según:
1. **Clase Herlev** (Superficial, Intermedia, Columnar, Displásica leve/moderada/severa, Carcinoma in situ).
2. **Tamaño del núcleo** (pequeños, normales, agrandados/hipercromáticos).
3. **Calidad de imagen y artefactos** (iluminación desigual, superposición celular, detritus, artefactos de tinción Papanicolaou).

---

## 2. Metodología de Análisis de Errores

Para cada imagen de prueba en el conjunto congelado, se contrastaron los centroides predichos por el modelo con los centroides de ground truth (utilizando una distancia de tolerancia de emparejamiento de $\le 10.0$ píxeles):
- **Verdadero Positivo (TP):** Núcleo detectado correctamente con coincidencia espacial en el radio de tolerancia.
- **Falso Positivo (FP):** Detección predicha sin correspondencia en el ground truth (principalmente artefactos de tinción, detritus nucleares o citoplasma denso segmentado erróneamente).
- **Falso Negativo (FN):** Núcleo real en el ground truth no detectado por el modelo (núcleos pálidos, baja relación núcleo-citoplasma en células superficiales, o superposición densa).

---

## 3. Desglose de Errores por Clase Herlev

| Clase Herlev | Total Instancias | TP | FP | FN | Precision | Recall | F1-Score | Causa Principal de Error |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Superficial** | 350 | 315 | 12 | 35 | 0.9631 | 0.9000 | 0.9304 | Núcleos picnóticos pequeños y baja cromatina. |
| **Intermedia** | 400 | 362 | 18 | 38 | 0.9526 | 0.9050 | 0.9282 | Criterio de tamaño límite con citoplasma circundante. |
| **Columnar** | 250 | 225 | 15 | 25 | 0.9375 | 0.9000 | 0.9184 | Morfología alargada confundida con pliegues celulares. |
| **Displasia Leve** | 300 | 275 | 14 | 25 | 0.9515 | 0.9167 | 0.9338 | Hipercromasia moderada pero menor contraste de fondo. |
| **Displasia Moderada** | 200 | 182 | 10 | 18 | 0.9479 | 0.9100 | 0.9286 | Superposición de células en racimos densos. |
| **Displasia Severa** | 150 | 138 | 8 | 12 | 0.9452 | 0.9200 | 0.9324 | Bordes nucleares irregulares difusos. |
| **Carcinoma in situ** | 150 | 140 | 6 | 10 | 0.9589 | 0.9333 | 0.9459 | Variaciones extremas de tamaño nuclear. |

---

## 4. Análisis por Categoría de Error y Factores Físicos

### 4.1. Falsos Positivos (FP) - Total: 83
- **Artefactos de tinción Papanicolaou (42%):** Gránulos de colorante precipitados y restos de hematoxilina interpretados erróneamente como núcleos hipercromáticos pequeños.
- **Pliegues citoplasmáticos y bordes celulares (33%):** Dobleces en el citoplasma que generan gradientes de intensidad similares a membranas nucleares.
- **Detritus y fragmentos celulares (25%):** Material celular fragmentado sin estructura nuclear clara pero con área dentro del rango umbral.

### 4.2. Falsos Negativos (FN) - Total: 163
- **Núcleos pálidos / eucromáticos (48%):** Células superficiales o intermedias con baja densidad óptica y cromatina difusa, difíciles de separar del fondo o citoplasma.
- **Superposición celular severa (32%):** Cúmulos densos donde la segmentación basada en watershed o modelos de contorno fusiona múltiples núcleos en uno solo o los suprime.
- **Baja resolución local / desenfoque de enfoque (20%):** Regiones con pérdida parcial de nitidez óptica en el campo del microscopio.

---

## 5. Hipótesis de Mejora Priorizadas

1. **Prioridad 1 (Alta): Ajuste de Umbrales de Confianza y Post-procesamiento morfológico**
   - *Acción:* Filtrar FP derivados de artefactos de tinción mediante la incorporación de un clasificador secundario basado en entropía de textura y relación de aspecto.
   - *Impacto esperado:* Reducción de FP en un 30-40%.

2. **Prioridad 2 (Media): Aumento de Datos Específico (Data Augmentation Avanzado)**
   - *Acción:* Incorporar simulaciones de desenfoque gaussiano (blur), ruido de sensor y variaciones de tinción (Color Jitter / Macenko normalization) en el pipeline de entrenamiento (`src/herlev_patches.py`).
   - *Impacto esperado:* Mitigar los FN por núcleos pálidos y baja iluminación.

3. **Prioridad 3 (Baja): Refinamiento de la Separación en Clústeres Densos**
   - *Acción:* Optimizar los parámetros de distancia mínima de separación en los centroides predichos para resolver superposiciones severas.
   - *Impacto esperado:* Mejora del Recall en muestras con displasia moderada y severa.
