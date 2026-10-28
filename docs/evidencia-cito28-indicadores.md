# CITO-28: Indicadores clave de rendimiento

**Estado:** Finalizado técnicamente; publicado para revisión del proyecto  
**Implementación:** [`src/metricas_sistema.py`](../src/metricas_sistema.py)  
**Consumo:** [`app.py`](../app.py) y [`src/historial_resultados.py`](../src/historial_resultados.py)

## Indicadores por muestra

| Indicador | Fórmula | Fuente |
|---|---|---|
| Células detectadas | `total_celulas` | Resultado de `analizar_nucleos` |
| Células normales | `normales` | Clasificación por área del pipeline |
| Células sospechosas | `sospechosas` | Clasificación por área del pipeline |
| Porcentaje de sospechosas | `sospechosas / max(total_celulas, 1) × 100` | Conteos de la misma ejecución |
| Células frontera | `frontera` | Clasificación cercana al umbral |
| Porcentaje frontera | `frontera / max(total_celulas, 1) × 100` | Conteos de la misma ejecución |
| Porcentaje de riesgo | Valor `porcentaje_riesgo` emitido por el pipeline | Resultado de la ejecución |

Cuando no hay células detectadas, los porcentajes derivados se muestran como
`0.0` y no se produce una división por cero. La frontera es un indicador de
incertidumbre y puede solaparse con la categoría sospechosa; no se suman las
categorías para construir un porcentaje alternativo.

## Indicadores agregados

Para el historial de ejecuciones:

- **Ejecuciones:** cantidad de filas válidas de `bitacora_experimentos.csv`.
- **Imágenes únicas:** cantidad de nombres de muestra distintos.
- **Promedios:** suma del indicador por ejecución dividida entre el número de
  ejecuciones.
- **Riesgo experimental promedio:** media de `porcentaje_riesgo` disponible.
- **Tasa de riesgo elevado:** ejecuciones con `porcentaje_riesgo > 10.0`,
  divididas entre ejecuciones con riesgo disponible.
- **Comparación por muestra:** tabla histórica con fecha, imagen, parámetros DoG,
  conteos y riesgo; la vista de métricas añade evolución temporal.

## Interpretación y límites

Estos KPI describen el comportamiento del prototipo y sirven para comparar
muestras o ejecuciones. No son métricas de precisión, recall, F1 o IoU: esas
métricas requieren ground truth espacial válido y matching reproducible. Los
conteos sospechosos y el porcentaje de riesgo no constituyen diagnóstico y
requieren revisión experta.

## Evidencia reproducible

```text
python -m unittest tests.test_metricas_sistema tests.test_historial_resultados -q
Ran 9 tests ... OK
```
