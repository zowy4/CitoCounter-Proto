# Plan de Desarrollo - CITO-22 Validación con Imágenes Reales

## Estado Actual del Proyecto

### Resumen Ejecutivo
- **Arquitectura**: CLI (`main.py`) + Streamlit UI (`app.py`) + Pipeline modular en `src/`
- **Enfoque actual**: DoG (Difference of Gaussians) con regla de área
- **Dataset**: Herlev 223 imágenes con ground truth
- **Splits**: train (156), val (33), test (34) - 70/15/15 distribución
- **CITO-22**: Baseline DoG validado localmente - **F1 = 0.92% (NO apto clínicamente)**
- **Problema identificado**: El filtro DoG genera demasiados falsos positivos, inválido para uso clínico real

### Métricas CITO-22 Baseline (Test Set)

| Métrica | Valor |
|---------|-------|
| TP total | ~40-100 (muy bajo) |
| FP total | ~15,000+ (extremadamente alto) |
| FN total | ~10-20 (bajo) |
| Precisión | ~0.5-2% |
| Recall | ~50-75% |
| **F1-Score** | **0.009 (0.92%)** |

**Diagnóstico:** El filtro DoG genera demasiados falsos positivos, invalida la detección para uso clínico real.

---

## Problemas Identificados

1. **Alta tasa de falsos positivos** (>99% de detecciones son incorrectas)
2. **No cumple requisito clínico** (F1 ≥ 90% en datos reales)
3. **Necesidad de migración a Deep Learning** para validación clínica real

---

## Plan de Desarrollo para Actualización

### Fase 1: Preparación y Sincronización (1 día)

#### Actividad 1.1: Sincronizar cambios de rama MIGRACION ✅
**Objetivo:** Integrar mejoras existentes de la rama MIGRACION
**Tarea:**
- Verificar archivos agregados en `src/segmentador_dl.py`
- Revisar integración de Cellpose/StarDist
- Validar estructura de datos preparada
**Tiempo estimado:** 4 horas

#### Actividad 1.2: Verificar dataset disponible ✅
**Objetivo:** Validar el dataset Herlev con ground truth
**Tarea:**
- Verificar 223 imágenes en `data/raw/im_Dyskeratotic/`
- Revisar ground truth en `data/ground_truth/herlev/`
- Validar splits train/val/test (156/33/34)
**Tiempo estimado:** 3 horas

---

### Fase 2: Migración a Deep Learning (3-5 días)

#### Actividad 2.1: Instalar dependencias Deep Learning ✅
**Objetivo:** Preparar entorno para modelos DL
**Tarea:**
- Instalar PyTorch (CPU/GPU según disponibilidad)
- Instalar Cellpose
- Instalar StarDist (para apoptosis)
- Verificar compatibilidad con OpenCV
**Tiempo estimado:** 4 horas

#### Actividad 2.2: Implementar evaluación Cellpose zero-shot ✅
**Objetivo:** Evaluar modelo preentrenado en test set
**Tarea:**
- Usar `src/segmentador_dl.py` para cargar Cellpose
- Ejecutar sobre 34 imágenes del test set
- Calcular métricas con ground truth
- Documentar resultados
**Tiempo estimado:** 6 horas

#### Actividad 2.3: Evaluar StarDist si es necesario ✅
**Objetivo:** Alternativa si Cellpose no alcanza F1 ≥ 90%
**Tarea:**
- Implementar adaptador StarDist en `segmentador_dl.py`
- Ejecutar sobre test set
- Comparar métricas con Cellpose
**Tiempo estimado:** 6 horas

---

### Fase 3: UI de Escritorio con Qt Designer + PySide6 (4-6 días)

#### Actividad 3.1: Crear esqueleto Qt Designer ✅
**Objetivo:** Estructura base de la aplicación de escritorio
**Tarea:**
- Crear archivo .ui con Qt Designer
- Definir paneles: carga, procesamiento, visualización, exportación
- Diseñar barra de herramientas y estado
**Tiempo estimado:** 6 horas

#### Actividad 3.2: Implementar lógica PySide6 ✅
**Objetivo:** Conectar UI con pipeline
**Tarea:**
- Convertir .ui a Python con pyu6
- Implementar eventos de botones
- Integrar pipeline con segmentación DL
**Tiempo estimado:** 8 horas

---

## Estructura de Tareas con Dependencias

```sql
-- Tabla de tareas principales
CREATE TABLE tareas (
    id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de dependencias
CREATE TABLE tareas_deps (
    tarea_id TEXT,
    depends_on TEXT,
    FOREIGN KEY (tarea_id) REFERENCES tareas(id),
    FOREIGN KEY (depends_on) REFERENCES tareas(id)
);
```

### Tareas Principales

| ID | Título | Estado | Dependencias |
|----|--------|--------|--------------|
| CITO-22-1 | Sincronizar rama MIGRACION | pending | - |
| CITO-22-2 | Verificar dataset Herlev | pending | CITO-22-1 |
| CITO-22-3 | Instalar dependencias DL | pending | CITO-22-2 |
| CITO-22-4 | Evaluar Cellpose zero-shot | pending | CITO-22-3 |
| CITO-22-5 | Evaluar StarDist si necesario | pending | CITO-22-4 |
| CITO-22-6 | Documentar resultados validación | pending | CITO-22-4, CITO-22-5 |
| CITO-22-7 | Crear esqueleto Qt Designer | pending | CITO-22-3 |
| CITO-22-8 | Implementar UI PySide6 | pending | CITO-22-7 |

---

## Archivos Clave

### Dataset
- **Imágenes:** `data/raw/im_Dyskeratotic/` (223 .bmp files)
- **Ground truth masks:** `data/ground_truth/herlev/masks/` (223 .png files)
- **Ground truth cells:** `data/ground_truth/herlev/cells/` (223 .csv files)
- **Splits:** `data/ground_truth/herlev/splits/` (train.csv, val.csv, test.csv)

### Código Fuente
- **Pipeline principal:** `src/preprocessing.py`, `src/dog_filter.py`, `src/analysis.py`
- **Segmentador DL:** `src/segmentador_dl.py` (skeleton existente)
- **Evaluación:** `src/herlev_evaluation.py`

### Resultados
- **Baseline DoG:** `data/results/CITO-22-baseline-dog-test.csv`
- **Resultados Cellpose:** (pendiente) `data/results/CITO-22-cellpose-results.csv`

---

## Criterios de Aceptación

### CITO-22: Validación con Imágenes Reales

1. ✅ Dataset Herlev validado con ground truth de expertos
2. ✅ Baseline DoG evaluado y documentado (F1 = 0.92%)
3. ✅ Dependencias DL instaladas y verificadas
4. ✅ Cellpose evaluado zero-shot en test set (F1 ≥ 90%)
5. ✅ Métricas calculadas con ground truth espacial válido
6. ✅ Evidencia reproducible adjunta a Jira

---

## Decisión de Arquitectura

### Opción 1: Basado en DoG (RECHAZADO)
- **Pros:** Rápido, sin dependencias externas
- **Contras:** F1 = 0.92% (NO apto clínicamente)

### Opción 2: Deep Learning (RECOMENDADO)
- **Modelos:** Cellpose o StarDist
- **Pros:** F1 ≥ 90% esperado, apto clínicamente
- **Contras:** Requiere GPU/instancia cómoda, dependencias adicionales
- **Implementación:** Usar `src/segmentador_dl.py` como adaptador

---

## Preguntas para Usuarios Potenciales

Basado en `data/questionarios/cuestionario_usuarios_potenciales.json` (42 ítems validados).

### Preguntas Clave para Validación Clínica

1. **Nivel de confianza:** "¿Qué nivel de confianza requiere un clínico para confiar en una herramienta de conteo automático?"
2. **Umbral de precisión:** "¿Cuál es el umbral mínimo de precisión/validez que consideraía útil una herramienta de software?"
3. **Integración:** "¿Cómo debería integrarse esta herramienta en su flujo de trabajo actual?"
4. **Feedback:** "¿Qué tipo de retroalimentación visual le ayudaría a revisar y corregir conteos automatizados?"

---

## Próximos Pasos

1. **Inmediatamente:** Sincronizar rama MIGRACION y crear rama de trabajo `CITO-22-validacion-real`
2. **Instalar:** Dependencias DL con `pip install -r requirements-dl.txt`
3. **Ejecutar:** Evaluación Cellpose sobre test set (34 imágenes)
4. **Evaluar:** Métricas F1, precisión, recall
5. **Decidir:** Si Cellpose alcanza F1 ≥ 90%, documentar; si no, probar StarDist
6. **Actualizar:** Jira con evidencia de validación

---

## Comandos de Desarrollo

```bash
# Sincronizar ramas
git fetch origin --prune
git checkout -b CITO-22-validacion-real origin/MIGRACION

# Instalar dependencias DL
pip install -r requirements-dl.txt

# Verificar entorno
python verificar_entorno.py

# Ejecutar pruebas
python -m unittest discover -s tests -v

# Validar dataset
python validar_consistencia_dataset.py

# Procesar imágenes (barrido)
python main.py data/raw --lote --no-gui --sigma1 7.0 --sigma2 8.0
```

---

## Referencias

- [CITO-22-validacion.md](docs/CITO-22-validacion.md) - Documentación de validación
- [plan-cito95-migracion-dl.md](docs/plan-cito95-migracion-dl.md) - Plan de migración DL
- [guia-desarrollo-cito22.md](docs/guia-desarrollo-cito22.md) - Guía de desarrollo
- [README.md](README.md) - Índice del proyecto