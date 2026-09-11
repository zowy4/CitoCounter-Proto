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
- IoU: IoU = TP / (TP + FP + FN)

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
Preparación inicial completada. Falta la referencia de verdad sobre el subconjunto para producir las métricas definitivas de CITO-23.
