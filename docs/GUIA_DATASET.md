# 🗂️ Guía de Gestión de Dataset - CitoCounter Proto

Este documento explica el protocolo para agregar nuevas imágenes médicas al sistema garantizando el anonimato y la trazabilidad (BM6).

---

## 🔄 Flujo de Trabajo de Datos

```
┌─────────────────────┐
│  1. RECOLECCIÓN     │  Imágenes crudas del microscopio
│  mis_imagenes_nuevas/│
└──────────┬──────────┘
           │
           │ python crear_dataset.py
           ▼
┌─────────────────────┐
│  2. ESTANDARIZACIÓN │  Renombrado + Sanitización + Indexación
│  crear_dataset.py   │
└──────────┬──────────┘
           │
           │ Movidas a data/raw/
           ▼
┌─────────────────────┐
│  3. PROCESAMIENTO   │  Análisis automatizado
│  main.py / app.py   │
└──────────┬──────────┘
           │
           │ Resultados en data/results/
           ▼
┌─────────────────────┐
│  4. VISUALIZACIÓN   │  Gráficas científicas
│  graficar_tesis.py  │
└─────────────────────┘
```

---

## 🛠️ Herramienta: crear_dataset.py

Este script automatiza la "ingesta" de datos científicos.

### 📋 Características Principales

#### 1️⃣ **Renombrado Secuencial**
Transforma nombres aleatorios en identificadores únicos:

**ANTES:**
```
IMG_20231105_paciente1.png
foto_microscopio_v2.jpg
scan_cervical_001.tif
DSC_8453.jpg
```

**DESPUÉS:**
```
MUESTRA_001.jpg
MUESTRA_002.jpg
MUESTRA_003.jpg
MUESTRA_004.jpg
```

#### 2️⃣ **Sanitización de Metadatos**
- Elimina información EXIF que pueda contener datos personales
- Convierte a formato estándar JPG (calidad 95%)
- Preserva solo información esencial (resolución, fecha de procesamiento)

#### 3️⃣ **Indexación Automática**
Registra cada imagen en `data/dataset_index.csv` con trazabilidad completa.

---

## 📊 Índice Maestro (dataset_index.csv)

Este archivo es la **"fuente de verdad"** del dataset. **NO debe editarse manualmente.**

### Estructura de Columnas

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| **ID_Imagen** | Nombre estandarizado (Clave primaria) | `MUESTRA_001.jpg` |
| **Nombre_Original** | Para trazabilidad interna | `IMG_20231105.png` |
| **Fecha_Agregado** | Timestamp de incorporación | `2024-11-30 15:45` |
| **Resolucion** | Dimensiones en píxeles | `1920x1080` |
| **Etiqueta_Inicial** | Estado de clasificación | `Sin Clasificar` |

### Ejemplo de Contenido

```csv
ID_Imagen,Nombre_Original,Fecha_Agregado,Resolucion,Etiqueta_Inicial
MUESTRA_001.jpg,IMG_20231105_paciente1.png,2024-11-30 15:45,1920x1080,Sin Clasificar
MUESTRA_002.jpg,foto_microscopio_v2.jpg,2024-11-30 15:45,2560x1440,Sin Clasificar
MUESTRA_003.jpg,scan001.tif,2024-11-30 15:45,1024x768,Sin Clasificar
```

---

## 🚀 Uso del Sistema

### **Paso 1: Importar Imágenes**

Crea la carpeta de entrada si no existe:

```powershell
mkdir mis_imagenes_nuevas
```

Copia tus imágenes del microscopio allí (manualmente o con comandos):

```powershell
# Copiar desde una ubicación específica
Copy-Item "C:\MisImagenes\*.jpg" "mis_imagenes_nuevas\"
Copy-Item "C:\MisImagenes\*.png" "mis_imagenes_nuevas\"
```

**Formatos aceptados:**
- JPG / JPEG
- PNG
- TIF / TIFF
- BMP

---

### **Paso 2: Estandarizar (Ejecutar el Script)**

```powershell
python crear_dataset.py
```

**Salida esperada:**

```
🔄 Iniciando creación de dataset desde: mis_imagenes_nuevas
📸 Encontradas 8 imágenes. Procesando...
   ✅ IMG_20231105.png -> MUESTRA_001.jpg
   ✅ foto_cervical.jpg -> MUESTRA_002.jpg
   ✅ scan_001.tif -> MUESTRA_003.jpg
   ✅ paciente_A_sample.png -> MUESTRA_004.jpg
   ✅ DSC_8453.jpg -> MUESTRA_005.jpg
   ✅ microscope_img_v2.png -> MUESTRA_006.jpg
   ✅ cervical_001.tif -> MUESTRA_007.jpg
   ✅ IMG_20231106.png -> MUESTRA_008.jpg
--------------------------------------------------
🎉 Dataset actualizado exitosamente.
📁 Imágenes agregadas: 8
📍 Ubicación: data/raw
📋 Índice: data/dataset_index.csv
```

---

### **Paso 3: Analizar (Procesar el Nuevo Dataset)**

#### **Opción A: CLI (Batch Processing)**

```powershell
# Procesar toda la carpeta data/raw/
python main.py --input data/raw/ --output data/results/ --sigma1 3.0 --sigma2 5.0
```

#### **Opción B: Dashboard Web (Análisis Individual)**

```powershell
streamlit run app.py
```

1. Abre http://localhost:8501
2. Carga una imagen desde `data/raw/MUESTRA_XXX.jpg`
3. Ajusta parámetros con sliders
4. Descarga resultados

---

### **Paso 4: Visualizar (Ver Resultados en Dashboard)**

Después de procesar varias muestras, genera gráficas científicas:

```powershell
python graficar_tesis.py
```

**Archivos generados:**
- `data/results/graficas_tesis/figura1_riesgo_por_muestra.png` (300 DPI)
- `data/results/graficas_tesis/figura2_correlacion.png` (300 DPI)

---

## 🔒 Privacidad y Control de Versiones (Git)

### ⚠️ Configuración de `.gitignore`

El archivo `.gitignore` está configurado para **bloquear la subida de imágenes médicas**:

```gitignore
# NO subir imágenes crudas
mis_imagenes_nuevas/*.jpg
mis_imagenes_nuevas/*.png
mis_imagenes_nuevas/*.tif

# NO subir imágenes estandarizadas
data/raw/*.jpg
data/raw/*.jpeg
data/raw/*.png

# NO subir anotaciones con datos sensibles
data/ground_truth/*.jpg
data/ground_truth/*.png

# SÍ subir metadatos (sin imágenes)
!data/dataset_index.csv
!data/ground_truth/README.md
```

### ✅ Reglas de Oro

1. ✅ **SIEMPRE** subir `dataset_index.csv` (contiene metadatos, no imágenes)
2. ❌ **NUNCA** forzar la subida de archivos `.jpg` a GitHub (`git add -f`)
3. ✅ **SIEMPRE** verificar antes de commit: `git status`
4. ✅ **SIEMPRE** usar nombres estandarizados (MUESTRA_XXX) en publicaciones

---

## 📐 Verificación de Integridad del Dataset

### Script de Validación

```powershell
python validar_consistencia_dataset.py
```

**Chequeos realizados:**
- ✅ Todas las entradas en CSV tienen archivo correspondiente en `data/raw/`
- ✅ Todas las imágenes en `data/raw/` están registradas en CSV
- ✅ No hay IDs duplicados
- ✅ Formatos de archivo correctos
- ✅ Resoluciones válidas (mínimo 500×500 px)

---

## 🔄 Gestión Incremental

El sistema permite agregar imágenes en cualquier momento:

### Ejemplo: Agregar Nuevas Muestras

```powershell
# Semana 1: 10 imágenes
# Resultado: MUESTRA_001 a MUESTRA_010

# Semana 2: 5 imágenes más
# El script detecta automáticamente el último número
# Resultado: MUESTRA_011 a MUESTRA_015

# Semana 3: 8 imágenes más
# Resultado: MUESTRA_016 a MUESTRA_023
```

**No se pierden números ni se sobreescribe nada.**

---

## 📋 Protocolo de Calidad del Dataset

### Checklist antes de Análisis

- [ ] Todas las imágenes en `data/raw/` tienen nombres `MUESTRA_XXX.jpg`
- [ ] `dataset_index.csv` actualizado con todas las entradas
- [ ] Resolución mínima: 500×500 píxeles
- [ ] Formato consistente (JPG)
- [ ] Al menos 5-10 imágenes para pruebas iniciales
- [ ] No hay archivos corruptos (verificado por `crear_dataset.py`)

### Checklist antes de Commit a Git

- [ ] `git status` no muestra archivos `.jpg` en staging
- [ ] `dataset_index.csv` está actualizado
- [ ] Solo se suben scripts y documentación
- [ ] No hay rutas absolutas en el código

---

## 🧪 Casos de Uso Documentados

### **Caso 1: Proyecto de Tesis (50 imágenes)**

```powershell
# Día 1: Primer lote (20 imágenes)
Copy-Item "C:\Capturas\Lote1\*.tif" "mis_imagenes_nuevas\"
python crear_dataset.py
python main.py --input data/raw/

# Semana 2: Segundo lote (15 imágenes)
Copy-Item "C:\Capturas\Lote2\*.jpg" "mis_imagenes_nuevas\"
python crear_dataset.py
python main.py --input data/raw/

# Semana 3: Lote final (15 imágenes)
Copy-Item "C:\Capturas\Lote3\*.png" "mis_imagenes_nuevas\"
python crear_dataset.py
python main.py --input data/raw/

# Generar reporte final
python graficar_tesis.py
```

### **Caso 2: Estudio Piloto (10 imágenes)**

```powershell
# Todo en una sesión
python crear_dataset.py
python main.py --input data/raw/ --output data/results/
python graficar_tesis.py
streamlit run app.py
```

---

## 🛠️ Solución de Problemas Comunes

### ❌ "La carpeta origen no existe"

**Problema:** El script no encuentra `mis_imagenes_nuevas/`

**Solución:**
```powershell
mkdir mis_imagenes_nuevas
```

### ⚠️ "No se encontraron imágenes"

**Causas posibles:**
1. Las imágenes están en subcarpetas (deben estar directamente en `mis_imagenes_nuevas/`)
2. Extensiones no reconocidas

**Verificar:**
```powershell
ls mis_imagenes_nuevas\
```

### ⚠️ "Saltando archivo corrupto"

**Problema:** Imagen dañada o no es un archivo válido

**Solución:**
1. Abrir la imagen en un visor de imágenes
2. Si no abre, descartar el archivo
3. Volver a exportar desde el microscopio

### 🔄 Números duplicados

**No debería ocurrir.** El script detecta automáticamente el siguiente número libre.

**Si ocurre:**
1. Verificar manualmente `data/raw/`
2. Renombrar duplicados manualmente
3. Actualizar `dataset_index.csv`

---

## 📚 Documentación Relacionada

| Archivo | Propósito |
|---------|-----------|
| `GUIA_CLI_v1.1.md` | Uso del CLI con argparse |
| `GUIA_DATASET.md` | Este documento |
| `DEMO_CREAR_DATASET.md` | Ejemplos prácticos |
| `README.md` | Documentación principal del proyecto |
| `RESUMEN_v1.1.md` | Resumen ejecutivo de funcionalidades |

---

## 📞 Soporte

**Para problemas con el dataset:**
1. Revisar este documento
2. Ejecutar `python validar_consistencia_dataset.py`
3. Verificar logs en consola

**Para problemas con análisis:**
- Ver `GUIA_CLI_v1.1.md`
- Consultar `README.md`

---

**Protocolo de Gestión de Datos v1.1**  
**CitoCounter Proto**  
**Última actualización:** Noviembre 2024
