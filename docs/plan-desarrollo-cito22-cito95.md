# Plan de Desarrollo: CITO-22 → CITO-95 (DoG → Deep Learning)

**Fecha:** 2026-10-28  
**Estado:** En desarrollo  
**Responsable:** Zoé Andrés Chacón Zavala  

---

## 1. Análisis del Proyecto Actual

### 1.1 Estructura del Proyecto

| Componente | Archivo | Descripción |
|------------|---------|-------------|
| CLI Principal | `main.py` | Pipeline de análisis con argumentos --no-gui, --sigma1, --sigma2 |
| UI Streamlit | `app.py` | Dashboard web para análisis interactivo |
| Preprocesamiento | `src/preprocessing.py` | Carga, conversión a gris, contraste y calidad de imagen |
| Filtro DoG | `src/dog_filter.py` | Difference of Gaussians para detección de núcleos |
| Análisis | `src/analysis.py` | Contornos, filtros de área y clasificación por referencia |
| Visualización | `src/visualization.py` | Paneles y salidas visuales |
| Contratos | `src/contracts/pipeline_contract.py` | Definiciones de tipos e interfaces |
| Schema Resultados | `src/result_schema.py` | Esquema canónico de resultados |
| Segmentador DL | `src/segmentador_dl.py` | Adaptador para Cellpose/StarDist (draft) |

### 1.2 Estado de Actividades en Jira

| CITO | Actividad | Estado | Comentario |
|------|-----------|--------|------------|
| CITO-22 | Calibración DoG con imágenes sintéticas | En revisión | F1=0.9315 sobre conjunto sintético |
| CITO-85 | Validación formal | Finalizado técnicamente | F1=0.9315 sobre sintético (no clínico) |
| CITO-92 | Autenticación API REST | Finalizado | JWT y rate limiting implementados |
| CITO-93 | Endurecer seguridad | En revisión | Logs auditoría, HTTPS pendientes |
| CITO-94 | Casos especiales | Finalizado | Superposición celular y artefactos |
| CITO-95 | Validar F1 ≥ 90% dataset congelado | Finalizado técnicamente | Requiere datos reales para validación clínica |
| CITO-96 | Completar dataset splits | Bloqueado | Necesario ground truth experto |
| CITO-97 | Calibrar DoG conjunto separado | Finalizado técnicamente | F1=0.9419 sobre sintético, no clínico |

### 1.3 Parámetros DoG Calibrados

**Configuración óptima identificada:**
- `sigma1 = 5.0`
- `sigma2 = 8.0`
- `ratio = 1.6`
- `watershed` con apertura final de 5 píxeles
- `polaridad = nucleos-claros`

**Métricas obtenidas (sintético):**
- Precision: 1.0000
- Sensibilidad: 0.8902
- F1-Score: 0.9419
- IoU medio: 0.7228

---

## 2. Limitaciones Identificadas

### 2.1 Validación Sintética vs Clínica

**Problema CRÍTICO:** Las métricas actuales (F1 ≈ 0.93) se basan en imágenes **sintéticas** generadas con YOLO, no en imágenes reales de Papanicolaou/EDF con ground truth experto. Esto no constituye evidencia clínica válida.

### 2.2 Necesidad de Ground Truth Real

Para validar con imágenes reales se requiere:
1. **Dataset Herlev**: Ya disponible en `data/raw/im_Dyskeratotic/` con archivos `.dat` (polígonos expertos)
2. **Conversión de formatos**: Los `.dat` deben convertirse a máscaras binarias
3. **Procedencia/licencia verificada**: Documentación pendiente sobre uso autorizado

### 2.3 Gap de Implementación DL

El archivo `src/segmentador_dl.py` existe como adaptador parcial pero:
- No está integrado en el pipeline principal
- Falta documentación completa
- Tests parciales existentes (`tests/test_segmentador_dl.py`)

---

## 3. Plan de Desarrollo para CITO-22

### Fase 1: Preparación del Entorno y Línea Base (1-2 días)

**Actividades:**
1. Verificar dependencias y crear entorno de desarrollo
2. Ejecutar baseline DoG sobre dataset sintético existente
3. Documentar resultados en Jira con evidencia adjunta

**Entregables:**
- Entorno de desarrollo configurado
- `data/results/CITO-22-baseline-sintetico.json`
- Comentario en Jira con decisión inicial

### Fase 2: Preparación de Imágenes Autorizadas (3-5 días)

**Actividades:**
1. **Verificar procedencia de Herlev**: Confirmar que `data/raw/im_Dyskeratotic/` puede usarse para validación
2. **Convertir .dat a máscaras**: Rasterizar polígonos expertos a PNG
3. **Separar conjunto de evaluación**: 20-30% de imágenes para evaluación independiente
4. **Documentar autorización**: Adjuntar evidencia de uso permitido

**Entregables:**
- `data/ground_truth/herlev/masks/` (máscaras PNG)
- `data/ground_truth/herlev/splits/test.csv`
- Documento `docs/CITO-22-procedencia-herlev.md`

### Fase 3: Ejecución del Barrido con Imágenes Reales (3-4 días)

**Actividades:**
1. Ejecutar pipeline con `sigma1=5.0, sigma2=8.0` sobre imágenes autorizadas
2. Evaluar métricas con ground truth experto usando `evaluar_cito23.py`
3. Documentar FP/FN por caso especial (superposición, artefactos, iluminación)
4. Ajustar parámetros si es necesario (máximo 1 variación a la vez)

**Entregables:**
- `data/results/CITO-22-evaluacion-real.json`
- `data/results/CITO-22-métricas.csv`
- `docs/evidencia-cito22-evaluacion-real.md`

### Fase 4: Documentación Final en Jira (1 día)

**Actividades:**
1. Adjuntar evidencia completa en incidencia CITO-22
2. Registrar decisión: ¿F1 real ≥ 90%?
3. Si no, determinar próximos pasos (ajuste parámetros vs migración DL)

**Entregables:**
- Comentario cerrado en Jira con evidencia adjunta

---

## 4. Plan de Migración a Deep Learning (CITO-95)

### Objetivo
Alcanzar F1 ≥ 90% en imágenes reales Papanicolaou/EDF con ground truth experto mediante migración de DoG a modelos de Deep Learning.

### Roadmap Propuesto

| Semana | Actividad | Objetivo |
|--------|-----------|----------|
| 1 | Fase 1 + Fase 2 de CITO-22 | Preparar dataset y baseline |
| 2 | Fase 3 de CITO-22 | Evaluar DoG con GT real; decidir si migración necesaria |
| 3 | Zero-shot Cellpose/StarDist | Evaluar modelos preentrenados |
| 4-5 | Fine-tuning con Herlev | Entrenar modelo con F1 objetivo |
| 6 | Integración en pipeline | Adaptar CLI, UI y API |
| 7 | Documentación final | Evidencia completa CITO-95 |

### Modelos Candidate

1. **Cellpose** - Bueno para segmentación de células, fácil de usar
2. **StarDist** - Optimizado para objetos radialmente simétricos
3. **U-Net** - Más flexible, requiere más datos de entrenamiento

---

## 5. Preguntas para Usuarios Potenciales (CITO-88)

### Sección 1: Experiencia con Herramientas de Citología
1. ¿Con qué frecuencia utiliza herramientas de análisis de imágenes en tu trabajo diario?
2. ¿Qué programas o softwares utilizas habitualmente para el conteo de núcleos?

### Sección 2: Usabilidad del Sistema Actual
3. ¿En qué medida cumple con tus necesidades la interfaz de Streamlit actual?
4. ¿Cuáles son los aspectos de la interfaz que te resultan más difíciles o poco intuitivos?
5. ¿Preferirías una aplicación de escritorio nativa (Qt/PySide6) en lugar de una web?

### Sección 3: Funcionalidad y Resultados
6. ¿Cómo valoras la precisión del conteo de núcleos actual (~93% F1 en datos sintéticos)?
7. ¿Qué tan importante es para ti la capacidad de exportar resultados (CSV, imágenes, reportes)?
8. ¿Te gustaría poder procesar lotes de imágenes de forma automática?

### Sección 4: Integración Clínica
9. ¿Qué criterios de calidad usarías para validar un sistema de conteo automático?
10. ¿Qué información adicional necesitarías para confiar en los resultados automáticos?

### Sección 5: Experiencia Técnica
11. ¿Cuentas con conocimientos técnicos para instalar y usar una aplicación de escritorio?
12. ¿Qué tipo de dispositivos utilizas habitualmente (portátil, escritorio, móvil)?

---

## 6. Próximos Pasos

### Inmediatos (Esta semana)
1. ✅ **Completar análisis del proyecto** (HECHO)
2. 🔄 **Verificar procedencia de datos Herlev** - Consultar con equipo clínico
3. ⏳ **Crear plan de desarrollo CITO-22** - Este documento

### Pendientes por priorizar
1. Verificar si `data/raw/im_Dyskeratotic/` puede usarse legalmente
2. Ejecutar baseline DoG sobre conjunto sintético existente
3. Decidir si continuar con ajuste de parámetros o migrar a DL

---

## 7. Referencias

- [Guía maestra de desarrollo](docs/guia-maestra-desarrollo.md)
- [Plan de migración DL](docs/plan-cito95-migracion-dl.md)
- [Inventario Herlev](docs/CITO-100-inventario-herlev.md)
- [Mapa componentes integración](docs/CITO-99-mapa-componentes-integracion.md)
- [Evaluación CITO-85](docs/evidencia-cito85-validacion.md)
- [Calibración CITO-97](docs/evidencia-cito97-calibracion-dog.md)
- [Seguridad y privacidad](docs/seguridad_privacidad.md)