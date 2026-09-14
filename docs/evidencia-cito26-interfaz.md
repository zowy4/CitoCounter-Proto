# Evidencia CITO-26 - Interfaz de conteo y clasificación

## Objetivo

Completar el dashboard local de Streamlit para visualizar detecciones, clasificación, incertidumbre y exportaciones reproducibles del pipeline DoG.

## Entrega

- [app.py](../app.py) mantiene carga local de imágenes, controles DoG, paneles de procesamiento y métricas de conteo.
- Los parámetros iniciales se alinean con la configuración experimental actual: `sigma1=7.0` y `sigma2=8.0`.
- La interfaz muestra una advertencia persistente de uso experimental y el número de detecciones en zona frontera.
- La carga se limita a 10 MiB y el temporal conserva la extensión original antes de procesarse.
- Las exportaciones PNG y CSV incluyen resultados, configuración y aviso de no diagnóstico.
- [src/interfaz_resultados.py](../src/interfaz_resultados.py) concentra la generación de CSV y el mensaje de incertidumbre, con pruebas unitarias en [tests/test_interfaz_resultados.py](../tests/test_interfaz_resultados.py).

## Criterios de aceptación locales

- La interfaz procesa una imagen local compatible sin exponer trazas al usuario.
- Se visualizan total, normales, sospechosas y frontera.
- El CSV conserva parámetros, umbral y advertencia experimental.
- El panel no presenta sus resultados como diagnóstico clínico.

## Estado

Pendiente de prueba manual en Streamlit y de revisión en Jira antes de pasar CITO-26 a `Hecha`.