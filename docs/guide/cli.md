# CLI y procesamiento por lotes

`main.py` permite procesar una imagen o una carpeta sin editar el código. Consulta siempre la ayuda de la versión instalada:

```bash
python main.py --help
```

## Ejemplos

```bash
# Imagen con valores por defecto
python main.py data/raw/muestra.jpg

# Imagen con parámetros DoG y sin ventanas
python main.py data/raw/muestra.jpg --sigma1 2.0 --sigma2 4.0 --no-gui

# Carpeta completa
python main.py data/raw --lote --no-gui

# Ajustar preprocesamiento
python main.py data/raw/muestra.jpg --ruido
python main.py data/raw/muestra.jpg --no-contraste

# Identificador de bitácora personalizado
python main.py data/raw/muestra.jpg --bitacora CAL-001
```

La relación habitual es `sigma2` aproximadamente entre 1.6 y 2 veces `sigma1`, pero debe calibrarse con el dataset.

## Opciones principales

| Opción | Función |
|---|---|
| `ruta` | Imagen o carpeta de entrada |
| `--lote` | Procesa todas las imágenes de una carpeta |
| `--sigma1`, `--sigma2` | Sigmas del filtro DoG |
| `--ruido` | Activa reducción de ruido |
| `--no-contraste` | Desactiva CLAHE |
| `--no-gui` | Evita ventanas gráficas |
| `--bitacora ID` | Usa un identificador de experimento explícito |

## Salidas

Los resultados se escriben en `data/results/` y los experimentos en `bitacora_experimentos.csv`. En modo lote usa `--no-gui` para evitar una ventana por imagen.

## Flujo recomendado

1. Ejecuta una imagen con `--no-gui`.
2. Revisa la bitácora y el resultado.
3. Cambia un solo parámetro.
4. Repite con un ID distinto.
5. Ejecuta `python analizar_bitacora.py` cuando tengas suficientes pruebas.

La sintaxis canónica es la ruta posicional mostrada arriba; no uses opciones `--input` o `--output` salvo que `--help` de tu versión las documente explícitamente.
