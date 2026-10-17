# CITO-85: Validacion formal de deteccion y segmentacion

**Estado:** En revision - criterio no alcanzado  
**Fecha de ejecucion:** 2026-10-17  
**Conjunto evaluado:** `data/sintetico/evaluacion`  
**Criterio de aceptacion:** F1-Score global >= 0.90

## Protocolo

- Se usaron las cinco imagenes de evaluacion con sus anotaciones YOLO
  correspondientes (78 referencias en total).
- El matching es espacial uno a uno mediante cajas delimitadoras y exige
  `IoU > 0.50`.
- La ejecucion usa `sigma1=3.0`, `sigma2=5.0` y polaridad
  `nucleos-claros`.
- El conjunto no se uso para modificar parametros durante esta actividad.
- La ejecucion genera el reporte de texto, JSON y una grafica comparando
  precision, sensibilidad, F1 e IoU, tanto globales como por imagen.

```text
python validar_metricas_cito23.py ^
  --images-dir data\sintetico\evaluacion\images ^
  --labels-dir data\sintetico\evaluacion\labels ^
  --index data\sintetico\dataset_index.csv ^
  --output-prefix data\results\CITO-85-validacion-formal ^
  --sigma1 3.0 --sigma2 5.0 --polaridad nucleos-claros
```

Los artefactos generados son:

- `data/results/CITO-85-validacion-formal.txt`
- `data/results/CITO-85-validacion-formal.json`
- `data/results/CITO-85-validacion-formal.png`

Los resultados individuales se mantienen fuera del repositorio conforme a la
politica de privacidad; el comando y el formato de los artefactos permiten
reproducirlos localmente.

## Resultados

| Metrica | Resultado | Objetivo | Estado |
|---|---:|---:|---|
| Verdaderos positivos | 54 | - | Informativo |
| Falsos positivos | 7 | - | Informativo |
| Falsos negativos | 24 | - | Informativo |
| Precision | 0.8852 | - | Informativo |
| Sensibilidad | 0.6923 | - | Informativo |
| F1-Score | 0.7770 | >= 0.9000 | No cumple |
| IoU medio | 0.7214 | - | Informativo |

La grafica generada marca el objetivo F1 >= 0.90 con una linea discontinua.
Ningun resultado de la actividad se interpreta como diagnostico clinico.

## Decision

**No cerrar CITO-85.** El F1 global queda 0.1230 por debajo del criterio de
aceptacion. Ajustar el detector utilizando este conjunto invalidaria su papel
como evaluacion separada. Antes de repetir la validacion se requiere calibrar
en un conjunto de desarrollo distinto, congelar configuracion y version de
datos, y volver a ejecutar exactamente el protocolo anterior.

La validacion con imagenes reales sigue bloqueada por la falta de anotaciones
espaciales expertas trazables; los resultados sin esas anotaciones no pueden
usarse para afirmar precision, sensibilidad, F1 o IoU.
