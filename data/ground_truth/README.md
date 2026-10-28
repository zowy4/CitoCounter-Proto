# 🎯 Ground Truth - Anotaciones Manuales

Esta carpeta almacena las anotaciones realizadas por expertos (ground truth) para validación científica del algoritmo.

## 📋 Estructura

```
ground_truth/
├── MUESTRA_001_annotated.jpg    # Imagen con marcas visuales
├── MUESTRA_001_cells.csv        # Coordenadas y clasificación de células
└── ...
```

## 🔬 Proceso de Anotación

1. **Selecciona una imagen** de `data/raw/`
2. **Anota manualmente** usando herramientas como:
   - LabelImg (para YOLO format)
   - ImageJ / Fiji
   - CVAT (Computer Vision Annotation Tool)
3. **Guarda aquí** con el mismo nombre base + sufijo `_annotated`

## 📊 Uso en Validación

Las anotaciones en esta carpeta sirven para:

- ✅ **Calcular métricas de precisión** (Precision, Recall, F1-Score)
- 🎯 **Validar detecciones** del algoritmo DoG
- 📈 **Medir error de clasificación** (falsos positivos/negativos)
- 📝 **Documentar para BM5** (Benchmarking científico)

## 🧪 Formato CSV Recomendado

Para archivos `*_cells.csv`:

```csv
Cell_ID,X,Y,Width,Height,Classification,Notes
1,245,380,42,38,Normal,Núcleo bien definido
2,567,421,68,72,Sospechoso,Área 2.5x promedio
```

## 🔗 Integración

Estos datos se usan en:
- `validar_con_groundtruth.py` (script de validación)
- Cálculo de métricas de rendimiento
- Generación de reportes para tesis

---

💡 **Importante:** Las anotaciones deben ser revisadas por personal médico capacitado para garantizar la validez científica.
