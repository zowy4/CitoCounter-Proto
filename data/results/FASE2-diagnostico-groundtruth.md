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
- 📝 `generar_groundtruth_sintetico.py` (próximo)
- 📝 `anotaciones_rapidas.txt` (próximo)

## Decisión Registrada

Para no bloquear el proyecto, se procede con:
- Ground truth parcial (10-20 imágenes con anotaciones)
- Datos sintéticos para testing inicial
- Documentación de qué datos tienen validación experta vs. automática

**Bloqueador Final**: Antes de cualquier conclusión clínica, se requiere validación de todo el dataset con experto citológico.

---

Elaborado: 2026-09-13
Estado: En Revisión
Siguiente: Fase 2.1 - Generar Ground Truth Sintético
