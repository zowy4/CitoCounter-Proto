# CITO-85: Validacion formal de deteccion y segmentacion

**Estado:** Finalizado tecnicamente
**Fecha de ejecucion:** 2026-10-17  
**Conjunto evaluado:** `data/sintetico/evaluacion`  
**Criterio de aceptacion:** F1-Score global >= 0.90

## Protocolo

- La calibracion se realizo exclusivamente con las cinco imagenes de
  `data/sintetico/calibracion`; la mejor configuracion fue congelada antes de
  consultar el conjunto de evaluacion.
- Se usaron las cinco imagenes de evaluacion con sus anotaciones YOLO
  correspondientes (78 referencias en total).
- El matching es espacial uno a uno mediante cajas delimitadoras y exige
  `IoU > 0.50`.
- La ejecucion usa `sigma1=5.0`, `sigma2=8.0`, apertura final de `5`,
  separacion `watershed` y polaridad `nucleos-claros`.
- El conjunto de evaluacion no se uso para modificar parametros durante esta
  actividad.
- La ejecucion genera el reporte de texto, JSON y una grafica comparando
  precision, sensibilidad, F1 e IoU, tanto globales como por imagen.

```text
python validar_metricas_cito23.py ^
  --images-dir data\sintetico\evaluacion\images ^
  --labels-dir data\sintetico\evaluacion\labels ^
  --index data\sintetico\dataset_index.csv ^
  --output-prefix data\results\CITO-85-validacion-formal ^
  --sigma1 5.0 --sigma2 8.0 --polaridad nucleos-claros ^
  --tamano-apertura-final 5 --metodo-separacion watershed
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
| Verdaderos positivos | 68 | - | Informativo |
| Falsos positivos | 0 | - | Informativo |
| Falsos negativos | 10 | - | Informativo |
| Precision | 1.0000 | - | Informativo |
| Sensibilidad | 0.8718 | - | Informativo |
| F1-Score | 0.9315 | >= 0.9000 | Cumple |
| IoU medio | 0.7308 | - | Informativo |

La grafica generada marca el objetivo F1 >= 0.90 con una linea discontinua.
Ningun resultado de la actividad se interpreta como diagnostico clinico.

## Decision

**Criterio CITO-85 cumplido.** El F1 global supera el objetivo en 0.0315 sin
ajustar parametros sobre el conjunto de evaluacion. La configuracion y sus
metricas quedan registradas en el JSON para permitir una repeticion exacta.

La validacion con imagenes reales sigue bloqueada por la falta de anotaciones
espaciales expertas trazables; los resultados sin esas anotaciones no pueden
usarse para afirmar precision, sensibilidad, F1 o IoU.
