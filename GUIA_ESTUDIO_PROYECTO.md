# Guía de Estudio Completa - CitoCounter Proto

## 📋 Resumen Ejecutivo

**CitoCounter Proto** es un prototipo de investigación para la detección y clasificación automatizada de núcleos celulares en imágenes de citología cervical. Utiliza el filtro **Difference of Gaussians (DoG)** combinado con una **regla de área de referencia (regla del 3x)** .

> ⚠️ **IMPORTANTE**: Es un **prototipo de investigación**, NO un dispositivo médico ni herramienta de diagnóstico. Los resultados requieren revisión experta.

---

## 🎯 ¿Qué hace el proyecto?

### Función Principal
Detecta y clasifica núcleos celulares en imágenes de citología cervical mediante:
1. **Preprocesamiento** de imagen (CLAHE, reducción de ruido, ajuste de polaridad)
2. **Filtro DoG** (Difference of Gaussians) para resaltar bordes nucleares
3. **Segmentación** mediante umbralización Otsu + detección de contornos
4. **Clasificación** por regla del 3x (área ≥ 3× promedio = sospechoso)
5. **Visualización** y exportación de resultados

### Clasificación
- **Normal (Verde)**: Área < 3× promedio de referencia
- **Sospechosa (Rojo)**: Área ≥ 3× promedio de referencia  
- **Zona Frontera (±10%)**: Requiere revisión experta
- **Descartadas**: Ruido (área < mínimo) o artefactos (área > máximo)

---

## 🛠️ Tecnologías Implementadas

### Stack Tecnológico
| Componente | Tecnología | Versión/Detalle |
|------------|------------|-----------------|
| **Lenguaje** | Python | 3.12+ |
| **Visión por Computadora** | OpenCV | 4.x |
| **Procesamiento Numérico** | NumPy | 1.26+ |
| **Interfaz Web** | Streamlit | 1.28+ |
| **Análisis de Datos** | Pandas | 2.1+ |
| **Testing** | pytest | 9.1+ |
| **Gestión de Entorno** | pip/venv | - |

### Módulos Principales (`src/`)
| Módulo | Función | Archivos Clave |
|--------|---------|----------------|
| **preprocessing.py** | Preprocesamiento de imagen | CLAHE, bilateral filter, HSV, polaridad |
| **dog_filter.py** | Filtro DoG | GaussianBlur, diferencia de Gaussianas |
| **analysis.py** | Análisis y clasificación | Otsu, contornos, regla 3x, Watershed |
| **visualization.py** | Visualización | Paneles, overlays, estadísticas |
| **interfaz_resultados.py** | Exportación/Interfaz | CSV, JSON, avisos |
| **metricas_sistema.py** | Métricas del sistema | Precision, recall, F1, histórico |
| **historial_resultados.py** | Bitácora | CSV logging, agregación |
| **etl_resultados.py** | ETL | Extracción, transformación, carga |
| **metricas_sistema.py** | Métricas de validación | Precision, recall, F1, IoU |

---

## 🔬 Cómo Funciona - Pipeline Completo

### 1. Preprocesamiento (`src/preprocessing.py`)
```
Imagen Original (BGR)
    ↓
Convertir a Grises (cv2.COLOR_BGR2GRAY)
    ↓
[Opcional] Reducir Ruido → Filtro Bilateral (d=7, σColor=75, σSpace=75)
    ↓
[Opcional] Mejorar Contraste → CLAHE (clipLimit=2.0, tileGridSize=8x8)
    ↓
[Opcional] Ajustar Polaridad → Inversión si 'nucleos-oscuros'
    ↓
[Opcional] Segmentación HSV → Máscara por saturación/valor
    ↓
Imagen Procesada (Grises, lista para DoG)
```

**Polaridades soportadas:**
- `nucleos-claros`: Fluorescencia (núcleos claros sobre fondo oscuro)
- `nucleos-oscuros`: Papanicolaou/EDF (núcleos oscuros sobre fondo claro) → Invierte imagen

### 2. Filtro DoG (`src/dog_filter.py`)
```
Imagen Grises
    ↓
Gaussiano 1 (σ1) → Detalles finos
    ↓
Gaussiano 2 (σ2) → Estructura general (σ2 > σ1, típicamente σ2 ≈ 1.6-2.0 × σ1)
    ↓
DoG = G1 - G2 (en float32 para preservar negativos)
    ↓
Normalizar 0-255 (cv2.NORM_MINMAX)
    ↓
Convertir a uint8
```

**Parámetros típicos:**
- `sigma1`: 2.0-8.0 (detalles finos)
- `sigma2`: 4.0-12.0 (estructura general)
- Regla: σ2 ≈ 1.6-2.0 × σ1

### 3. Análisis y Clasificación (`src/analysis.py`)
```
Imagen DoG (uint8)
    ↓
Binarización Otsu (cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ↓
Detección Contornos (cv2.RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
    ↓
[Opcional] Separación Watershed / Máximos Locales
    ↓
Para cada contorno:
    → Calcular área (cv2.contourArea)
    → Filtrar por área mínima/máxima
    → [Opcional] Filtrar circularidad/aspecto (polaridad oscura)
    ↓
Clasificar por Regla del 3x:
    Área ≥ 3× AREA_PROMEDIO_NUCLEO_NORMAL → SOSPECHOSA (Rojo)
    Área < 3× AREA_PROMEDIO_NUCLEO_NORMAL → NORMAL (Verde)
    Zona Frontera: ±10% alrededor del umbral
    ↓
Anotación Visual: Rectángulo + Etiqueta (VERDE/ROJO)
    ↓
Calcular % Riesgo = Sospechosas / Total × 100
```

### Parámetros de Clasificación (Configurables)
| Parámetro | Valor Default | Descripción |
|-----------|---------------|-------------|
| `AREA_PROMEDIO_NUCLEO_NORMAL` | 300 px² | **DEBE CALIBRARSE** con datos reales |
| `FACTOR_RIESGO` | 3.0 | Regla del 3x (Dra. Rangel) |
| `MARGEN_FRONTERA` | 0.10 | ±10% zona frontera |
| `AREA_MINIMA_NUCLEO` | 50/200 px² | Ruido (claro/oscuro) |
| `AREA_MAXIMA_NUCLEO` | 5000/300000 px² | Artefactos (claro/oscuro) |
| `UMBRAL_DOG` | 15 | Umbral mínimo para borde |

### Zona Frontera (±10%)
- **Límite inferior**: umbral × 0.9
- **Límite superior**: umbral × 1.1
- Las células en esta zona requieren revisión experta

---

## 🖥️ Interfaz Streamlit (`app.py`) - Secciones y Funciones

### Header
- Título: "CitoCounter Proto - Panel de Control Interactivo"
- Aviso experimental prominente (⚠️)

### Sidebar - Controles (5 secciones)

#### 1. 📂 Fuente de Imágenes
- **Upload**: Subir 1+ archivos (JPG, PNG, TIF, TIFF, BMP) - máx 10MB
- **Dataset**: Usar imágenes de `data/raw/` (train/val/test)

#### 2. 1️⃣ Parámetros DoG
- **Sigma 1** (0.5-10.0, default 7.0): Detalle fino
- **Sigma 2** (0.5-15.0, default 8.0): Estructura general
- Validación: σ2 > σ1, muestra ratio σ2/σ1

#### 3. 2️⃣ Preprocesamiento
- **Polaridad**: `nucleos-claros` / `nucleos-oscuros`
- **CLAHE**: On/Off + Modo (clahe/auto/histogram/normalize)
- **Reducir Ruido**: On/Off + Nivel (bajo/medio/alto)

#### 4. 3️⃣ Segmentación Avanzada (CITO-33)
- **HSV**: On/Off + Método (saturation/value) + Umbral (0-255)

#### 5. 4️⃣ Separación Núcleos (CITO-32)
- **Método**: none / watershed / maximos_locales

#### 6. 5️⃣ Visualización
- Contornos reales On/Off
- Mostrar áreas On/Off

### Área Principal - Pestañas de Resultados

| Pestaña | Contenido |
|---------|-----------|
| 🎯 **Análisis Final** | Imagen anotada (Verde=Normal, Rojo=Sospechoso), métricas |
| 🔬 **Filtro DoG** | Imagen DoG + componentes G1/G2 (expandible) |
| ⚙️ **Preprocesamiento** | Imagen gris + estado de cada paso |
| 📷 **Original** | Imagen original + dimensiones |
| 🎨 **HSV / Separación** | Máscara HSV + imagen con máscara / Separación Watershed |
| 📋 **Criterios Clasificación** | Reglas activas + tabla por célula (área, clase, frontera, motivo) |

### Métricas Principales (4 columnas)
| Métrica | Descripción |
|---------|-------------|
| **Total Células** | Núcleos detectados totales |
| **Normales** | Área < 3× promedio |
| **Sospechosas** | Área ≥ 3× promedio (delta rojo) |
| **% Riesgo** | Sospechosas/Total × 100 (semáforo: 🟢<5% 🟡5-10% 🔴>10%) |

### Expandibles Adicionales
- ⚠️ **Advertencias Calidad**: Contraste, brillo, saturación
- 📈 **Métricas Calidad**: Contraste, brillo, saturación, estado
- 📊 **Estadísticas Detalladas**: Min/Max/Promedio áreas + gráfico barras + umbral
- 💾 **Descargas**: PNG, CSV, JSON completo

### Expandibles Inferiores
- 📈 **Historial** (CITO-27): Ejecuciones, imágenes, células, % riesgo
- 📊 **Indicadores CITO-28**: Totales, promedios, tasa riesgo alto, evolución

---

## 📊 Métricas de Validación y Porcentaje de Detección

### Estado Actual (Validación Exploratoria)
| Métrica | Valor | Estado |
|---------|-------|--------|
| **Precisión** | ~38% | Exploratoria |
| **Sensibilidad (Recall)** | ~36% | Exploratoria |
| **F1-Score** | ~37% | Exploratoria |
| **IoU** | ~23% | Exploratoria |

> ⚠️ **NOTA**: Estos valores son **exploratorios** basados en 9 imágenes con distancia 10px. **NO son métricas clínicas validadas**. Requieren:
> - Ground truth espacial válido (anotaciones expertas)
> - Dataset congelado separado (train/val/test)
> - Calibración DoG con conjunto autorizado separado (CITO-22)

### Métricas del Sistema (CITO-28)
| Métrica | Descripción |
|---------|-------------|
| **Ejecuciones totales** | Contador de corridas |
| **Imágenes únicas** | Imágenes distintas procesadas |
| **Células promedio** | Promedio de detecciones por imagen |
| **% Riesgo promedio** | Promedio de % sospechosas |
| **Tasa riesgo alto** | % imágenes con >10% riesgo |

### Validez del Porcentaje de Detección
| Aspecto | Estado | Comentario |
|---------|--------|------------|
| **Calibración DoG** | ❌ Pendiente | Requiere CITO-22 con conjunto autorizado |
| **Área promedio** | ❌ No calibrada | Valor 300px² es placeholder |
| **Ground truth** | ⚠️ Parcial | Solo 1 imagen anotada (IMG_001) |
| **Dataset splits** | ✅ Completado | Train/Val/Test 70/20/10 (seed=42) |
| **Métricas clínicas** | ❌ No validadas | Requieren CITO-31 con dataset congelado |

> **Conclusión**: El % de detección actual es **experimental**. No usar para decisiones clínicas.

---

## 🧪 Cómo Probar el Sistema

### 1. Verificación de Entorno
```bash
python -m pip install -r requirements.txt
python verificar_entorno.py
```

### 2. Prueba Rápida CLI (Imagen Única)
```bash
python main.py data/raw/MUESTRA_001.jpg --no-gui
```

### 3. Prueba Lote (Batch) - Dataset Completo
```bash
python main.py data/raw --lote --no-gui --sigma1 3.0 --sigma2 5.0
```

### 4. Interfaz Web Interactiva
```bash
streamlit run app.py
# Abre en http://localhost:8501
```

### 5. Validación de Dataset
```bash
python validar_consistencia_dataset.py
```

### 5. Tests Automatizados
```bash
python -m pytest tests/ -v
# 173 tests pasando
```

### 6. Calibración DoG (CITO-22)
```bash
python calibrar_dog.py data/calibration/images \
  --sigma1 2.0 3.0 4.0 \
  --sigma2 3.0 5.0 6.0 8.0 \
  --salida data/calibration/cito22_barrido_dog.csv
```

### 6. Dashboard Métricas
```bash
python analizar_bitacora.py
```

---

## 📁 Estructura de Directorios Clave

```
CitoCounter-Proto/
├── main.py                    # CLI principal
├── app.py                     # Dashboard Streamlit
├── crear_dataset.py           # Importar/estandarizar imágenes
├── validar_consistencia_dataset.py  # Validar dataset
├── calibrar_dog.py            # Calibración DoG
├── analizar_bitacora.py       # Análisis bitácora
├── requirements.txt           # Dependencias
├── data/
│   ├── raw/                   # Imágenes entrada (train/val/test)
│   ├── results/               # Resultados generados
│   └── ground_truth/          # Ground truth (pendiente)
├── CitoDataset_v1/            # Dataset de referencia
│   ├── images/train/val/test/
│   ├── labels/train/val/test/  # YOLO format
│   └── metadata/
├── src/
│   ├── preprocessing.py       # Preprocesamiento
│   ├── dog_filter.py          # Filtro DoG
│   ├── analysis.py            # Análisis y clasificación
│   ├── visualization.py       # Visualización
│   ├── interfaz_resultados.py # Exportación/Interfaz
│   ├── metricas_sistema.py    # Métricas sistema
│   ├── historial_resultados.py # Bitácora
│   ├── etl_resultados.py      # ETL
│   └── metricas_sistema.py    # Métricas validación
├── tests/                     # 173 tests
└── docs/                      # Documentación
```

---

## ❓ Respuestas a Preguntas Frecuentes

### Sobre el Algoritmo
**P: ¿Cómo detecta los núcleos el sistema?**
R: Usa filtro DoG para resaltar bordes → Binarización Otsu → Detección de contornos externos → Clasificación por área.

**P: ¿Qué es la "Regla del 3x"?**
R: Núcleos con área ≥ 3× el área promedio de referencia se clasifican como "Sospechosos". 

**P: ¿Por qué hay dos polaridades?**
R: `nucleos-claros` (fluorescencia) detecta blobs claros. `nucleos-oscuros` (Papanicolaou/EDF) invierte la imagen para que núcleos oscuros se comporten como blobs claros.

**P: ¿Qué hace el filtro DoG exactamente?**
R: DoG = Gaussiano(σ1) - Gaussiano(σ2). Aproxima Laplaciano de Gaussiana (LoG) pero más rápido. Resalta bordes a escala σ2/σ1.

**P: ¿Qué hace Watershed?**
R: Separa núcleos superpuestos usando transformada de distancia + watershed. Útil para núcleos en contacto.

**P: ¿Qué hace la segmentación HSV?**
R: Usa canal S (saturación) o V (valor) del espacio HSV para crear máscara que resalta núcleos por color, no solo intensidad.

### Sobre Parámetros
**P: ¿Cómo elegir σ1 y σ2?**
R: Regla empírica: σ1 ≈ diámetro_núcleo/6, σ2 ≈ diámetro_núcleo/3. Típicamente σ2 ≈ 1.6-2.0 × σ1. 

**P: ¿Qué es la "Zona Frontera"?**
R: ±10% alrededor del umbral de riesgo (3× promedio). Células en esta zona requieren revisión experta.

**P: ¿Cómo calibrar el área promedio?**
R: Usar `calibrar_area_promedio()` con imágenes de control "100% normales" anotadas por experto. Actualizar `AREA_PROMEDIO_NUCLEO_NORMAL`.

### Sobre Validación
**P: ¿Cuál es la precisión actual?**
R: ~38% precisión, ~36% sensibilidad, ~37% F1 (exploratorio, 9 imágenes). **NO usar clínicamente**.

**P: ¿Cómo validar clínicamente?**
R: Requiere: 1) Calibración DoG (CITO-22), 2) Dataset splits congelados (CITO-70), 3) Ground truth experto, 4) Validación F1≥90% (CITO-31).

**P: ¿Qué es "Ground Truth"?**
R: Anotaciones expertas (formato YOLO) que marcan ubicación, límites y clase de cada núcleo. Requiere doble revisión experta.

### Sobre Uso Clínico
**P: ¿Puede usarse para diagnóstico?**
R: **NO**. Es prototipo experimental. Aviso visible en toda la interfaz: "No equivale a diagnóstico clínico".

**P: ¿Qué significa "% Riesgo"?**
R: % de células clasificadas como sospechosas (área ≥ 3× promedio). **NO es probabilidad de cáncer**.

**P: ¿Qué hacer con falsos positivos/negativos?**
R: Ajustar σ1/σ2, área mínima/máxima, usar Watershed para superposición, HSV para bajo contraste.

---

## 📋 Cuestionario Actualizado para Citólogos

Ver archivo: `CUESTIONARIO_CITOLOGOS.md` (actualizado con secciones para nuevas funcionalidades: HSV, Watershed, métricas calidad, exportación JSON)

### Nuevas Secciones Agregadas:
- **Parte 2.3**: Controles HSV y Watershed
- **Parte 2.4**: Pestañas HSV/Separación y Criterios Clasificación
- **Parte 4.2**: Exportación JSON completa
- **Parte 7.2**: Priorización actualizada con nuevas opciones

---

## 🎬 Guion de Demo para Sesión con Citólogos

Ver archivo: `GUION_DEMO_CITOLOGOS.md` (guion detallado minuto a minuto)

### Resumen del Guion (90 min)

| Fase | Duración | Actividad Clave |
|------|----------|-----------------|
| **1. Bienvenida** | 5 min | Consentimiento, aviso experimental |
| **2. Pre-Sesión** | 5 min | Perfil y expectativas |
| **3. Demo Guiada** | 10 min | Flujo completo con EDF004.png |
| **4. Exploración Libre** | 15 min | Participante prueba controles |
| **5. Validación Clínica** | 25 min | 5-10 casos con ground truth |
| **6. Métricas/Export** | 10 min | Historial, indicadores, exportaciones |
| **7. Feedback** | 15 min | Fortalezas, debilidades, NPS |
| **8. Seguridad/Ética** | 5 min | Privacidad, responsabilidad |
| **9. Cierre** | 5 min | Acciones, firmas |

### Qué Mostrar en Pantalla (Demo Guiada - 10 min)

| Minuto | Pantalla | Qué Decir |
|--------|----------|-----------|
| 0-1 | Header + Sidebar | "Aviso experimental visible. Sidebar con 5 secciones de control" |
| 1-2 | Fuente: Dataset | "2000 imágenes en data/raw, splits train/val/test" |
| 2-3 | Sigma 1/2 | "σ1=detalle fino, σ2=estructura. Ratio 1.6-2x. Validación visual" |
| 3-4 | Polaridad + CLAHE | "Claros=fluorescencia, Oscuros=Papanicolaou. CLAHE auto adapta contraste" |
| 4-5 | HSV + Watershed | "HSV para color, Watershed para superposición. Experimentales" |
| 5-6 | Cargar EDF004.png | "Caso normal, bajo riesgo. Ver pestañas" |
| 6-7 | Pestañas 1-3 | "Análisis Final (Verde/Rojo), DoG (G1/G2), Preprocesamiento" |
| 7-8 | Pestañas 4-6 | "Original, HSV/Separación, Criterios por célula" |
| 8-9 | Métricas + Expandibles | "4 métricas clave, advertencias calidad, estadísticas, descargas" |
| 9-10 | Historial + Indicadores | "Bitácora automática, indicadores CITO-28, evolución temporal" |

### Qué Decir en Validación Clínica (25 min)

1. **Mostrar imagen SIN resultados**: "¿Cuántas células ve? ¿Cuáles sospechosas? % riesgo?"
2. **Mostrar resultado sistema**: Comparar, registrar acuerdo/discrepancia
3. **Si discrepancia**: "¿Qué ve usted que el sistema no ve? ¿Por qué clasificaría diferente? ¿El umbral 3x tiene sentido? ¿Cambiaría σ1/σ2?"

### Preguntas Clave para Feedback
- "¿La regla 3x coincide con su criterio? ¿Qué factor usaría?"
- "¿Zona frontera ±10% apropiada? ¿Cómo maneja casos frontera?"
- "¿Casos problemáticos? Superposición, artefactos, inflamación, metaplasia"
- "¿Qué campos faltan en exportación para su reporte de laboratorio?"
- "NPS 0-10: ¿Recomendaría a colega?"

---

## 📈 Estado del Proyecto y Próximos Pasos

### ✅ Completado
- [x] Pipeline completo (Preprocesamiento → DoG → Análisis → Visualización)
- [x] Interfaz Streamlit v1.1 con todas las funcionalidades
- [x] Dataset splits train/val/test (70/20/10, seed=42)
- [x] Etiquetas YOLO para todos los splits
- [x] CSV metadata limpio (2000 registros)
- [x] Dataset index con columna Split
- [x] Validación consistencia dataset (100% passing)
- [x] Tests: 173/173 passing
- [x] Documentación completa

### ⚠️ Pendiente (Crítico para Validación Clínica)
| Prioridad | Tarea | Jira | Esfuerzo |
|-----------|-------|------|----------|
| **ALTA** | Calibración DoG con conjunto autorizado | CITO-22/97 | 2-3 sem |
| **ALTA** | Validar F1≥90% con dataset congelado | CITO-31/95 | 1-2 sem |
| **ALTA** | Ground truth experto completo | CITO-70 | 2-3 sem |

### 🔮 Próximas Mejoras Técnicas
- Autenticación + Rate Limiting (CITO-92)
- Logs auditoría + HTTPS (CITO-93)
- Casos especiales: superposición, artefactos, iluminación (CITO-94)
- Integración LIS/HL7/FHIR
- Migración a React/Next.js (si se decide)

---

## 📞 Contacto y Recursos

- **Repositorio**: https://github.com/zowy4/CitoCounter-Proto
- **Documentación**: `docs/` (guías, guía maestra, plan proyecto)
- **Issues Jira**: CITO-22 a CITO-97
- **Bitácora**: `bitacora_experimentos.csv`
- **Dataset**: `CitoDataset_v1/` + `data/raw/`

---

*Guía generada: 2026-10-08 | Versión: 1.1 | Proyecto: CitoCounter Proto*