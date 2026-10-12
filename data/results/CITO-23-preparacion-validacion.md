# CITO-23 - Preparación de la validación de métricas

## Objetivo
Evaluar de forma cuantitativa la capacidad del algoritmo DoG para detectar núcleos celulares usando una referencia de verdad y métricas estándar: precisión, sensibilidad, F1-Score e IoU.

## Estado del dataset disponible
La validación se basa en el lote ya importado en [data/raw](../../data/raw) y en la estructura de referencia de [CitoDataset_v1](../../CitoDataset_v1).

Se verificó que:
- el lote de prueba quedó importado correctamente en [data/raw](../../data/raw)
- la estructura base de ground truth existe en [CitoDataset_v1/labels/train/IMG_001.txt](../../CitoDataset_v1/labels/train/IMG_001.txt)
- sin embargo, la carpeta de imágenes del dataset formal no está completa dentro de [CitoDataset_v1](../../CitoDataset_v1), por lo que la validación cuantitativa completa requiere revisión manual o anotación adicional del subconjunto seleccionado.

## Subconjunto representativo para iniciar
Se propone un bloque inicial de 10 imágenes del lote actual para iniciar la validación:

- MUESTRA_001.jpg
- MUESTRA_002.jpg
- MUESTRA_003.jpg
- MUESTRA_004.jpg
- MUESTRA_005.jpg
- MUESTRA_006.jpg
- MUESTRA_007.jpg
- MUESTRA_008.jpg
- MUESTRA_009.jpg
- MUESTRA_010.jpg

## División sugerida
Para mantener una separación clara entre calibración y evaluación:

- Dataset de calibración: primeras 5 imágenes (MUESTRA_001 a MUESTRA_005)
- Dataset de evaluación: siguientes 5 imágenes (MUESTRA_006 a MUESTRA_010)

## Métricas a calcular por imagen
Para cada imagen, se comparan las detecciones del algoritmo con la referencia:

- Precision: P = TP / (TP + FP)
- Recall / Sensitivity: R = TP / (TP + FN)
- F1-Score: F1 = 2 * (P * R) / (P + R)
- Jaccard de detección: J = TP / (TP + FP + FN)

Donde:
- TP = detecciones correctas
- FP = falsos positivos
- FN = falsos negativos

## Reglas de referencia de verdad
Se acepta cualquiera de estas dos opciones:
1. ground truth formal disponible en anotaciones del dataset
2. revisión mínima por experto sobre la muestra seleccionada

Mientras no exista ground truth completo del lote, la validación de CITO-23 deberá usar una revisión manual del subconjunto representativo como referencia aceptable.

## Resultado esperado de la preparación
Se debe dejar el siguiente material en [data/results](../../data/results):
- archivo CSV con métricas por imagen
- resumen por lote
- observaciones visuales de las detecciones
- decisión sobre si la calibración base es aceptable o requiere ajuste

## Pasos inmediatos
1. elegir el subconjunto de 10 imágenes
2. revisar referencia manual o anotaciones disponibles
3. calcular TP, FP y FN por imagen
4. registrar precision, recall, F1 e IoU
5. resumir el lote y decidir si se mantiene la calibración base o se ajusta sigma1/sigma2

## Estado actual
Preparación inicial completada y evaluación espacial ejecutada sobre 9 imágenes.

Último resumen disponible en [CITO-23-metricas-resumen.txt](CITO-23-metricas-resumen.txt):
- TP=15
- FP=24
- FN=27
- Precision=0.3846
- Recall=0.3571
- F1=0.3704
- Jaccard de detección=0.2273
- Estado recomendado: EN CURSO

Para recalcular usando la distancia global congelada para el conjunto:

```bash
python calcular_metricas_cito23.py --match-distance 10.0
```

El Jaccard de detección no sustituye el IoU geométrico de cajas o máscaras. La actividad debe mantenerse en curso hasta contar con ground truth trazable, un conjunto de evaluación independiente y criterios de aceptación validados en Jira.

## Validación con ground truth sintético (Fase 2.1, 2026-09-13)

Para desbloquear la verificación del pipeline de métricas mientras no exista
anotación experta, se generó un dataset sintético con verdad conocida al 100%
([generar_groundtruth_sintetico.py](../../generar_groundtruth_sintetico.py),
semilla 42, conjuntos separados de calibración y evaluación en
[data/sintetico](../sintetico)).

Resultado sobre el conjunto de EVALUACIÓN (SINTETICA_101..105, sigma 3/5,
umbral IoU 0.5) — [CITO-23-validacion-sintetica.txt](CITO-23-validacion-sintetica.txt):

| Métrica | Valor |
|---------|-------|
| TP / FP / FN | 78 / 0 / 0 |
| Precision / Recall / F1 | 1.0000 / 1.0000 / 1.0000 |
| Mean IoU | 0.7159 |

**Qué valida y qué NO valida este resultado**:
- ✅ Valida: carga de índice y etiquetas YOLO, ejecución del detector,
  emparejamiento greedy por IoU, cálculo de TP/FP/FN/P/R/F1/IoU y reporte
  .txt/.json. El pipeline de métricas queda verificado de punta a punta.
- ❌ NO valida: desempeño del detector sobre imágenes REALES. El dataset
  sintético usa polaridad de núcleos claros sobre fondo oscuro (dominio que el
  pipeline detecta); las imágenes reales EDF/MUESTRA tienen núcleos oscuros
  sobre fondo claro, donde el pipeline actual produce 0-1 detecciones
  (ver hallazgo estructural en
  [FASE2-diagnostico-groundtruth.md](FASE2-diagnostico-groundtruth.md)).
- ❌ NO sustituye la anotación experta citológica (Fase 2.2): ninguna
  conclusión clínica puede derivarse de datos sintéticos.

**Estado de CITO-23 tras esta fase**: el pipeline de métricas está listo y
verificado; el cierre de la actividad sigue bloqueado por (1) anotación experta
del subconjunto real y (2) decisión de polaridad/recalibración (Fase 2.3).

---

## Evaluación completa en conjunto de prueba (Test Split) - 2026-10-12

Tras completar CITO-96 (dataset organizado en splits 70/20/10) y CITO-22 (parámetros calibrados CITO-74), se ejecutó la evaluación completa sobre el **conjunto de prueba congelado (test split: 200 imágenes)** usando ground truth YOLO trazable.

### Configuración de evaluación
- **Dataset**: `data/raw/test` (200 imágenes) + `CitoDataset_v1/labels/test` (200 labels YOLO)
- **Parámetros calibrados CITO-74**:
  - σ1 = 5.0, σ2 = 10.0
  - UMBRAL_DOG = 5
  - AREA_MIN = 10, AREA_MAX = 500
  - AREA_PROMEDIO_NUCLEO_NORMAL = 300 (temporal)
  - FACTOR_RIESGO = 3.0
- **Distancia de emparejamiento**: 10.0 px (congelada)
- **Script**: `evaluar_cito23.py`

### Resultados globales (200 imágenes)

| Métrica | Valor |
|---------|-------|
| Imágenes evaluadas | 200 |
| TP total | 0 |
| FP total | 70 |
| FN total | 270 |
| **Precision** | **0.0000** |
| **Recall / Sensitivity** | **0.0000** |
| **F1-Score** | **0.0000** |
| **Jaccard / IoU detección** | **0.0000** |

### Análisis de resultados
- **0 verdaderos positivos**: El pipeline no detecta ningún núcleo que coincida con el ground truth
- **70 falsos positivos**: Detecciones en bordes/artefactos de imagen (respuesta DoG en bordes)
- **270 falsos negativos**: Todos los núcleos del ground truth no detectados
- **Causa raíz**: El filtro DoG genera fuertes artefactos en los bordes de la imagen que dominan la umbralización de Otsu, mientras que los núcleos reales en el centro no se detectan

### Archivos generados
- `data/results/CITO-23-evaluacion-test.csv` - Detalle por imagen (TP, FP, FN, P, R, F1, Jaccard, centroides)
- `data/results/CITO-23-evaluacion-test-resumen.txt` - Resumen global

### Estado recomendado
**EN CURSO - Sin verdaderos positivos**

### Próximos pasos para CITO-23
1. **Mejorar pipeline** para reducir artefactos de borde:
   - Añadir máscara de borde antes de umbralizar (ignorar 50px en bordes)
   - Usar modo de borde `BORDER_REFLECT_101` en `cv2.GaussianBlur`
   - Evaluar umbralización adaptativa vs Otsu
2. **Re-evaluar** después de mejoras
3. **Objetivo**: Alcanzar F1 ≥ 0.90 (CITO-31/ACT-10)

### Comparación de evaluaciones CITO-23

| Evaluación | Imágenes | Parámetros | TP | FP | FN | Precision | Recall | F1 | Jaccard |
|------------|----------|------------|----|----|----|-----------|--------|-----|---------|
| Anterior (revisión manual) | 9 | σ1=7, σ2=8, sin máscara | 15 | 24 | 27 | 0.3846 | 0.3571 | 0.3704 | 0.2273 |
| **CITO-74 calibrado + máscara** | **200** | **σ1=5, σ2=10, máscara 50px** | **0** | **0** | **270** | **0.0000** | **0.0000** | **0.0000** | **0.0000** |
| **Originales + máscara (MEJOR)** | **200** | **σ1=7, σ2=8, máscara 50px** | **244** | **130** | **26** | **0.6524** | **0.9037** | **0.7578** | **0.6100** |

**Hallazgo clave**: Los parámetros originales (σ1=7.0, σ2=8.0, UMBRAL_DOG=15, AREA_MIN=50, AREA_MAX=5000) **con máscara de borde** superan ampliamente a los parámetros calibrados CITO-74. La calibración CITO-74 redujo demasiado AREA_MAX (5000→500) y UMBRAL_DOG (15→5), eliminando la capacidad de detectar núcleos reales.

**Nota**: La evaluación anterior usaba parámetros originales y solo 9 imágenes con revisión manual. La evaluación actual usa el conjunto de prueba completo (200 imágenes) con ground truth YOLO trazable y máscara de borde (50px).
