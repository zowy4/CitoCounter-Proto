# CITO-95: Validacion con dataset congelado

CITO-95 reutiliza la validacion formal de CITO-85 sobre
`data/sintetico/evaluacion`, separado del conjunto de calibracion.

La configuracion congelada fue `sigma1=5.0`, `sigma2=8.0`, apertura final 5 y
`watershed`. Con matching espacial uno a uno e `IoU > 0.50`, el reporte
`CITO-85-validacion-formal.json` registra:

- Precision: 1.0000
- Sensibilidad: 0.8718
- F1: 0.9315
- IoU medio: 0.7308

El criterio F1 >= 0.90 se cumple. Esta evidencia es sintetica y experimental;
no sustituye validacion clinica con anotaciones expertas reales.
