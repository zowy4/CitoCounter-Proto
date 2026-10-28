# Etiquetado YOLO con LabelImg

Esta guía resume el etiquetado de núcleos para `CitoDataset_v1`.

## Instalación y ejecución

```bash
python -m pip install labelImg
labelImg
```

En LabelImg, cambia el formato a YOLO, abre `CitoDataset_v1/images/train/` o `images/val/` y configura como destino `labels/train/` o `labels/val/`.

## Clases

- `0 Normal`: núcleo regular y menor que el umbral de riesgo.
- `1 Anormal`: núcleo que cumple o supera el criterio de referencia de 3x; equivale a sospechoso, no a diagnóstico.
- `2 Artefacto`: polvo, manchas, burbujas o estructuras que no son células.

La definición del umbral debe ser aprobada por personal experto y mantenerse consistente.

## Flujo por imagen

1. Pulsa `W` y dibuja una caja ajustada al núcleo.
2. Selecciona la clase.
3. Guarda con `Ctrl+S`.
4. Avanza con `D`.
5. Repite hasta completar el split.

Atajos útiles: `A` imagen anterior, `Del` eliminar caja, `Ctrl+Z` deshacer.

## Reglas de calidad

- Etiqueta todos los núcleos visibles que entren en el protocolo.
- No etiquetes objetos parciales si el protocolo los excluye.
- No mezcles clases por conveniencia ni etiquetes citoplasma.
- Revisa muestras ambiguas con un segundo experto.
- No uses metadatos clínicos identificables en nombres o anotaciones.

## Verificación

```bash
python validar_consistencia_dataset.py
```

El validador debe comprobar imágenes y etiquetas emparejadas, clases válidas y splits completos. Antes de calcular métricas, separa las imágenes usadas para calibración de las usadas para evaluación.
