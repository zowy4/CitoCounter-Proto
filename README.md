# CitoCounter Proto 🔬

**Prototipo de investigación para análisis automatizado de células sanguíneas**

Sistema basado en el algoritmo **Diferencia de Gaussiana (DoG)** que implementa la regla de clasificación de la Dra. Rangel: *"Núcleos con área > 3x el tamaño promedio normal son sospechosos"*.

---

## 📋 Descripción del Proyecto

Este software es un prototipo de investigación diseñado para:
- ✅ Detectar núcleos celulares en imágenes de microscopía
- ✅ Clasificar células según su tamaño (Normal vs. Sospechoso)
- ✅ Validar la regla del "3x tamaño del núcleo"
- ✅ Procesar imágenes rápidamente para pruebas de concepto

**NO es un dispositivo médico certificado.** Es una herramienta de investigación para validar hipótesis científicas.

---

## 🏗️ Estructura del Proyecto

```
CitoCounter_Proto/
│
├── data/                      # Datos de entrada/salida
│   ├── raw/                   # Imágenes originales del microscopio
│   ├── ground_truth/          # Imágenes anotadas por expertos (validación)
│   └── results/               # Resultados procesados (imágenes + reportes)
│
├── src/                       # Código fuente
│   ├── __init__.py
│   ├── preprocessing.py       # Conversión a gris, mejora de contraste
│   ├── dog_filter.py          # Algoritmo Diferencia de Gaussiana
│   ├── analysis.py            # Clasificación y regla del 3x
│   └── visualization.py       # Generación de imágenes anotadas
│
├── main.py                    # Ejecutable principal
├── requirements.txt           # Dependencias de Python
└── README.md                  # Este archivo
```

---

## 🚀 Instalación

### Requisitos
- Python 3.8 o superior
- Windows / macOS / Linux

### Paso 1: Clonar o descargar el proyecto
```powershell
cd "C:\Users\zowya\OneDrive\Escritorio\zowy\TALLER 1\Software"
```

### Paso 2: Crear entorno virtual (recomendado)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Paso 3: Instalar dependencias
```powershell
pip install -r requirements.txt
```

---

## 📖 Uso Básico

### PASO 0: Verificar Entorno (Primera vez)
```powershell
python verificar_entorno.py
```
Este script verifica que todo esté instalado correctamente.

### 1. Preparar las Imágenes
Coloca tus imágenes de microscopio en la carpeta `data/raw/`:
```
data/raw/muestra_prueba.jpg
```

**🧪 PRUEBA DE HUMO (Recomendado antes de usar imágenes reales):**
- Descarga una imagen de "Pap smear microscopy" de Google
- Guárdala como `data/raw/muestra_prueba.jpg`
- Ver guía detallada: `docs/GUIA_PRIMER_DISPARO.md`

### 2. Ejecutar el Análisis
```powershell
python main.py
```

### 3. Revisar Resultados
Los resultados se guardan automáticamente en:
- `data/results/` - Imágenes procesadas con timestamp
- `bitacora_experimentos.csv` - Registro automático de parámetros y resultados

**Archivos generados:**
- `resultado_analisis_YYYYMMDD_HHMMSS.png` - Imagen anotada
- `panel_comparativo_YYYYMMDD_HHMMSS.png` - Vista del pipeline completo

### 4. Analizar Experimentos (Después de varias pruebas)
```powershell
python analizar_bitacora.py
```
Genera estadísticas de todos los experimentos para BM5

---

## ⚙️ Calibración del Sistema

### Fase 1: Ajustar Parámetros DoG

Edita `main.py` y modifica las variables según el tamaño de tus núcleos:

```python
SIGMA1 = 3.0  # Ajustar según tamaño de núcleos
SIGMA2 = 5.0  # Debe ser ~1.6x SIGMA1
```

**Regla práctica:**
- Si núcleos miden ~30 píxeles de diámetro → `SIGMA1=5`, `SIGMA2=10`
- Si núcleos miden ~15 píxeles de diámetro → `SIGMA1=2.5`, `SIGMA2=4.0`

### Fase 2: Calibrar Área Promedio Normal

Con imágenes de **células 100% normales** anotadas por la Dra. Rangel:

1. Coloca las imágenes normales en `data/ground_truth/`
2. Ejecuta el script de calibración:

```python
from src.analysis import calibrar_area_promedio
from src.preprocessing import preprocesar_imagen
from src.dog_filter import aplicar_filtro_dog

# Cargar imágenes normales
imagenes_dog = []
for archivo in ["normal1.jpg", "normal2.jpg", "normal3.jpg"]:
    gris, _ = preprocesar_imagen(f"data/ground_truth/{archivo}")
    dog = aplicar_filtro_dog(gris, SIGMA1, SIGMA2)
    imagenes_dog.append(dog)

# Calcular área promedio
area_calibrada = calibrar_area_promedio(imagenes_dog)

# Actualizar en src/analysis.py
print(f"Actualiza AREA_PROMEDIO_NUCLEO_NORMAL = {area_calibrada:.1f}")
```

3. Actualiza el valor en `src/analysis.py`:
```python
AREA_PROMEDIO_NUCLEO_NORMAL = 450.0  # Valor calibrado
```

---

## 🎨 Interpretación de Resultados

### Código de Colores
- 🟢 **VERDE** = Célula Normal (área < 3x promedio)
- 🔴 **ROJO** = Célula Sospechosa (área ≥ 3x promedio)

### Reporte en Consola
```
==============================================================
REPORTE DE ANÁLISIS - CitoCounter Proto
==============================================================
Total de células detectadas: 245
  • Células normales:         230
  • Células sospechosas:      15
  • Porcentaje de riesgo:     6.1%
--------------------------------------------------------------
```

---

## 🧪 Validación Científica

### Métricas Clave a Documentar
1. **Sensibilidad**: % de células sospechosas reales detectadas
2. **Especificidad**: % de células normales correctamente clasificadas
3. **Exactitud**: % de clasificaciones correctas totales

### Protocolo de Validación
1. Seleccionar 50 imágenes con diagnóstico conocido
2. Procesar con CitoCounter Proto
3. Comparar resultados vs. anotaciones de experto
4. Calcular matriz de confusión

### Prueba de Concordancia
```python
# Comparar con anotaciones del experto
from sklearn.metrics import confusion_matrix

y_true = [0, 0, 1, 0, ...]  # Anotaciones de la Dra. Rangel
y_pred = [0, 0, 1, 0, ...]  # Predicciones de CitoCounter

cm = confusion_matrix(y_true, y_pred)
print(cm)
```

---

## 🔧 Solución de Problemas

### Error: "No se encontró la imagen"
- Verifica que el archivo existe en `data/raw/`
- Actualiza la variable `RUTA_IMAGEN` en `main.py`

### Muchos falsos positivos (detecta como sospechosas células normales)
- **Aumenta** `AREA_PROMEDIO_NUCLEO_NORMAL` en `src/analysis.py`
- O ajusta `FACTOR_RIESGO` (ej: de 3.0 a 3.5)

### Muchos falsos negativos (no detecta células sospechosas)
- **Disminuye** `AREA_PROMEDIO_NUCLEO_NORMAL`
- O ajusta `FACTOR_RIESGO` (ej: de 3.0 a 2.5)

### Detecta polvo o ruido como células
- **Aumenta** `AREA_MINIMA_NUCLEO` en `src/analysis.py`
- Activa reducción de ruido: `REDUCIR_RUIDO = True` en `main.py`

### Iluminación irregular
- Activa mejora de contraste: `MEJORAR_CONTRASTE = True` (ya activo por defecto)

---

## 📚 Referencias Científicas

1. **Diferencia de Gaussiana (DoG)**:
   - Marr, D., & Hildreth, E. (1980). "Theory of Edge Detection"
   - Lindeberg, T. (1998). "Feature Detection with Automatic Scale Selection"

2. **Análisis de Imágenes Biomédicas**:
   - Meijering, E. (2012). "Cell Segmentation: 50 Years Down the Road"
   - Carpenter, A. E., et al. (2006). "CellProfiler: Image analysis software"

---

## 👥 Equipo de Investigación

**Proyecto**: Detección Automatizada de Células Anormales en Sangre  
**Institución**: [Tu Universidad/Centro de Investigación]  
**Asesor Científico**: Dra. Rangel (Experta en Hematología)  
**Desarrollo**: Equipo de Software Biomédico  

---

## 📄 Licencia

Este es un prototipo de investigación para uso académico.  
**NO está certificado para uso clínico.**

---

## 🔄 Próximas Versiones

### v0.2 (Planeado)
- [ ] Modo de procesamiento por lotes (múltiples imágenes)
- [ ] Exportación de reportes en formato CSV
- [ ] Interfaz gráfica (GUI) básica

### v0.3 (Futuro)
- [ ] Clasificación multiclase (más de 2 categorías)
- [ ] Integración con microscopios digitales
- [ ] Machine Learning para clasificación avanzada

---

## 📞 Contacto

Para preguntas técnicas o científicas sobre el proyecto:
- Revisar la documentación en el código fuente (`src/*.py`)
- Consultar con el equipo de investigación

---

## 🎯 Recordatorio Importante

Este software es una **herramienta de investigación** para:
✅ Validar hipótesis científicas  
✅ Probar algoritmos de procesamiento de imágenes  
✅ Generar datos para publicaciones  

❌ **NO es un dispositivo médico**  
❌ **NO debe usarse para diagnósticos clínicos**  
❌ **NO reemplaza el criterio de profesionales de la salud**  

---

*Última actualización: Noviembre 2025*
