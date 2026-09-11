# Evidencia CITO-22: calibración preliminar del filtro DoG

## Ejecución

- **Actividad:** ACT-01
- **Incidencia Jira:** CITO-22
- **Fecha:** 2026-09-10
- **Entrada solicitada:** `data/raw/`
- **Imágenes procesadas:** 9
- **Configuraciones válidas:** 26
- **Evidencia tabular:** `data/calibration/cito22_barrido_dog_raw.csv`
- **Comando:**

```text
python calibrar_dog.py data/raw --sigma1 2.0 2.5 3.0 3.5 4.0 --sigma2 3.0 4.0 5.0 6.0 7.0 8.0 --salida data/calibration/cito22_barrido_dog_raw.csv
```

## Resultado observado

Las configuraciones con menor coeficiente de variación del área detectada
fueron:

| sigma1 | sigma2 | Relación | Imágenes sin detecciones | Detecciones | CV del área |
|---:|---:|---:|---:|---:|---:|
| 3.0 | 4.0 | 1.33 | 5 | 4 | 0.681 |
| 3.5 | 5.0 | 1.43 | 5 | 6 | 0.686 |
| 2.0 | 5.0 | 2.50 | 5 | 6 | 0.819 |

El coeficiente de variación no es una métrica de exactitud. No se selecciona
una configuración como parámetro definitivo con base únicamente en este
resultado.

## Decisión para Jira

**Estado recomendado: En revisión / Bloqueada para cierre.**

La ejecución técnica está realizada, pero CITO-22 no puede marcarse como
`Hecha` porque `data/ground_truth/` no contiene anotaciones expertas y no hay
un conjunto de evaluación separado con el que comparar falsos positivos,
falsos negativos, precisión, sensibilidad o F1. La documentación local de
`data/raw/` tampoco permite verificar por sí sola autorización institucional.

Comentario sugerido para CITO-22:

> Se ejecutó el barrido preliminar CITO-22 el 2026-09-10 sobre 9 imágenes de
> `data/raw/`, con 26 configuraciones sigma. La evidencia está en
> `data/calibration/cito22_barrido_dog_raw.csv`. El cierre queda bloqueado
> hasta incorporar anotaciones expertas autorizadas y separar un conjunto de
> evaluación. No se modificaron los parámetros globales del algoritmo.

## Pendientes para cerrar la actividad

1. Confirmar autorización y procedencia de las imágenes.
2. Incorporar anotaciones expertas para las mismas imágenes o un conjunto
   autorizado equivalente.
3. Separar calibración y evaluación sin reutilizar las imágenes para ajustar
   parámetros.
4. Definir el criterio de selección con el responsable científico.
5. Ejecutar la evaluación y adjuntar métricas a CITO-22.
6. Revisar la evidencia y cambiar Jira a `Hecha` solo después de cumplir los
   criterios de aceptación.
