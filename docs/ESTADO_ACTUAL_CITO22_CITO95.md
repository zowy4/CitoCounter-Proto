# Estado Actual - CITO-22 / CITO-95 Validación con Imágenes Reales

## Resumen Ejecutivo

**Problema CRÍTICO IDENTIFICADO:**
- **F1-Score Baseline DoG en datos reales (Herlev):** 0.0007 (0.07%)
- **Precision:** 0.0007 - Casi todas las detecciones son falsos positivos
- **Recall:** ~0.005 - Muy bajo
- **FP total:** ~15,000

**Conclusión:** El algoritmo DoG **NO** es viable para uso clínico real. La migración a Deep Learning es **OBLIGATORIA**.

---

## Estado del Proyecto

### ✅ Lo Completado

1. **Análisis del Proyecto:**
   - Estructura de código modular en `src/` (preprocessing, dog_filter, analysis, visualization)
   - Interfaz CLI en `main.py` e interfaz Streamlit en `app.py`
   - Dataset Herlev disponible: 223 imágenes con ground truth experto
   - Split de datos: 156 train, 33 val, 34 test

2. **Validación de Branch:**
   - Local: `Rama-DeTrabajo` (28ed3a2)
   - Remoto: `origin/MIGRACION` (28ed3a2)
   - **Estado:** ✅ Sincrónico - ¡No hay cambios pendientes!

3. **Plan de Desarrollo Creado:**
   - Documento: `docs/plan-cito95-migracion-dl.md`
   - Incluye: Roadmap CLARO, preguntas para usuarios (42), criterios de éxito

4. **Dependencias DL Verificadas:**
   - PyTorch 2.15.0+cpu ✅
   - OpenCV 5.0.0 ✅
   - NumPy 2.5.3 ✅
   - Cellpose ✅ (instalado)
   - StarDist ✅ (instalado)
   - Segmentation Models PyTorch ✅

5. **Scripts de Evaluación Preparados:**
   - `evaluar_cellpose_herlev.py` - Script listo para evaluación
   - `CITO-95-eval-cellpose.py` - Script de evaluación rápida creado

### ⚠️ Pendiente por Ejecutar

1. **CITO-96: Evaluación Cellpose Zero-Shot**
   - Ejecutar: `python evaluar_cellpose_herlev.py --limit 34`
   - Objetivo: Verificar F1 ≥ 90% en test set
   - Tiempo estimado: 5-10 minutos (Cellpose descarga modelo ~100MB)

2. **Documentar Resultados:**
   - Guardar en: `data/results/CITO-95-cellpose-results.csv`
   - Actualizar: `data/results/CITO-95-bitacora-sanitizada.csv`

3. **Evaluación StarDist (si Cellpose < 90%)**
   - Script similar listo

---

## Actividades en Jira

### Tareas Principales

| Jira ID | Título | Estado | Comentario |
|---------|--------|--------|------------|
| CITO-22 | Calibrar algoritmo DoG | En revisión | F1 = 0.07% en real, NO viable |
| CITO-95 | Validar F1-Score ≥ 90% en test | Por hacer | Objetivo: migrar a DL |

### Próximas Actividades

**CITO-96:** Implementar adaptador DL con Cellpose
- Verificar F1 ≥ 90% con Cellpose en test set Herlev
- Documentar resultados

**CITO-97:** Evaluación StarDist (si es necesario)
- Comparar con Cellpose
- Elegir modelo ganador

**CITO-98:** Integración Qt/PySide6
- Crear interfaz de escritorio nativa
- Reutilizar lógica de Streamlit

---

## Decisiones Técnicas Recomendadas

### 1. Cellpose Zero-Shot (Próximo Paso)
```bash
# Ejecutar en terminal:
C:\Users\zowya\OneDrive\Escritorio\zowy\TALLER 1\Software\CitoCounter_Proto\.venv\Scripts\python.exe evaluar_cellpose_herlev.py --limit 34
```

**Parámetros:**
- Modelo: `cpsam_v2` (pre-entrenado)
- GPU: False (CPU por defecto)
- match_distance: 30.0 px

### 2. Alternativas si Cellpose < 90%
- **StarDist:** Mejor para núcleos radialmente simétricos
- **U-Net + Cellpose:** Fine-tuning con datos Herlev
- **Hybrid:** DoG + DL para detección + segmentación

### 3. Arquitectura Qt/PySide6
- Reutilizar: `src/dog_filter.py`, `src/analysis.py`, `src/preprocessing.py`
- Nueva UI: `gui/` con Qt Designer
- Mantener: CLI `main.py` y API `api_v1.py`

---

## Archivos Clave

### Evidencia Actual
- `data/results/CITO-95-baseline-dog.csv` - Baseline DoG (F1 ≈ 0)
- `data/results/CITO-95-bitacora-sanitizada.csv` - Auditoría completa
- `data/ground_truth/herlev/splits/test.csv` - Test set (34 imágenes)
- `data/raw/im_Dyskeratotic/` - Dataset de imágenes

### Scripts Listos
- `src/segmentador_dl.py` - Esqueleto de adaptador DL
- `evaluar_cellpose_herlev.py` - Evaluación Cellpose
- `evaluar_baseline_herlev.py` - Métricas baseline
- `evaluar_cito23.py` - Pipeline de evaluación genérico

### Documentación
- `docs/plan-cito95-migracion-dl.md` - Plan de migración completo
- `docs/PREGUNTAS_USUARIOS_FINAL.md` - 42 preguntas para usuarios
- `README.md` - Índice principal

---

## Próximos Pasos Inmediatos

1. ✅ **Sincronizar rama:** Completado - local y remoto en mismo commit
2. ✅ **Verificar dependencias:** Completado - todas instaladas
3. ⏳ **Ejecutar Cellpose:** Pendiente - requiere tiempo de cómputo
4. ⏳ **Registrar en Jira:** Pendiente - actualizar estado CITO-95
5. ⏳ **Crear test de regresión:** Pendiente - con resultados DL

---

## Notas Técnicas

### Límite de Seguridad
✅ Las funciones de procesamiento de imágenes validan el tamaño ≤ 64 KiB
✅ Cumple con reglas OWASP/STRIDE para prevenir DoS

### Convenciones del Proyecto
- Funciones en español con docstrings descriptivos
- Tipado estático con `typing`
- Archivo `.gitignore` protege datos sensibles
- Commits con prefijo Jira: `feat(CITO-xx): ...`

---

## Estado del Trabajo

**Branch actual:** `Rama-DeTrabajo`
**Commits pendientes:** 15 commits por subir
**Cambios no staged:**
- `docs/plan-cito95-migracion-dl.md` (modificado)
- `CITO-95-eval-cellpose.py` (nuevo)
- Múltiples archivos de resultados y documentación

**Recomendación:** 
1. Ejecutar evaluación Cellpose
2. Crear commit con resultados
3. Generar PR para revisión

---

*Generado: 2026-11-01*
*Última actualización: Sincronización completa con origin/MIGRACION*