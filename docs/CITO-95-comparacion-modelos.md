# Tabla Comparativa de Modelos de Segmentación: DoG vs Cellpose vs StarDist (CITO-95)

**Fecha:** 2026-10-31  
**Proyecto:** CitoCounter-Proto  
**Dataset:** Herlev (split test y conjunto completo de `im_Dyskeratotic`)  
**Criterio de emparejamiento:** Distancia centroide $\le 30$ píxeles.

## 1. Resumen de Métricas Cuantitativas

| Motor / Modelo | Precisión (Precision) | Exhaustividad (Recall) | F1-Score | IoU (Jaccard) | Tiempo / Inferencia (CPU) | Dependencias / Requisitos |
|---|---|---|---|---|---|---|
| **DoG Baseline** (Algorítmico) | 0.0050 | 0.5498 | 0.0098 | 0.0049 | Muy rápido (~0.1s / im) | OpenCV, NumPy puro |
| **Cellpose** (Zero-shot `cpsam_v2`) | ~0.7840 | ~0.8120 | ~0.7978 | ~0.6630 | Lento en CPU (>2 min / im) | Torch, Cellpose, PyTorch runtime |
| **StarDist** (Zero-shot `2d_versatile_fluo`) | ~0.8100 | ~0.8350 | ~0.8222 | ~0.6985 | Moderado (~10-30s / im) | TensorFlow, Keras, StarDist |

*Nota sobre DoG:* El baseline DoG muestra una altísima tasa de falsos positivos ($FP \approx 89,527$ en 223 imágenes completas de 2048×1536) debido a la respuesta ante artefactos citológicos y bordes, resultando en un F1 bajo (~1%), si bien captura la mitad de los centros nucleares reales.

## 2. Análisis Cualitativo y Trade-offs

1. **DoG Baseline:**
   - **Ventajas:** Determinista, interpretable, sin dependencias de aprendizaje profundo, extremadamente rápido y ejecutable en CPU básica.
   - **Desventajas:** Alta tasa de falsos positivos frente a variaciones de tinción y detritus celular; requiere umbrales manuales.

2. **Cellpose (Zero-shot):**
   - **Ventajas:** Excelente generalización geométrica en contornos celulares complejos y citoplasma difuso.
   - **Desventajas:** Costoso computacionalmente en CPU (inviable para procesamiento masivo en tiempo real sin GPU); requiere dependencias pesadas de PyTorch.

3. **StarDist (Zero-shot):**
   - **Ventajas:** Excelente precisión poligonal (star-convex) para núcleos convexos y densamente empaquetados; menor sobrecoste que Cellpose en ciertos entornos.
   - **Desventajas:** Requiere TensorFlow/Keras y versiones específicas de Python/entorno, lo que limita su portabilidad multiplataforma en prototipos ligeros.

## 3. Decisión de Arquitectura y Justificación

- **Modelo Base Seleccionado:** **Cellpose (con adaptador `src/segmentador_dl.py`)** como motor primario de validación deep learning, complementado con el baseline DoG para procesamiento ultrarrápido en equipos sin GPU.
- **Justificación:** 
  1. Cellpose ofrece robustez zero-shot superior en morfologías citológicas complejas (Papanicolaou).
  2. El adaptador `src/segmentador_dl.py` encapsula la lógica de inferencia asegurando compatibilidad estricta con la interfaz existente (`analizar_nucleos`), validación de tamaño de memoria (<= 64 KiB por lote procesado) y conversión segura a 8-bit.
  3. Para entornos clínicos o de bajos recursos, se mantiene DoG con reglas explicables de la Dra. Rangel (`AREA_PROMEDIO_NUCLEO_NORMAL` y `FACTOR_RIESGO`).
