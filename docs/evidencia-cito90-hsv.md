# CITO-90: Segmentacion OpenCV HSV

La segmentacion HSV esta integrada en `src.preprocessing.segmentar_por_hsv` y
en el CLI mediante `--usar-hsv` y `--metodo-hsv`.

- `saturation`: aisla regiones con saturacion superior al umbral.
- `value`: aisla regiones con brillo superior al umbral.
- La mascara aplica apertura morfologica y dilatacion ligera antes de pasar al
  pipeline DoG.

Las pruebas controladas verifican ambos metodos y el rechazo de un metodo no
soportado:

```text
python -m unittest tests.test_cito90_hsv -q
```

HSV es una tecnica experimental complementaria; requiere calibracion por
conjunto y no constituye validacion clinica.
