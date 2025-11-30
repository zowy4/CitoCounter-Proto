# 📦 Guía: Creación y Gestión del Dataset

**CitoCounter Proto v1.1** - Sistema de Estandarización de Datos

---

## 🎯 Objetivo

Transformar imágenes desordenadas del microscopio en un dataset científico organizado, reproducible y listo para análisis automatizado.

---

## 📁 Estructura del Dataset

```
CitoCounter_Proto/
│
├── mis_imagenes_nuevas/          # 📥 Bandeja de entrada (temporal)
│   ├── README.md
│   └── [tus imágenes aquí]
│
├── data/
│   ├── raw/                      # 📸 Imágenes estandarizadas
│   │   ├── MUESTRA_001.jpg
│   │   ├── MUESTRA_002.jpg
│   │   └── ...
│   │
│   ├── ground_truth/             # 🎯 Anotaciones manuales
│   │   ├── README.md
│   │   ├── MUESTRA_001_annotated.jpg
│   │   └── MUESTRA_001_cells.csv
│   │
│   ├── results/                  # 📊 Resultados de análisis
│   │   ├── PANEL_*.png
│   │   └── graficas_tesis/
│   │
│   └── dataset_index.csv         # 📋 Catálogo maestro
│
└── crear_dataset.py              # 🛠️ Script de organización
```

---

## 🚀 Proceso Paso a Paso

### **Paso 1: Reunir Imágenes**

Copia todas tus imágenes del microscopio (sin importar nombres o formato) a la carpeta:

```
mis_imagenes_nuevas/
```

**Formatos aceptados:**
- JPG / JPEG
- PNG
- TIF / TIFF
- BMP

**Ejemplo de contenido desordenado:**
```
IMG_20231105_paciente1.png
foto_microscopio_v2.jpg
scan001.tif
DSC_8453.jpg
cervical_sample_A.png
```

---

### **Paso 2: Ejecutar el Script de Estandarización**

Desde la raíz del proyecto:

```powershell
python crear_dataset.py
```

**Lo que hace el script:**

1. ✅ **Verifica integridad** de cada imagen
2. 📝 **Lee metadata** (resolución, formato)
3. 🔄 **Convierte a JPG** estándar (calidad 95%)
4. 📛 **Renombra secuencialmente**:
   - IMG_20231105_paciente1.png → `MUESTRA_001.jpg`
   - foto_microscopio_v2.jpg → `MUESTRA_002.jpg`
   - scan001.tif → `MUESTRA_003.jpg`
5. 📁 **Mueve a** `data/raw/`
6. 📊 **Registra en** `data/dataset_index.csv`

---

### **Paso 3: Verificar el Índice CSV**

Abre `data/dataset_index.csv`:

| ID_Imagen | Nombre_Original | Fecha_Agregado | Resolución | Etiqueta_Inicial |
|-----------|----------------|----------------|------------|------------------|
| MUESTRA_001.jpg | IMG_20231105_paciente1.png | 2024-11-30 15:30 | 1920x1080 | Sin Clasificar |
| MUESTRA_002.jpg | foto_microscopio_v2.jpg | 2024-11-30 15:30 | 2560x1440 | Sin Clasificar |
| MUESTRA_003.jpg | scan001.tif | 2024-11-30 15:30 | 1024x768 | Sin Clasificar |

**Columnas explicadas:**
- **ID_Imagen:** Nombre estandarizado en `data/raw/`
- **Nombre_Original:** Nombre antes de procesar (trazabilidad)
- **Fecha_Agregado:** Timestamp de importación
- **Resolución:** Dimensiones en píxeles
- **Etiqueta_Inicial:** Estado de clasificación (puedes editarlo manualmente)

---

### **Paso 4: Analizar con CitoCounter**

Ahora puedes procesar las imágenes estandarizadas:

#### **Opción A: CLI (Batch Processing)**

```powershell
# Procesar todas las muestras
python main.py --input data/raw/ --output data/results/ --sigma1 3.0 --sigma2 5.0
```

#### **Opción B: Web Dashboard**

```powershell
streamlit run app.py
```

1. Carga una imagen desde `data/raw/MUESTRA_XXX.jpg`
2. Ajusta parámetros con sliders
3. Descarga resultados

---

## 🎯 Gestión de Ground Truth (Opcional)

Para validación científica, necesitas **anotaciones manuales** de un experto.

### **Proceso de Anotación**

1. **Selecciona una muestra** para anotar (ej. `MUESTRA_001.jpg`)

2. **Usa una herramienta de anotación:**
   - **LabelImg** (YOLO format) - Recomendado
   - **ImageJ/Fiji** (análisis científico)
   - **CVAT** (online)

3. **Guarda en** `data/ground_truth/`:
   ```
   MUESTRA_001_annotated.jpg     (imagen marcada visualmente)
   MUESTRA_001_cells.csv         (coordenadas y clasificación)
   ```

### **Formato CSV de Anotaciones**

Archivo: `MUESTRA_001_cells.csv`

```csv
Cell_ID,X,Y,Width,Height,Classification,Notes
1,245,380,42,38,Normal,Núcleo bien definido
2,567,421,68,72,Sospechoso,Área 2.8x promedio
3,123,205,35,34,Normal,Forma regular
```

---

## 📊 Generación de Gráficas para Tesis

Después de procesar varias muestras, genera visualizaciones científicas:

```powershell
python graficar_tesis.py
```

**Output:**
- `data/results/graficas_tesis/figura1_riesgo_por_muestra.png` (300 DPI)
- `data/results/graficas_tesis/figura2_correlacion.png` (300 DPI)

**Uso en documento:**
- BM5 (Validación experimental)
- Sección de Resultados
- Análisis comparativo

---

## 🔄 Agregar Más Imágenes Después

El script es **incremental** - puedes agregar imágenes en cualquier momento:

1. Pon las nuevas fotos en `mis_imagenes_nuevas/`
2. Ejecuta `python crear_dataset.py`
3. El script continúa la numeración: `MUESTRA_010.jpg`, `MUESTRA_011.jpg`, ...

---

## ✅ Checklist de Calidad del Dataset

Antes de considerar tu dataset "listo":

- [ ] Todas las imágenes están en `data/raw/` con nombres estandarizados
- [ ] `dataset_index.csv` tiene todas las entradas
- [ ] Resolución mínima: 500×500 píxeles
- [ ] Formato consistente (JPG)
- [ ] Al menos 5-10 imágenes para pruebas iniciales
- [ ] Al menos 1 imagen con ground truth para validación
- [ ] Nombres originales preservados en el índice (trazabilidad)

---

## 🛠️ Solución de Problemas

### **"❌ La carpeta origen no existe"**

**Solución:** Crea la carpeta `mis_imagenes_nuevas/` en la raíz:

```powershell
mkdir mis_imagenes_nuevas
```

### **"⚠️ No se encontraron imágenes"**

**Verificar:**
1. Las imágenes están en `mis_imagenes_nuevas/` (no en subcarpetas)
2. Tienen extensión válida: `.jpg`, `.png`, `.tif`, etc.

### **"⚠️ Saltando archivo corrupto"**

**Causa:** La imagen está dañada o no es un archivo válido.

**Solución:** Abre la imagen en un visor de imágenes para verificar integridad.

### **Números duplicados**

El script **automáticamente detecta** el siguiente número libre. Si tienes `MUESTRA_001.jpg` y `MUESTRA_002.jpg`, el próximo será `MUESTRA_003.jpg`.

---

## 📝 Ejemplo Completo

### **Situación inicial:**

Tienes 15 fotos del microscopio con nombres aleatorios en tu carpeta de Descargas.

### **Proceso:**

```powershell
# 1. Copiar fotos a la bandeja de entrada
cp C:\Users\zowya\Downloads\*.jpg mis_imagenes_nuevas\

# 2. Ejecutar estandarización
python crear_dataset.py

# 3. Verificar resultados
ls data\raw\

# Output:
# MUESTRA_001.jpg
# MUESTRA_002.jpg
# ...
# MUESTRA_015.jpg

# 4. Analizar todo el lote
python main.py --input data/raw/ --output data/results/

# 5. Generar gráficas
python graficar_tesis.py
```

### **Resultado:**

- ✅ 15 imágenes estandarizadas en `data/raw/`
- ✅ Índice completo en `dataset_index.csv`
- ✅ 15 análisis en `bitacora_experimentos.csv`
- ✅ Gráficas listas para tu tesis

---

## 🔗 Scripts Relacionados

| Script | Propósito | Comando |
|--------|-----------|---------|
| `crear_dataset.py` | Estandarizar imágenes | `python crear_dataset.py` |
| `main.py` | Análisis CLI | `python main.py --input data/raw/` |
| `app.py` | Dashboard web | `streamlit run app.py` |
| `graficar_tesis.py` | Gráficas científicas | `python graficar_tesis.py` |
| `validar_consistencia_dataset.py` | Verificar CitoDataset_v1 | `python validar_consistencia_dataset.py` |

---

## 📚 Referencias

- **YOLO Dataset Format:** Para compatibilidad con LabelImg
- **CSV Standards:** RFC 4180 (para dataset_index.csv)
- **JPEG Quality:** 95% preserva detalles microscópicos sin bloating

---

**Última actualización:** 2024-11-30  
**Versión:** CitoCounter Proto v1.1  
**Autor:** Sistema de Gestión de Dataset Científico
