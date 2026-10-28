# FASE 2: Diagnóstico del Ground Truth - CITO-23

## ⚠️ SITUACIÓN CRÍTICA

La validación de métricas en CITO-23 **falló completamente (0% TP, 0% recall)** porque:

**NO EXISTE GROUND TRUTH PARA VALIDAR**

### Hallazgos

| Elemento | Estado | Detalles |
|----------|--------|----------|
| **Imágenes en dataset** | ✅ 101 imágenes | `data/raw/MUESTRA_001.jpg` a `MUESTRA_101.jpg` |
| **Dataset Index** | ✅ Completado | `data/dataset_index.csv` mapea cada MUESTRA_NNN.jpg al nombre original |
| **Etiquetas YOLO** | ❌ **FALTA** | Solo `CitoDataset_v1/labels/train/IMG_001.txt` (1 de 101) |
| **Archivo de etiquetas faltantes** | ❌ **CRÍTICO** | Faltan 100 archivos: `078.txt`, `063.txt`, `042.txt`, etc. |

### Estructura esperada vs. real

```
ESPERADO:
CitoDataset_v1/labels/train/
├── 078.txt (10 anotaciones - MUESTRA_001.jpg)
├── 063.txt (N anotaciones - MUESTRA_002.jpg)
├── 042.txt
├── 035.txt
└── ... (100 más)

REALIDAD:
CitoDataset_v1/labels/train/
└── IMG_001.txt (10 anotaciones - no mapea a ninguna MUESTRA)
```

## Opciones de Solución

### Opción A: Crear Ground Truth Sintético (RÁPIDO, para testing)
1. Generar anotaciones YOLO automáticas usando heurísticas
2. Manual review rápida de 10 imágenes de prueba
3. **Tiempo**: 2-4 horas
4. **Resultado**: Dataset de validación parcial para calibración

**Recomendación**: Iniciar con esto para poder continuar con CITO-23/J-07

### Opción B: Anotación Manual Experta (CORRECTO, lento)
1. Convocar personal médico/citotécnicos
2. Usar herramienta de anotación (LabelImg, Roboflow)
3. Doble revisión para concordancia
4. **Tiempo**: 2-4 semanas (depende equipo disponible)
5. **Resultado**: Ground truth validado y citológicamente correcto

### Opción C: Usar datos sintéticos existentes
1. Revisar si hay datos en `generar_datos_sinteticos.py`
2. Crear núcleos virtuales con parámetros conocidos
3. **Tiempo**: 1-2 horas de setup
4. **Resultado**: Ground truth 100% controlado para pruebas

## Plan Inmediato (RECOMENDADO)

Combinar **Opción A + C**:

1. **Fase 2.1** (1 hora): Crear script de generación de ground truth sintético
   - Generar 10 imágenes de prueba con núcleos simulados
   - Anotaciones YOLO generadas automáticamente
   - Test del validador contra datos conocidos

2. **Fase 2.2** (2-3 horas): Anotación rápida de 10 imágenes reales
   - Seleccionar 10 imágenes del lote existente
   - Manual review: trazar núcleos en herramienta rápida
   - Generar archivos YOLO para validación

3. **Fase 2.3** (Continuación): Proceder con recalibración DoG (Fase 3)
   - Usar 5 imágenes para calibración
   - Usar 5 imágenes para evaluación
   - Grid search en parámetros

## Archivos Generados en esta Fase

- ✅ `FASE2-diagnostico-groundtruth.md` (este archivo)
- ✅ `validar_metricas_cito23.py` (script mejorado de validación)
- ✅ `generar_groundtruth_sintetico.py` (Fase 2.1, completado)
- ✅ `tests/test_generar_groundtruth_sintetico.py` (4 pruebas)
- ✅ `tests/test_validar_metricas_cito23.py` (métricas contra verdad conocida, 8 pruebas)
- 📝 `anotaciones_rapidas.txt` (Fase 2.2, pendiente — requiere experta)

## ✅ FASE 2.1 COMPLETADA (2026-09-13)

### Entregables

1. **`generar_groundtruth_sintetico.py`**: genera imágenes sintéticas tipo citología
   con núcleos de geometría conocida (elipses, áreas coherentes con las reglas
   CITO-24: normales 220-420 px², sospechosas 950-1500 px²) y anotaciones YOLO
   automáticas. Conjuntos SEPARADOS de calibración (SINTETICA_001..005) y
   evaluación (SINTETICA_101..105), semilla reproducible (default 42), CLI.
2. **`validar_metricas_cito23.py` parametrizado**: `--images-dir`, `--labels-dir`,
   `--index`, `--output-prefix`, `--sigma1`, `--sigma2`, `--images`; modo automático
   (todas las imágenes del índice con etiqueta); JSON v1.1 con metadatos.
3. **Validación ejecutada** contra el conjunto de evaluación sintético
   (`data/results/CITO-23-validacion-sintetica.txt/.json`).

### Resultado de la validación sintética (sigma 3/5, umbral IoU 0.5)

| Métrica | Valor |
|---------|-------|
| Imágenes evaluadas | 5 (SINTETICA_101..105) |
| TP | 78 |
| FP | 0 |
| FN | 0 |
| Precision | 1.0000 |
| Recall | 1.0000 |
| F1 | 1.0000 |
| Mean IoU | 0.7159 |

**Interpretación**: el PIPELINE DE MÉTRICAS (índice → etiquetas YOLO → detección →
emparejamiento greedy por IoU → reporte) queda validado de punta a punta contra
verdad conocida al 100%. El IoU medio 0.7159 (no 1.0) es correcto y esperado:
las detecciones se serializan como cajas cuadradas de lado √área mientras el GT
es elíptico (IoU círculo-cuadrado concéntricos ≈ 0.785).

### 🔬 HALLAZGO ESTRUCTURAL: polaridad de detección

Durante la Fase 2.1 se identificó la causa del 0% TP sobre imágenes reales:

1. **El pipeline DoG+Otsu actual detecta núcleos CLAROS sobre fondo OSCURO**
   (tipo fluorescencia). Verificado: la imagen sintética SINTETICA_101 invertida
   produce 16/16 detecciones con áreas coincidentes con el GT.
2. **Las imágenes reales (EDF/MUESTRA) tienen núcleos OSCUROS sobre fondo claro**
   (tipo campo claro, tinción Papanicolaou). Tras `NORM_MINMAX` + `THRESH_BINARY+OTSU`,
   el FONDO queda como región blanca → un único contorno gigante descartado por
   área (>5000 px²) → 0-1 detecciones por imagen.
3. **Discrepancia con la bitácora resuelta**: los conteos históricos (p. ej.
   T-005-01: EDF000.png sigma 3/5 → 219 células) se registraron ANTES de los
   filtros de área de CITO-24 (AREA_MINIMA=50 px²). Esos conteos incluían
   fragmentos de ruido de 1-30 px². Con las reglas actuales, EDF000 con 3/5
   produce 1 detección válida (354 px²).

### Implicación para Fase 2.3 (recalibración DoG)

Antes de cualquier grid search sobre sigma, el equipo debe decidir cómo alinear
la polaridad del pipeline con las imágenes reales. Opciones documentadas:
- **A**: invertir la imagen en el preprocesamiento (255 - gris) antes del DoG.
- **B**: umbralizar la respuesta DoG negativa (`THRESH_BINARY_INV` o g2-g1).
- **C**: mantener el pipeline para dominio fluorescencia y adquirir imágenes
  en ese dominio.

Esta decisión es de CITO-22/CITO-23 (calibración) y requiere re-ejecutar el
barrido de calibración tras el cambio; NO se modificó el pipeline en esta fase.

## Decisión Registrada

Para no bloquear el proyecto, se procede con:
- Ground truth parcial (10-20 imágenes con anotaciones)
- Datos sintéticos para testing inicial
- Documentación de qué datos tienen validación experta vs. automática

**Bloqueador Final**: Antes de cualquier conclusión clínica, se requiere validación de todo el dataset con experto citológico.

---

Elaborado: 2026-09-13
Estado: Fase 2.1 completada; Fase 2.2 (anotación experta) pendiente — bloqueador humano
Siguiente: Fase 2.2 - Anotación experta de 10 imágenes reales; Fase 2.3 - decisión de polaridad + recalibración
