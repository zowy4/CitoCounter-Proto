# Evidencia CITO-27 - Dashboard consolidado de resultados

## Objetivo

Integrar el historial de ejecuciones del prototipo en el dashboard local para consultar conteos, clasificaciones y parámetros de varias ejecuciones.

## Implementación

- [src/historial_resultados.py](../src/historial_resultados.py) normaliza la bitácora `bitacora_experimentos.csv`, incluso cuando no tiene encabezado.
- [app.py](../app.py) muestra una sección histórica con ejecuciones, imágenes, células detectadas y promedio experimental.
- La tabla conserva por ejecución imagen, fecha, parámetros DoG, conteo total, normales, sospechosas y porcentaje experimental.
- Los valores agregados no se presentan como métricas clínicas.

## Criterios de aceptación locales

- El lector ignora filas inválidas sin detener el dashboard.
- Las métricas consolidadas coinciden con la suma y promedio de la bitácora.
- La vista histórica aparece antes de cargar una imagen nueva.
- La interfaz mantiene la advertencia de prototipo de investigación.

## Verificación

- Pruebas unitarias: `python -m unittest tests.test_historial_resultados -v`
- Suite completa: `python -m unittest discover -s tests -v`
- Prueba manual: `streamlit run app.py --server.headless true --server.port 8501`

## Estado

Implementación local completada. Pendiente de revisión visual y aceptación en Jira antes de pasar CITO-27 a `Hecha`.