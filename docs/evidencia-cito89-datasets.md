# CITO-89: Fuentes candidatas de datasets

## Candidatos identificados

| Fuente | Uso potencial | Verificacion requerida antes de usar |
|---|---|---|
| Herlev Pap Smear Dataset | Clasificacion de celulas cervicales | Licencia, acceso oficial y compatibilidad de etiquetas |
| SIPaKMeD | Clasificacion de celulas del frotis Pap | Terminos de uso, clases y ausencia de restricciones de redistribucion |
| CERVIX93 | Deteccion y segmentacion de celulas cervicales | Licencia, anotaciones espaciales y separacion train/val/test |

## Decision

No se descarga, incorpora ni publica ningun dataset desde esta actividad. Cada
candidato debe pasar por: licencia compatible, autorizacion documentada,
revision de privacidad, versionado, inventario de anotaciones y un split de
evaluacion separado antes de entrar a `data/`.

Las metricas espaciales (precision, sensibilidad, F1 e IoU) solo se reportaran
cuando el candidato aporte ground truth espacial valido y reproducible.
