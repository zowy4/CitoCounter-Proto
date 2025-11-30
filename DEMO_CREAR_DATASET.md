# 🧪 Demo: Sistema de Creación de Dataset

Este archivo demuestra cómo usar `crear_dataset.py` para organizar tus imágenes.

## 📋 Simulación de Uso

### **Escenario:**
Tienes 8 imágenes del microscopio con nombres desordenados.

### **Proceso:**

```powershell
# 1. Copiar tus imágenes a la carpeta de importación
# (Coloca aquí tus archivos reales)
cp C:\MisImagenes\*.png mis_imagenes_nuevas\
cp C:\MisImagenes\*.jpg mis_imagenes_nuevas\

# 2. Ejecutar el script de estandarización
python crear_dataset.py

# Output esperado:
# 🔄 Iniciando creación de dataset desde: mis_imagenes_nuevas
# 📸 Encontradas 8 imágenes. Procesando...
#    ✅ IMG_20231105.png -> MUESTRA_001.jpg
#    ✅ foto_cervical.jpg -> MUESTRA_002.jpg
#    ✅ scan_001.tif -> MUESTRA_003.jpg
#    ✅ paciente_A_sample.png -> MUESTRA_004.jpg
#    ✅ DSC_8453.jpg -> MUESTRA_005.jpg
#    ✅ microscope_img_v2.png -> MUESTRA_006.jpg
#    ✅ cervical_001.tif -> MUESTRA_007.jpg
#    ✅ IMG_20231106.png -> MUESTRA_008.jpg
# --------------------------------------------------
# 🎉 Dataset actualizado exitosamente.
# 📁 Imágenes agregadas: 8
# 📍 Ubicación: data/raw
# 📋 Índice: data/dataset_index.csv
```

### **Resultado en `data/raw/`:**

```
data/raw/
├── MUESTRA_001.jpg  (era: IMG_20231105.png)
├── MUESTRA_002.jpg  (era: foto_cervical.jpg)
├── MUESTRA_003.jpg  (era: scan_001.tif)
├── MUESTRA_004.jpg  (era: paciente_A_sample.png)
├── MUESTRA_005.jpg  (era: DSC_8453.jpg)
├── MUESTRA_006.jpg  (era: microscope_img_v2.png)
├── MUESTRA_007.jpg  (era: cervical_001.tif)
└── MUESTRA_008.jpg  (era: IMG_20231106.png)
```

### **Contenido de `data/dataset_index.csv`:**

```csv
ID_Imagen,Nombre_Original,Fecha_Agregado,Resolucion,Etiqueta_Inicial
MUESTRA_001.jpg,IMG_20231105.png,2024-11-30 15:45,1920x1080,Sin Clasificar
MUESTRA_002.jpg,foto_cervical.jpg,2024-11-30 15:45,2560x1440,Sin Clasificar
MUESTRA_003.jpg,scan_001.tif,2024-11-30 15:45,1024x768,Sin Clasificar
MUESTRA_004.jpg,paciente_A_sample.png,2024-11-30 15:45,1280x960,Sin Clasificar
MUESTRA_005.jpg,DSC_8453.jpg,2024-11-30 15:45,3840x2160,Sin Clasificar
MUESTRA_006.jpg,microscope_img_v2.png,2024-11-30 15:45,1600x1200,Sin Clasificar
MUESTRA_007.jpg,cervical_001.tif,2024-11-30 15:45,2048x1536,Sin Clasificar
MUESTRA_008.jpg,IMG_20231106.png,2024-11-30 15:45,1920x1080,Sin Clasificar
```

---

## 🔄 Ejecución Incremental

Si después agregas 3 imágenes más:

```powershell
# Copiar nuevas imágenes
cp C:\NuevasCapturas\*.jpg mis_imagenes_nuevas\

# Ejecutar de nuevo el script
python crear_dataset.py

# Output:
# 🔄 Iniciando creación de dataset desde: mis_imagenes_nuevas
# 📸 Encontradas 3 imágenes. Procesando...
#    ✅ nueva_muestra_1.jpg -> MUESTRA_009.jpg
#    ✅ nueva_muestra_2.jpg -> MUESTRA_010.jpg
#    ✅ nueva_muestra_3.jpg -> MUESTRA_011.jpg
# --------------------------------------------------
# 🎉 Dataset actualizado exitosamente.
# 📁 Imágenes agregadas: 3
```

El script **continúa automáticamente** desde el último número.

---

## ✅ Verificación

```powershell
# Ver imágenes estandarizadas
ls data\raw\

# Ver índice completo
cat data\dataset_index.csv

# Contar total de muestras
(Get-ChildItem data\raw\*.jpg).Count
```

---

## 🚀 Próximos Pasos

Una vez que tengas las imágenes en `data/raw/`, puedes:

### 1. **Análisis Individual (Web App)**
```powershell
streamlit run app.py
```
- Carga `MUESTRA_XXX.jpg`
- Ajusta parámetros σ1 y σ2
- Descarga resultados

### 2. **Análisis en Lote (CLI)**
```powershell
python main.py --input data/raw/ --output data/results/ --sigma1 3.0 --sigma2 5.0
```
- Procesa todas las muestras automáticamente
- Guarda en `bitacora_experimentos.csv`

### 3. **Generar Gráficas para Tesis**
```powershell
python graficar_tesis.py
```
- Lee `bitacora_experimentos.csv`
- Genera visualizaciones de alta calidad (300 DPI)

---

## 📊 Ejemplo de Flujo Completo

```powershell
# 1. Importar imágenes
cp C:\Microscopio\Noviembre\*.tif mis_imagenes_nuevas\
python crear_dataset.py

# 2. Analizar todo el lote
python main.py --input data/raw/ --output data/results/

# 3. Generar visualizaciones
python graficar_tesis.py

# 4. Verificar resultados
cat bitacora_experimentos.csv
ls data\results\graficas_tesis\
```

**Resultado:**
- ✅ Imágenes organizadas: `data/raw/MUESTRA_001.jpg` ... `MUESTRA_N.jpg`
- ✅ Análisis completo: `bitacora_experimentos.csv`
- ✅ Gráficas para tesis: `figura1_riesgo_por_muestra.png`, `figura2_correlacion.png`

---

## 🛠️ Casos de Uso Reales

### **Caso 1: Tesis con 50 imágenes**
```powershell
# Día 1: Importar primer lote (20 imágenes)
python crear_dataset.py
python main.py --input data/raw/

# Semana 2: Agregar 15 imágenes más
python crear_dataset.py  # Continúa desde MUESTRA_021
python main.py --input data/raw/

# Semana 3: Agregar 15 finales
python crear_dataset.py  # Continúa desde MUESTRA_036
python main.py --input data/raw/

# Generar todo el reporte
python graficar_tesis.py
```

### **Caso 2: Proyecto piloto con 10 imágenes**
```powershell
# Todo en un día
python crear_dataset.py
python main.py --input data/raw/ --output data/results/
python graficar_tesis.py

# Revisar en web app
streamlit run app.py
```

---

**Nota:** Este demo no incluye imágenes reales por privacidad. Usa tus propias capturas del microscopio.
