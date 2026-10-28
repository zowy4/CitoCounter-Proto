# CITO-27: Evidencia del dashboard de resultados y métricas

**Estado:** Finalizado técnicamente; publicado para revisión del proyecto  
**Interfaz:** [`app.py`](../app.py)  
**Historial:** [`src/historial_resultados.py`](../src/historial_resultados.py)  
**Métricas:** [`src/metricas_sistema.py`](../src/metricas_sistema.py)

## Criterios cubiertos

- El botón **Dashboard** ofrece acceso explícito a la vista principal.
- **Historial** consulta `bitacora_experimentos.csv` y muestra ejecuciones por
  muestra, fecha, imagen, parámetros DoG, total de células, normales,
  sospechosas y riesgo experimental.
- **Métricas** muestra ejecuciones totales, imágenes únicas, promedios,
  porcentaje de riesgo, tasa de riesgo elevado y evolución temporal.
- La vista presenta estado vacío cuando no hay ejecuciones registradas, sin
  inventar resultados.
- El dashboard permite descargar un reporte de métricas reproducible.
- Los indicadores incluyen advertencia visible de que son experimentales y no
  constituyen diagnóstico médico; las muestras sospechosas o fronterizas
  requieren revisión experta.
- El procesamiento en lote mantiene el resumen consolidado por imagen y
  expone los errores individuales sin ocultarlos.

## Evidencia reproducible

```text
python -m unittest tests.test_historial_resultados tests.test_metricas_sistema tests.test_interfaz_resultados -q
Ran 10 tests ... OK
```

Además, `app.py` compila correctamente con `py_compile` y el cambio pasó
`git diff --check`.
