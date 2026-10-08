# Guía de estudio completa - CitoCounter Proto

## 1. Resumen ejecutivo

CitoCounter Proto es un prototipo de investigación para detectar, segmentar y contar núcleos celulares en imágenes de citología cervical. El sistema combina:

- preprocesamiento de imagen,
- filtro Difference of Gaussians (DoG),
- umbralización y contornos,
- clasificación por área, y
- visualización y reporte de resultados.

El proyecto está pensado para apoyo de investigación y evaluación técnica, no para diagnóstico clínico. El resultado de la herramienta debe revisarse siempre por un citotecnólogo, patólogo o especialista.

> Aviso clave: este proyecto no es un dispositivo médico ni una herramienta certificada para diagnóstico.

---

## 2. ¿Qué hace el proyecto?

El proyecto analiza imágenes de citología cervical y trata de responder dos preguntas:

1. ¿Cuántos núcleos parecen estar presentes?
2. ¿Cuáles tienen una morfología o tamaño que podría considerarse sospechosa?

El flujo principal es:

1. Cargar la imagen.
2. Convertirla a escala de grises.
3. Mejorar contraste y reducir ruido.
4. Aplicar filtro DoG para resaltar estructuras nucleares.
5. Binarizar y detectar contornos.
6. Filtrar artefactos por tamaño y forma.
7. Clasificar cada detección como normal, sospechosa o descartada.
8. Mostrar el resultado con anotaciones y exportarlo.

### Regla de clasificación
La regla actual del proyecto se define en `src/analysis.py`:

- `AREA_PROMEDIO_NUCLEO_NORMAL = 300` px²
- `FACTOR_RIESGO = 3.0`
- `UMBRAL_SOSPECHOSO = 300 * 3 = 900` px²
- `MARGEN_FRONTERA = 0.10` (±10%)

Por tanto:

- Si el área es menor que el mínimo permitido: se descarta como ruido.
- Si el área es mayor que el máximo permitido: se descarta como artefacto.
- Si el área es mayor o igual a 900 px²: se etiqueta como sospechosa.
- Si el área es menor a 900 px²: se etiqueta como normal.
- Si está dentro de ±10% del umbral: se marca como zona frontera y requiere revisión.

La clasificación final se presenta visualmente en verde para normales y rojo para sospechosas.

---

## 3. Cómo se usa

### 3.1 Uso desde línea de comandos

Requisitos:

```bash
python -m pip install -r requirements.txt
python verificar_entorno.py
```

Analizar una imagen individual:

```bash
python main.py data/raw/imagen.jpg --no-gui
```

Procesar una carpeta entera:

```bash
python main.py data/raw --lote --no-gui --sigma1 7.0 --sigma2 8.0
```

Parámetros habituales:

- `--sigma1`: desenfoque fino
- `--sigma2`: desenfoque general, mayor que `sigma1`
- `--ruido`: activar reducción extra de ruido
- `--no-contraste`: desactivar CLAHE
- `--polaridad`: `nucleos-claros` o `nucleos-oscuros`

### 3.2 Uso desde la interfaz web

```bash
streamlit run app.py
```

La app contiene:

- panel lateral con parámetros,
- vista de imagen original,
- vista DoG,
- análisis final,
- métricas de calidad,
- historial y exportación.

### 3.3 Qué hace cada pantalla

La interfaz de Streamlit (`app.py`) incluye secciones para:

- cargar imagen o escoger dataset,
- ajustar sigma 1 y sigma 2,
- activar CLAHE y reducción de ruido,
- cambiar polaridad,
- usar HSV y separación de núcleos,
- revisar resultados por pestaña,
- guardar PNG, CSV y JSON.

---

## 4. Tecnologías implementadas

| Componente | Tecnología | Propósito |
|---|---|---|
| Lenguaje principal | Python | Orquestación del pipeline |
| Visión por computadora | OpenCV | carga, filtros, contornos, umbralización |
| Procesamiento numérico | NumPy | matrices, transformaciones y estadísticas |
| Interfaz web | Streamlit | dashboard visual y exploración interactiva |
| Datos tabulares | Pandas | historial y consolidación de resultados |
| Validación | pytest / unittest | pruebas automatizadas |
| Reproducibilidad | CSV, JSON, bitácora | seguimiento de experimentos |

### Módulos principales

- `main.py`: punto de entrada CLI.
- `app.py`: dashboard web con controls.
- `src/preprocessing.py`: gris, CLAHE, ruido, polaridad e HSV.
- `src/dog_filter.py`: Difference of Gaussians.
- `src/analysis.py`: umbralizado, contornos, filtrado y clasificación.
- `src/visualization.py`: anotaciones y paneles.
- `src/interfaz_resultados.py`: resúmenes y exportación.
- `src/metricas_sistema.py`: indicadores y cálculo de métricas.
- `src/historial_resultados.py`: log de ejecuciones.
- `src/etl_resultados.py`: agregado y exportación.
- `api_v1.py`: API REST experimental.

---

## 5. Cómo funciona el cálculo

### 5.1 Preprocesamiento
El módulo `src/preprocessing.py` hace lo siguiente:

- convierte la imagen a escala de grises,
- mejora el contraste con CLAHE o ecualización,
- puede reducir ruido con filtro bilateral,
- puede invertir la polaridad si la imagen tiene núcleos oscuros sobre fondo claro,
- permite segmentación por HSV para reforzar zonas con intensidad o saturación distinta.

Esto se hace porque los núcleos en citología pueden ser claros o oscuros según la preparación y el tipo de tinción.

### 5.2 Filtro DoG
El módulo `src/dog_filter.py` aplica dos desenfoques Gaussianos y resta sus resultados:

- `G1 = GaussianBlur(imagen, sigma1)`
- `G2 = GaussianBlur(imagen, sigma2)`
- `DoG = G1 - G2`

La parte importante es que la diferencia se conserva en `float32` antes de normalizar y convertir a `uint8` para ser compatible con OpenCV y watershed. Esto ayuda a resaltar estructuras con tamaño parecido al núcleo, y no se destruye la información por recorte prematuro.

### 5.3 Binarización y contornos
En `src/analysis.py` se hace:

- umbralización de Otsu,
- detección de contornos externos,
- cálculo del área con `cv2.contourArea`,
- eliminación por tamaño mínimo/máximo,
- opcionalmente separación con watershed o máximos locales.

Esto produce una lista de objetos candidatos con su área, forma y posición.

### 5.4 Clasificación por área
Cada contorno se evalúa así:

- si `area < area_minima`: descartada por ruido
- si `area > area_maxima`: descartada por artefacto
- si `area >= umbral_sospechoso`: sospechosa
- si `area < umbral_sospechoso`: normal
- si está en ±10% del umbral: frontera

La decisión se registra con motivo explicable: ruido, artefacto, `Área >= umbral de riesgo`, etc.

---

## 6. Para qué sirve cada apartado del sistema

| Apartado | Qué hace | Para qué sirve |
|---|---|---|
| `main.py` | Ejecuta el pipeline completo desde CLI | Permite análisis por terminal y lotes |
| `app.py` | Interfaz Streamlit | Facilita uso visual y demostración para evaluadores |
| `src/preprocessing.py` | Ajusta brillo, contraste y polaridad | Mejora la calidad y prepara la imagen para DoG |
| `src/dog_filter.py` | Calcula la diferencia de Gaussianas | Resalta núcleos según su tamaño |
| `src/analysis.py` | Detecta contornos y clasifica | Decide qué es normal/sospechoso |
| `src/visualization.py` | Dibuja cajas y etiquetas | Muestra resultados en la imagen |
| `src/metricas_sistema.py` | Calcula indicadores | Resumen de rendimiento y comparación |
| `src/historial_resultados.py` | Guarda ejecuciones | Permite seguimiento temporal |
| `src/etl_resultados.py` | Consolida y exporta | Hace análisis por lote y extra exportación |
| `api_v1.py` | Exposición REST | Permite integración con otras apps |
| `validar_consistencia_dataset.py` | Comprueba integridad del dataset | Evita errores en datos de entrada |
| `calcular_metricas_cito23.py` | Calcula TP/FP/FN y precisión/recall/F1 | Evalúa detección con ground truth |

---

## 7. Cómo probar el proyecto

### 7.1 Verificar entorno

```bash
python verificar_entorno.py
```

### 7.2 Ejecutar pruebas unitarias

```bash
python -m unittest discover -s tests -v
```

### 7.3 Validar integridad del dataset

```bash
python validar_consistencia_dataset.py
```

### 7.4 Ejecutar una imagen individual

```bash
python main.py data/raw/imagen.jpg --no-gui --sigma1 7.0 --sigma2 8.0 --polaridad nucleos-oscuros
```

### 7.5 Ejecutar lote

```bash
python main.py data/raw --lote --no-gui --sigma1 7.0 --sigma2 8.0
```

### 7.6 Ejecutar la interfaz web

```bash
streamlit run app.py
```

### 7.7 Calcular métricas exploratorias

```bash
python calcular_metricas_cito23.py
```

Esto ayuda a preparar un resumen con `precision`, `recall`, `f1` y `jaccard_deteccion` cuando existe ground truth o centroides anotados.

---

## 8. ¿Qué porcentaje de detección tiene y qué tan válido es?

El repositorio documenta un estado exploratorio: en la guía y los artefactos del proyecto, se reportan valores aproximados de:

- precisión: ~38%
- recall: ~36%
- F1: ~37%
- IoU: ~23%

Estos valores se describen como exploratorios y no clínicamente validados. El proyecto mismo deja claro que:

- no es una herramienta de diagnóstico,
- requiere ground truth válido,
- necesita un dataset separado para entrenamiento y evaluación,
- debe calibrarse con datos autorizados,
- no se debe usar como decisión médica.

Además, el script `calcular_metricas_cito23.py` calcula métricas reconociendo `TP`, `FP` y `FN` usando emparejamiento espacial, pero la referencia del proyecto recomienda marcos de revisión y validación y no afirma rendimiento clínico.

En otras palabras: el sistema puede ser útil como prototipo de investigación, pero su precisión todavía no está validada para uso clínico.

---

## 9. Preguntas frecuentes (FAQ)

### ¿Es una herramienta diagnóstica?
No. Es un prototipo de investigación para apoyo en detección y conteo de núcleos.

### ¿Cómo decide si una célula es sospechosa?
Por el área total del contorno. Si el área supera un umbral determinado por el promedio normal multiplicado por 3, se marca como sospechosa.

### ¿Qué es la zona frontera?
Es el margen de ±10% alrededor del umbral. Las células en esa zona requieren revisión humana.

### ¿Cómo maneja imágenes con núcleos oscuros?
La polaridad `nucleos-oscuros` invierte la imagen antes del DoG para que los núcleos actúen como blobs claros.

### ¿Qué hace el DoG exactamente?
Resta dos versiones suavizadas de una imagen (con distintos sigmas). Eso resalta estructuras con un tamaño determinado y ayuda a aislar núcleos.

### ¿Cómo se reducen falsos positivos?
Filtrando por tamaño mínimo y máximo, circularidad y relación de aspecto, según el caso y la polaridad.

### ¿Qué pasa si la imagen tiene mucho ruido?
Se puede usar reducción de ruido y CLAHE, o cambiar sigma y polaridad en la app/CLI.

### ¿Se puede usar con varias imágenes a la vez?
Sí, el proyecto incluye modo lote desde `main.py` y la interfaz puede procesar múltiples archivos.

### ¿Cómo se sabe si la imagen es útil o está mala?
La app incluye indicadores de calidad de imagen: contraste, brillo, saturación y advertencias.

### ¿La métrica final del sistema es válida?
No como valor clínico. Solo es una señal exploratoria que requiere revisión y validación con ground truth real.

---

## 10. Conclusión

CitoCounter Proto es un sistema experimental orientado a entender patrones celulares en citología cervical mediante visión por computadora. Su valor real está en:

- ayudar a automatizar la detección preliminar,
- acelerar la revisión visual,
- facilitar comparación de parámetros,
- soportar investigación reproducible,
- documentar reglas explicables de clasificación.

Pero su uso debe mantenerse dentro del marco de investigación, con supervisión profesional y con la clara advertencia de que no sustituye la interpretación clínica.

---

## 11. Documentos recomendados para profundizar

- `README.md`
- `docs/arquitectura_sistema.md`
- `docs/plan-proyecto.md`
- `docs/guia-maestra-desarrollo.md`
- `docs/guide/inicio.md`
- `docs/guide/cli.md`
- `docs/guide/dataset.md`
- `docs/guide/experimentos.md`

Estos documentos son el contexto técnico y normativo del proyecto y ayudan a comprender la intención, el alcance y las limitaciones reales del prototipo.
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