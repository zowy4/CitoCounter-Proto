# CITO-70: Splits de Dataset y División Train/Val/Test

**Fecha:** 2026-10-02  
**Responsable:** Zoé Andrés Chacón Zavala  
**Prioridad:** Highest  
**Estado:** En curso  
**Tipo:** Actividad Secuencial (depende de CITO-69)  

---

## 1. Propósito

Definir la división formal del dataset CitoCounter-Proto en conjuntos de train, validation y test, estableciendo protocolo de uso, garantías de anonimización y métricas de evaluación justas para el prototipo de investigación.

---

## 2. Contexto Actual del Dataset

### 2.1. Composición Actual

| Conjunto | Número de Imágenes | Núcleos Aproximados | Descripción |
|----------|-------------------|---------------------|-------------|
| **MUESTRA_001 a MUESTRA_211** | 211 | 71,431 total (99.5% Normal, 0.5% Anormal) | Imágenes JPG estandarizadas en `data/raw/` |
| **SINTÉTICA (20 imágenes)** | 20 | ~5,000 (generados) | Datos sintéticos en `CitoDataset_v1/metadata/clinical_data_synthetic.csv` |
| **IMG_001 (ground truth)** | 1 | ~300 | Imagen con etiquetado YOLO detallado en `CitoDataset_v1/labels/train/` |

**Total:** 232 imágenes (211 reales + 20 sintéticas + 1 ground truth)

### 2.2. Distribución de Clases

| Clase | Porcentaje | Count | Descripción |
|-------|------------|-------|-------------|
| **Normal** | 99.5% | 71,093 | Nucleos citológicos normales |
| **Anormal** | 0.5% | 337 | Nucleos con características sospechosas |
| **Artifact** | 0% | 0 | Nucleos artefacto (fuera de rango) |

**Nota:** El dataset tiene sesgo hacia clases normales (211 imágenes vs 20 sintéticas con anomalias).

---

## 3. Propuesta de Splits

### 3.1. División Recomendada

| Split | Porcentaje | Imágenes | Propósito |
|-------|------------|----------|-----------|
| **Train** | 70% | 163 imágenes | Entrenamiento de modelo |
| **Validation** | 20% | 47 imágenes | Validación de hiperparámetros |
| **Test** | 10% | 22 imágenes | Evaluación final, métricas reportadas |

**Total:** 232 imágenes (redondeado)

### 3.2. Consideraciones de Anonimización (CITO-69)

- **Todos los splits deben estar anonimizados** - sin nombres de archivo identificables en metadatos públicos
- **MISMAS proporciones de clases** en todos los splits (mantener 99.5% Normal, 0.5% Anormal aproximadamente)
- **Sin superposición** entre splits - cada imagen en exactamente un split
- **Metadatos públicos** solo con información agregada (total, conteos por clase), sin IDs individuales

### 3.3. Restricciones de Uso

| Restricción | Descripción |
|-------------|-------------|
| **Train público** | Puede compartirse para investigación y reproducción de resultados |
| **Validation/Test** | Recomendado mantener en uso interno o bajo acuerdo de material transfer |
| **Sin fuga de datos** | Ninguna imagen puede aparecer en más de un split |
| **Mantener proporción** | La distribución de clases normales/anormales debe ser similar en todos los splits |

---

## 4. Protocolo de División

### 4.1. Pasos de Implementación

1. **Barajar el dataset** - Random shuffle con seed fija (ej. `seed=42`) para reproducibilidad
2. **Dividir por proporciones** - 70% train, 20% validation, 10% test
3. **Actualizar `data/dataset_index.csv`** - Agregar columna `Split` (train/val/test)
4. **Mover archivos de imagen** - `data/raw/` organizados en `data/raw/train/`, `data/raw/val/`, `data/raw/test/`
5. **Actualizar etiquetas YOLO** - Mover archivos `.txt` de `CitoDataset_v1/labels/train/` a correspondientes split
6. **Actualizar metadatos** - `CitoDataset_v1/metadata/clinical_data_synthetic.csv` con anotaciones de split
7. **Documentar el proceso** - `DOC-70-01: Protocolo de splits`

### 4.2. Estructura de Archivos Después de la División

```
/data/
  raw/
    train/    - 163 imágenes MUESTRA_XXX.jpg
    val/      - 47 imágenes MUESTRA_XXX.jpg
    test/     - 22 imágenes MUESTRA_XXX.jpg
    ground_truth/ - README.md (sin cambios)
  results/
    graficas_tesis/
    screenshots/

/CitoDataset_v1/
  labels/
    train/    - 163 archivos .txt + val/test subsets
    val/      - 47 archivos .txt
    test/     - 22 archivos .txt
    reporte_etiquetado.txt
  metadata/
    clinical_data_synthetic.csv - actualizado con split info
  classes.txt
  README.md

/data/dataset_index.csv - con columna Split añadida
```

### 4.3. Validación de Splits

| Validación | Descripción | Herramienta |
|------------|-------------|-------------|
| **Sin superposición** | Verificar que ninguna imagen aparezca en más de un split | `python validar_splits.py` |
| **Proporción de clases** | Verificar 99.5% Normal, 0.5% Anormal en cada split | `python validar_consistencia_dataset.py` |
| **Total de imágenes** | 163 + 47 + 22 = 232 | Recuento manual |
| **Metadatos consistentes** | clinical_data_synthetic.csv tiene solo IMG_001 con split=test | Revisión manual |

---

## 5. Dependencias con Otras Actividades JIRA

| Actividad | Tipo de Dependencia | Descripción |
|-----------|--------------------|-------------|
| **CITO-69** | **Paralela (inicia después)** | Privacidad debe definirse primero (anonimización de datos), luego definir splits. CITO-69 → CITO-70. |
| **CITO-71** | **Secuencial (dep. de CITO-70)** | Protocolo de anotación requiere dataset con splits definidos (CITO-70). |
| **CITO-73** | **Independiente (ayuda mutua)** | Correcciones DoG (CITO-42) y contexto clínico (CITO-68) se complementan con mejoras de parámetros después de definir splits. |
| **CITO-75** | **Secuencial (dep. de CITO-70)** | Métricas F1/IoU requieren dataset con splits (CITO-70) antes de calcular y reportar. |
| **CITO-84** | **Depende de todas** | Auditoría final requiere todos los entregables previos, incluye validación de splits (CITO-70). |

---

## 6. Actividades Pendientes CITO-70

### 6.1. Inmediatas (Día 1-2)

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Revisar código actual de `data/dataset_index.csv` | Equipo | 4 | Documento de estado actual |
| Definir seed fija y protocolo de shuffle | Liderazgo | 2 | `DOC-70-01: Protocolo de splits` |
| Mover archivos de imagen a carpetas train/val/test | Ingeniería | 6 | Estructura de carpetas actualizada |
| Mover etiquetas YOLO a carpetas correspondientes | Ingeniería | 4 | Labels organizados por split |

### 6.2. Desarrollo (Día 3-4)

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Actualizar `data/dataset_index.csv` con columna `Split` | Desarrollo | 4 | CSV con 232 filas + columna Split |
| Actualizar `CitoDataset_v1/metadata/clinical_data_synthetic.csv` | Desarrollo | 2 | Metadata con info de split |
| Crear script `validar_splits.py` - validación automática | QA/Desarrollo | 4 | Script passing validation |

### 6.3. Validación y Cierre (Día 5)

| Tarea | Responsable | Horas | Entregable |
|-------|-------------|-------|------------|
| Ejecutar `python validar_splits.py` y verificar passing | QA | 3 | Test report |
| Actualizar `.github/Jira.csv` (estado avanzado) | Responsable CITO-70 | 1 | CSV actualizado |
| Hand-off a CITO-71 (protocolo de anotación) | Responsable CITO-70 | 2 | Documento de handoff |
| Revisar que métricas F1/IoU puedan calcularse después | Equipo | 3 | Validación de flujo de métricas |

---

## 7. Entregables CITO-70

| Entregable | Descripción | Estado |
|------------|-------------|--------|
| **`DOC-70-01: Protocolo de splits`** | Documento con seed, proporciones, pasos de implementación | Pendiente |
| **Estructura de carpetas train/val/test** | `data/raw/train/`, `data/raw/val/`, `data/raw/test/` con imágenes redistribuidas | Pendiente |
| **Labels YOLO por split** | `CitoDataset_v1/labels/train/`, `val/`, `test/` redistribuidos | Pendiente |
| **`data/dataset_index.csv` actualizado** | 232 filas + columna `Split` (train/val/test) | Pendiente |
| **`validar_splits.py` script** | Validación automática de splits (sin superposición, proporciones) | Pendiente |
| **Actualización `.github/Jira.csv`** | CITO-70: fecha inicio, dependencias CITO-71, estado "En curso" | Pendiente |

---

## 8. Métricas de Éxito CITO-70

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| **S1:** Dataset dividido en 3 splits sin superposición | ✅ Pass | Ejecutar `python validar_splits.py` |
| **S2:** Proporción 70/20/10 cumplida (163/47/22) | ✅ Pass | Recuento de imágenes por split |
| **S3:** Proporción de clases mantenida (99.5% Normal, 0.5% Anormal) | ✅ Pass | `python validar_consistencia_dataset.py` |
| **S4:** `data/dataset_index.csv` tiene columna `Split` en 100% de filas | ✅ Pass | Revisión de CSV |
| **S5:** `.github/Jira.csv` actualizado | ✅ Pass | Estado "En curso", dependencias CITO-71 agregadas |

**Criterio de aceptación:** Se cumplen las 5 métricas S1-S5.

---

## 9. Referencias y Normatividad

| Referencia | Descripción |
|------------|-------------|
| **LFPDPPP** (Principio de limitación de uso) | Los datos deben usarse solo para fines especificados |
| **Guías de machine learning** | Train/val/test splits estándar, sin fuga de datos |
| **CITO-69** | Privacidad y anonimización deben mantenerse en todos los splits |
| **Prácticas de investigación** | Reproducibilidad y evaluación justa |

---

## 10. Historial de Versiones

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| **1.0** | 2026-10-02 | Versión inicial. Definición de splits de dataset. | Zoé Andrés Chacón Zavala |

---

## 11. Contacto

**Responsable del proyecto:** Zoé Andrés Chacón Zavala  
**Repositorio:** https://github.com/zowy4/CitoCounter-Proto  
**Correo:** (contacto del proyecto)  
**Fecha de última revisión:** 2026-10-02  

---

**Fin del documento CITO-70**