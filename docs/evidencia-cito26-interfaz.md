# CITO-26: Evidencia de interfaz de resultados

**Estado:** Finalizado técnicamente; publicado para revisión del proyecto  
**Interfaz:** [`app.py`](../app.py)  
**Pruebas de componentes de resultados:** [`tests/test_interfaz_resultados.py`](../tests/test_interfaz_resultados.py)

## Criterios cubiertos

- **Conteo y clasificación:** el detalle individual muestra total, normales,
  sospechosas y porcentaje de riesgo; también muestra las células en zona
  frontera cuando existen.
- **Parámetros:** la configuración lateral permite ajustar σ1, σ2, polaridad,
  CLAHE, reducción de ruido, HSV y método de separación. La vista de resultados
  expone los parámetros usados y las reglas activas.
- **Incertidumbre:** se muestra la zona frontera, el margen de clasificación y
  las métricas de calidad de imagen (contraste, brillo, saturación y estado).
- **Advertencia de no diagnóstico:** el aviso experimental aparece en el
  encabezado y en el resumen del análisis; las exportaciones también incluyen
  el aviso.
- **Estados de error:** archivos que exceden 10 MiB, cargas inválidas, dataset
  vacío, imágenes no procesables y fallos individuales del lote se comunican
  con `st.error` o `st.warning` sin presentar un resultado exitoso ficticio.
- **Carga y lote:** el `file_uploader` admite JPG, PNG, JPEG y TIFF, permite
  varias imágenes y presenta progreso, éxitos, fallos y resumen consolidado.

## Evidencia reproducible

```text
python -m unittest tests.test_interfaz_resultados -v
Ran 2 tests ... OK
```

Las pruebas verifican que las exportaciones contienen parámetros, incertidumbre
y advertencia experimental, y que un resultado con detecciones frontera solicita
revisión experta.

La interfaz es experimental. Sus conteos y clasificaciones no constituyen
diagnóstico médico ni sustituyen la revisión de personal experto.
