# Dataset e importación de imágenes

## Flujo

```text
mis_imagenes_nuevas/ -> crear_dataset.py -> data/raw/ -> main.py o app.py -> data/results/
```

## Importar imágenes

1. Copia imágenes JPG, JPEG, PNG, TIF, TIFF o BMP a `mis_imagenes_nuevas/`.
2. Ejecuta:

```bash
python crear_dataset.py
```

3. El script valida, convierte a JPG, asigna nombres `MUESTRA_XXX.jpg`, mueve los archivos a `data/raw/` y actualiza `data/dataset_index.csv`.
4. Verifica el dataset:

```bash
python validar_consistencia_dataset.py
```

El proceso es incremental y continúa desde el siguiente número libre.

## Analizar el dataset

```bash
python main.py data/raw --lote --no-gui --sigma1 3.0 --sigma2 5.0
python graficar_tesis.py
```

Para revisar una imagen interactivamente:

```bash
streamlit run app.py
```

## Trazabilidad y privacidad

`data/dataset_index.csv` conserva el nombre original y metadatos de importación. No incluyas nombres de pacientes, EXIF identificable ni imágenes clínicas en Git. Usa datos sintéticos o anonimizados y revisa `.gitignore` antes de cualquier commit.

## Ground truth

Las anotaciones expertas se guardan en `data/ground_truth/` o en la estructura YOLO de `CitoDataset_v1/`. Cada imagen debe tener su anotación correspondiente, un split explícito y un criterio de etiquetado documentado. Consulta la [guía de etiquetado](etiquetado.md).

## Criterios mínimos de calidad

- resolución suficiente para distinguir núcleos;
- formato legible y sin corrupción;
- IDs únicos y estables;
- índice actualizado;
- separación entre calibración y evaluación;
- autorización y anonimización verificadas.

El dataset incluido en `CitoDataset_v1/` es de referencia y sus metadatos clínicos son sintéticos; consulta su [README](../../CitoDataset_v1/README.md).
