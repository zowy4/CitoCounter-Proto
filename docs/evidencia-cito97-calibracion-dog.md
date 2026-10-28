# CITO-97: Calibracion DoG con conjunto separado

**Estado:** Finalizado tecnicamente

## Separacion de conjuntos

La calibracion usa exclusivamente `data/sintetico/calibracion/images` y sus
etiquetas YOLO. La evaluacion CITO-85 usa exclusivamente
`data/sintetico/evaluacion`; esos directorios no se mezclaron.

## Barrido y decision

Se evaluaron las parejas `(3,5)`, `(3,8)`, `(3,10)`, `(5,8)` y `(5,10)`.
Todas detectaron nuclei en las cinco imagenes de calibracion. La configuracion
seleccionada fue `sigma1=5.0`, `sigma2=8.0`, con `watershed` y apertura final
de 5, porque obtuvo validacion espacial de desarrollo reproducible:

| Metrica | Resultado |
|---|---:|
| TP | 73 |
| FP | 0 |
| FN | 9 |
| Precision | 1.0000 |
| Sensibilidad | 0.8902 |
| F1 | 0.9419 |
| IoU medio | 0.7228 |

## Evidencia reproducible

```text
python calibrar_dog.py data\sintetico\calibracion\images --sigma1 3 5 --sigma2 5 8 10 --salida data\calibration\cito97_barrido_dog_sintetico.csv
python validar_metricas_cito23.py --images-dir data\sintetico\calibracion\images --labels-dir data\sintetico\calibracion\labels --index data\sintetico\dataset_index.csv --output-prefix data\results\CITO-97-calibracion-separada --sigma1 5.0 --sigma2 8.0 --polaridad nucleos-claros --tamano-apertura-final 5 --metodo-separacion watershed
```

Los artefactos numericos son `data/calibration/cito97_barrido_dog_sintetico.csv`
y `data/results/CITO-97-calibracion-separada.{json,txt}`. Las graficas no se
versionan por la politica de resultados.

## Limite de interpretacion

La decision es valida para el conjunto sintetico separado y no constituye
calibracion clinica. La calibracion de imagenes reales requiere anotaciones
espaciales expertas, autorizacion de uso y una evaluacion independiente.
