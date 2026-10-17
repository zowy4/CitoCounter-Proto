# CITO-91: Procesamiento de muchas imagenes

El CLI por lotes limita de forma predeterminada cada ejecucion a 100 imagenes:

```text
python main.py data\raw --lote --no-gui --max-imagenes 100
```

Los archivos se filtran por extensiones de imagen, se ordenan antes de
procesarse y se ejecutan secuencialmente. La ejecucion secuencial evita
condiciones de carrera al registrar la bitacora y limita el consumo simultaneo
de memoria de OpenCV.

`--max-imagenes` debe ser mayor que cero. Para procesar una coleccion grande,
se recomienda dividirla en lotes reproducibles e identificar cada ejecucion con
`--bitacora`.

Prueba reproducible:

```text
python -m unittest tests.test_cito91_lotes -q
```
