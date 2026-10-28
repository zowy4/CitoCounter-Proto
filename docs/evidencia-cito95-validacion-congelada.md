# CITO-95: Validación con dataset congelado

## Estado actual: **BLOQUEADO para imágenes reales**

### Validación en datos sintéticos (COMPLETADA - CITO-85)
CITO-95 reutiliza la validación formal de CITO-85 sobre `data/sintetico/evaluacion`, separado del conjunto de calibración.

La configuración congelada fue `sigma1=5.0`, `sigma2=8.0`, apertura final 5 y `watershed`. Con matching espacial uno a uno e `IoU > 0.50`, el reporte `CITO-85-validacion-formal.json` registra:

- Precision: 1.0000
- Sensibilidad: 0.8718
- F1: 0.9315
- IoU medio: 0.7308

**El criterio F1 ≥ 0.90 se cumple en datos sintéticos.** ✅

> **⚠️ Limitación crítica:** Esta evidencia es **sintética y experimental**; no sustituye validación clínica con anotaciones expertas reales en imágenes Papanicolaou/EDF.

---

## Limitación fundamental del DoG en imágenes reales (DESCUBIERTA EN CITO-94/CITO-97)

### Hallazgo crítico
El algoritmo **Difference of Gaussians (DoG) no es adecuado para imágenes Papanicolaou/EDF 2048x1536** sin preprocesamiento avanzado que no existe actualmente.

| Métrica | Datos sintéticos | Imágenes reales (Papanicolaou/EDF) |
|---------|------------------|-----------------------------------|
| F1-Score | **0.9315** ✅ | **0.0000** ❌ |
| Precision | 1.0000 | 0.0000 |
| Recall | 0.8718 | 0.0000 |

### Causa raíz
Los **artefactos de borde del DoG dominan la respuesta** en imágenes reales:

- **Artefactos DoG en bordes:** 150-255 (dominan la imagen)
- **Núcleos reales:** 87-113 (respuesta más débil)
- **Extensión de artefactos:** 900px+ desde borde izquierdo, 500px+ desde inferior
- **Máscara asimétrica requerida:** >80% de la imagen (inviable)

### Evidencia experimental (CITO-94/CITO-97)
```
MUESTRA_014: Basic=6, Watershed=111, MaxLoc=0 (TP=0 en todos)
MUESTRA_056: Basic=7, Watershed=83, MaxLoc=0 (TP=0 en todos)  
MUESTRA_001: Basic=34, Watershed=29, MaxLoc=0 (TP=0 en todos)
```

---

## Plan para desbloquear CITO-95: Enfoque Deep Learning

### Opción recomendada: Cellpose / StarDist / U-Net

| Enfoque | Ventajas | Desventajas | Esfuerzo estimado |
|---------|----------|-------------|-------------------|
| **Cellpose** | Pre-entrenado para núcleos, zero-shot, fácil integración | Requiere PyTorch, GPU recomendada | 2-3 semanas |
| **StarDist** | Especializado en núcleos, probabilístico | Requiere TensorFlow/PyTorch | 3-4 semanas |
| **U-Net custom** | Control total, optimizable para Papanicolaou | Requiere entrenamiento, más datos | 4-6 semanas |

### Recomendación: **Cellpose** (inicio rápido)
- Modelo `cyto2` o `nuclei` pre-entrenado funciona bien en citología
- API simple: `model.eval(image, channels=[0,0])`
- Compatible con CPU (lento) y GPU (rápido)
- Licencia BSD-3, uso comercial permitido

### Dependencias a agregar
```txt
# Deep Learning - PARA VALIDACIÓN REAL (CITO-95)
torch==2.1.0              # PyTorch para Cellpose/StarDist
cellpose==3.0.0           # Segmentación de núcleos zero-shot
# O alternativamente:
# stardist==0.9.1         # StarDist para núcleos
# segmentation-models-pytorch==0.3.0  # U-Net, FPN, etc.
```

### Pasos de implementación

1. **Semana 1-2**: Agregar dependencias, crear wrapper `src/deep_learning.py`
2. **Semana 2-3**: Integrar Cellpose en pipeline (`analizar_nucleos_dl()`)
3. **Semana 3-4**: Validar en `data/raw/` con ground truth de `CitoDataset_v1/`
4. **Semana 4**: Comparar DoG vs Cellpose, documentar en CITO-95

### Métricas objetivo para imágenes reales
| Métrica | Objetivo | Nota |
|---------|----------|------|
| F1-Score | ≥ 0.90 | Requisito CITO-95 |
| Precision | ≥ 0.85 | Evitar falsos positivos |
| Recall | ≥ 0.85 | Detectar mayoría de núcleos |
| IoU medio | ≥ 0.70 | Calidad de segmentación |

---

## Decisión requerida

**¿Proceder con implementación Deep Learning (Cellpose) para desbloquear CITO-95 en imágenes reales?**

- [ ] **SÍ** - Agregar PyTorch/Cellpose, implementar wrapper, validar en datos reales
- [ ] **NO** - Mantener solo validación sintética, documentar limitación como conocida

> **Nota:** La validación sintética (F1=0.9315) ya cumple CITO-95 técnicamente, pero **no es evidencia clínica válida**. Para uso real, se requiere validación en imágenes Papanicolaou/EDF con ground truth experto.
