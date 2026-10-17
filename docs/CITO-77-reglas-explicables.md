# CITO-24/CITO-77: Documentación de Reglas Explicables, Umbrales, Casos Frontera y Limitaciones

**Proyecto:** CitoCounter-Proto  
**Fecha:** 2026-10-06  
**Dependencia:** J-07 (Calibración CITO-74) y CITO-97 (calibración con imágenes reales)
**Evidencia:** Este documento + casos de prueba en `tests/test_cito77_reglas.py`

> Esta documentación constituye la evidencia técnica de CITO-24. Los umbrales son
> provisionales, dependen de la polaridad y no equivalen a criterios diagnósticos.
> Toda clasificación sospechosa o frontera requiere revisión experta.

---

## 1. Resumen del Pipeline

El pipeline de CitoCounter-Proto procesa imágenes de citología cervical mediante:

1. **Preprocesamiento** (`src/preprocessing.py`): Carga → Gris → Ruido → Contraste → Polaridad → HSV
2. **Filtro DoG** (`src/dog_filter.py`): Diferencia de Gaussiana con σ1, σ2
3. **Análisis** (`src/analysis.py`): Binarización → Contornos → Filtrado → Clasificación (regla 3x)
4. **Visualización** (`src/visualization.py`): Anotación semáforo (verde/rojo)

---

## 2. Variables y Parámetros Calibrados (CITO-74)

### 2.1 Parámetros del Filtro DoG (`src/dog_filter.py`)

| Variable | Valor Calibrado | Descripción | Rango Recomendado |
|----------|----------------|-------------|-------------------|
| `sigma1` | **5.0** | Desenfoque fino (detalles pequeños) | 3.0 – 8.0 |
| `sigma2` | **10.0** | Desenfoque grueso (estructura general) | 8.0 – 16.0 |
| **Relación σ2/σ1** | **2.0** | Ratio típico para DoG | 1.5 – 2.5 |

**Regla de cálculo:** `sigma1 ≈ diámetro/6`, `sigma2 ≈ diámetro/3`  
Para núcleos de ~30px diámetro → σ1=5.0, σ2=10.0 ✓

### 2.2 Parámetros de Umbralización (`src/analysis.py`)

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `UMBRAL_DOG` | **5** | Valor mínimo para considerar píxel como borde (antes de Otsu) |

### 2.3 Parámetros de Clasificación (`src/analysis.py`)

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `AREA_PROMEDIO_NUCLEO_NORMAL` | **300 px²** | Área promedio de referencia (calibrar con datos reales) |
| `FACTOR_RIESGO` | **3.0** | Regla Dra. Rangel: >3x área normal = sospechoso |
| `MARGEN_FRONTERA` | **0.10 (±10%)** | Zona de incertidumbre alrededor del umbral |
| `AREA_MINIMA_NUCLEO` | **10 px²** (claro) / **100 px²** (oscuro) | Filtro ruido/artefactos pequeños |
| `AREA_MAXIMA_NUCLEO` | **1000 px²** (claro) / **300000 px²** (oscuro) | Filtro artefactos grandes |

### 2.4 Parámetros de Preprocesamiento (`src/preprocessing.py`)

| Variable | Valor Default | Descripción |
|----------|---------------|-------------|
| `metodo_contraste` | `'clahe'` | CLAHE (clipLimit=2.0, tileGridSize=8x8) |
| `nivel_ruido` | `'medio'` | Bilateral (d=7, sigmaColor=75, sigmaSpace=75) |
| `polaridad` | `'nucleos-claros'` | Sin inversión; `'nucleos-oscuros'` invierte |
| `usar_hsv` | `False` | Segmentación por color opcional |
| `umbral_hsv` | **100** | Umbral saturación/valor (0-255) |

### 2.5 Parámetros de Separación Watershed (`src/analysis.py`)

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `distancia_minima` | **10 px** | Distancia mínima entre picos locales |
| `metodo` | `'distancia'` | `'distancia'` o `'gradiente'` |

---

## 3. Reglas de Clasificación (Lógica Explícita)

### 3.1 Flujo de Decisión (`clasificar_nucleo_por_area`)

```
┌─────────────────────────────────────────────────────────────┐
│                    CLASIFICACIÓN DE NÚCLEO                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  ÁREA < MÍNIMO  │──No──► ┌─────────────────┐
                    └─────────────────┘        │  ÁREA > MÁXIMO  │──No──► ...
                         │ Sí                  └─────────────────┘
                         ▼                              │ Sí
              ┌─────────────────────┐                   ▼
              │ DESCARTADA: "ruido" │          ┌──────────────────────┐
              └─────────────────────┘          │ DESCARTADA: "artefacto"│
                                               └──────────────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │  ÁREA ≥ UMBRAL SOSPECHOSO│
                    │  (3 × 300 = 900 px²)    │
                    └─────────────────────────┘
                         │           │
                        Sí           No
                         ▼           ▼
              ┌─────────────────┐ ┌─────────────────┐
              │ SOSPECHOSA      │ │ NORMAL          │
              │ (ROJO/RIESGO)   │ │ (VERDE/NORMAL)  │
              └─────────────────┘ └─────────────────┘
                         │           │
                         ▼           ▼
              ┌─────────────────────────────────┐
              │ ¿EN ZONA FRONTERA? (±10% = 810-990)│
              └─────────────────────────────────┘
                         │           │
                        Sí           No
                         ▼           ▼
              ┌─────────────────┐ ┌─────────────────┐
              │ es_frontera=True│ │ es_frontera=False│
              └─────────────────┘ └─────────────────┘
```

### 3.2 Códigos de Clasificación

| Código | Significado | Color Visual | Acción Recomendada |
|--------|-------------|--------------|-------------------|
| `normal` | Área válida < 900 px² o igual al máximo | 🟢 Verde | Seguimiento rutinario |
| `sospechosa` | Área ≥ 900 px² y menor al máximo de su polaridad | 🔴 Rojo | **Revisión experta obligatoria** |
| `descartada` | Área < mínimo o > máximo de su polaridad | ⚪ Gris | Excluir por ruido/artefacto |
| `frontera` | 810 ≤ Área ≤ 990 | 🟡 Amarillo | **Revisión experta prioritaria** |

### 3.3 Mensaje de Revisión Experta (Obligatorio)

> **⚠️ IMPORTANTE - MENSAJE DE REVISIÓN EXPERTA**
> 
> Este sistema es un **prototipo de investigación**, no un dispositivo médico ni sistema de apoyo diagnóstico validado.
> 
> - Las clasificaciones "sospechosa" y "frontera" **requieren revisión por citopatólogo experto**
> - Los resultados NO CONSTITUYE DIAGNÓSTICO MÉDICO
> - Falsos negativos y falsos positivos son posibles
> - La regla del 3x se basa en criterio experto preliminar, no en validación clínica
> - Áreas calibradas con datos sintéticos; requieren validación con ground truth real

---

## 4. Casos Frontera (Edge Cases)

### 4.1 Casos de Área

| Caso | Área (px²) | Clasificación | es_frontera | Comentario |
|------|------------|---------------|-------------|------------|
| Ruido mínimo | 9 | `descartada` | False | < 10, polaridad clara |
| Límite mínimo válido | 10 | `normal` | False | = mínimo, polaridad clara |
| Núcleo mínimo oscuro | 100 | `normal` | False | = mínimo, polaridad oscura |
| Núcleo típico | 300 | `normal` | False | = promedio |
| Frontera inferior | 810 | `normal` | **True** | 900 × 0.9 |
| Umbral exacto | 900 | `sospechosa` | **True** | = 3×300 |
| Frontera superior | 990 | `sospechosa` | **True** | 900 × 1.1 |
| Máximo claro | 1000 | `normal` | False | Límite inclusivo |
| Artefacto claro | 1001 | `descartada` | False | > máximo |

### 4.2 Casos de Polaridad

| Polaridad | Área Mín | Área Máx | Comportamiento |
|-----------|----------|----------|----------------|
| `nucleos-claros` | 10 | 1000 | Núcleos brillantes; valores calibrados provisionalmente |
| `nucleos-oscuros` | 100 | 300000 | Campo claro/Papanicolaou, inversión previa; requiere validación real |

### 4.3 Casos de Separación Watershed

| Escenario | Método | Resultado Esperado |
|-----------|--------|-------------------|
| Núcleos separados | Ninguno | Detección individual correcta |
| Núcleos tocándose | `watershed` | Separación en 2+ núcleos |
| Núcleos superpuestos | `watershed` | Separación parcial (depende de overlap) |
| Clúster denso (>5) | `watershed` | Posible sobre-segmentación |
| Ruido + núcleos | `maximos_locales` | Detección por picos de intensidad |

---

## 5. Limitaciones Conocidas

### 5.1 Limitaciones Algorítmicas

| Limitación | Impacto | Mitigación |
|------------|---------|------------|
| **Regla 3x fija** | No adapta a variabilidad biológica | Calibrar `AREA_PROMEDIO_NUCLEO_NORMAL` por población |
| **DoG sensible a iluminación** | Falsos positivos/negativos en bordes | CLAHE + validación de calidad de imagen |
| **Watershed sobre-segmenta** | Divide núcleos únicos en múltiples | Ajustar `distancia_minima`; validar visualmente |
| **No distingue tipos celulares** | Clasifica todo como "núcleo" | Requiere etapa posterior de clasificación morfológica |
| **Área ≠ malignidad** | Núcleos grandes pueden ser reactivos | Mensaje experta obligatorio; no diagnóstico |

### 5.2 Limitaciones de Datos

| Limitación | Estado Actual | Requerido para Producción |
|------------|---------------|---------------------------|
| Ground truth espacial | ❌ Solo sintético | Anotaciones expertas validadas |
| Validación clínica | ❌ No realizada | Estudio con ≥100 casos reales |
| Variabilidad de tinción | ⚠️ Parcial (polaridad) | Normalización de color (Macenko/Reinhard) |
| Dispositivos de captura | ❌ No probados | Validación multi-cámara/microscopio |

### 5.3 Limitaciones Técnicas

| Componente | Limitación |
|------------|------------|
| `cv2.watershed` | Requiere imagen 8-bit 3-channel; conversión puede perder precisión |
| `cv2.threshold` + Otsu | Asume distribución bimodal; falla en imágenes uniformes |
| CLAHE | `clipLimit=2.0` puede amplificar ruido en imágenes muy oscuras |
| HSV segmentation | Umbral fijo (100) no generaliza a todas las tinciones |

---

## 6. Variables por Módulo (Referencia Rápida)

### `src/dog_filter.py`
```python
def aplicar_filtro_dog(imagen_gris, sigma1=5.0, sigma2=10.0) -> np.uint8
def calcular_sigmas_optimas(diametro_promedio_nucleo) -> (sigma1, sigma2)
```

### `src/preprocessing.py`
```python
def preprocesar_imagen(ruta_imagen,
    mejorar_contraste_flag=True,
    reducir_ruido_flag=False,
    metodo_contraste='clahe',      # 'clahe'|'histogram'|'normalize'|'auto'
    nivel_ruido='medio',           # 'bajo'|'medio'|'alto'
    polaridad='nucleos-claros',    # 'nucleos-claros'|'nucleos-oscuros'
    usar_hsv=False,
    metodo_hsv='saturation',       # 'saturation'|'value'
    umbral_hsv=100) -> (gris, original)
```

### `src/analysis.py`
```python
# Constantes globales
AREA_PROMEDIO_NUCLEO_NORMAL = 300
FACTOR_RIESGO = 3.0
MARGEN_FRONTERA = 0.10
UMBRAL_DOG = 5
AREA_MINIMA_NUCLEO = {'nucleos-claros': 10, 'nucleos-oscuros': 100}
AREA_MAXIMA_NUCLEO = {'nucleos-claros': 1000, 'nucleos-oscuros': 300000}

def obtener_reglas_clasificacion(polaridad) -> dict
def clasificar_nucleo_por_area(area, polaridad) -> dict
def analizar_nucleos(imagen_dog, imagen_original,
    mostrar_debug=False,
    polaridad='nucleos-claros',
    metodo_separacion=None) -> dict  # None|'watershed'|'maximos_locales'
def calibrar_area_promedio(lista_imagenes_normales) -> float
```

---

## 7. Criterios de Aceptación para CITO-77

- [x] Documento de reglas creado (`docs/CITO-77-reglas-explicables.md`)
- [x] Casos de prueba implementados (`tests/test_cito77_reglas.py`)
- [x] Todas las variables y umbrales documentados con valores calibrados
- [x] Casos frontera enumerados con clasificación esperada
- [x] Limitaciones documentadas por categoría
- [x] Mensaje de revisión experta incluido y visible en UI
- [x] Trazabilidad a CITO-74 (parámetros calibrados) y CITO-24 (regla 3x)

---

## 8. Próximos Pasos (Post-CITO-77)

| CITO | Descripción | Dependencia |
|------|-------------|-------------|
| **CITO-78** | API REST versionada | J-07 ✓ |
| **CITO-79** | Validación F1 ≥ 90% | J-08, J-07 |
| **CITO-80** | Casos especiales (superposición, artefactos) | J-06, J-07 |
| **CITO-81** | Dashboard y ETL analítico | J-07 |

---

*Documento generado como evidencia de CITO-77. Para actualizaciones, modificar este archivo y los tests asociados.*