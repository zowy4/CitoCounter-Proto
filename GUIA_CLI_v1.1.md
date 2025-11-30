# 🚀 CitoCounter Proto v1.1 - Guía Rápida CLI

## 🎯 ¿Qué cambió en v1.1?

**ANTES (v1.0):** Tenías que editar `main.py` cada vez que querías cambiar una imagen o parámetros.

**AHORA (v1.1):** Todo se controla desde la línea de comandos. ¡Sin editar código!

---

## 📖 Comandos Básicos

### 1. Analizar imagen por defecto
```bash
python main.py
```
Procesa `data/raw/image.png` con parámetros por defecto.

---

### 2. Analizar una imagen específica
```bash
python main.py data/raw/paciente_045.jpg
```

```bash
python main.py CitoDataset_v1/images/train/IMG_001.jpg
```

---

### 3. Experimentar con parámetros DoG
```bash
# Detección más fina (núcleos pequeños)
python main.py --sigma1 2.0 --sigma2 4.0

# Detección más gruesa (núcleos grandes)
python main.py --sigma1 5.0 --sigma2 10.0

# Sin mostrar ventanas (útil para probar rápido)
python main.py --sigma1 2.5 --sigma2 5.5 --no-gui
```

**💡 Tip:** La regla es σ2 ≈ 1.6-2.0 × σ1

---

### 4. Procesar carpeta completa (Modo Lote)
```bash
# Procesar todas las imágenes en data/raw/
python main.py data/raw --lote --no-gui

# Procesar dataset de entrenamiento
python main.py CitoDataset_v1/images/train --lote --no-gui
```

**⚠️ Importante:** Usa `--no-gui` en modo lote para no tener que cerrar 100 ventanas.

---

### 5. Controlar el preprocesamiento
```bash
# Desactivar mejora de contraste (CLAHE)
python main.py --no-contraste

# Activar reducción de ruido extra
python main.py --ruido

# Ambos
python main.py --no-contraste --ruido
```

---

### 6. Registrar en bitácora con ID personalizado
```bash
# El sistema auto-genera T-001, T-002, etc.
python main.py

# O especifica tu propio ID
python main.py --bitacora EXP-CALIBRACION-01
```

---

## 🔬 Ejemplos de Uso Real

### Caso 1: Calibración de Parámetros
Quieres encontrar los mejores valores de sigma para tu microscopio.

```bash
# Prueba 1
python main.py data/raw/calibracion.jpg --sigma1 2.0 --sigma2 4.0 --bitacora CAL-001

# Prueba 2
python main.py data/raw/calibracion.jpg --sigma1 3.0 --sigma2 5.0 --bitacora CAL-002

# Prueba 3
python main.py data/raw/calibracion.jpg --sigma1 4.0 --sigma2 8.0 --bitacora CAL-003
```

Luego compara los resultados en `bitacora_experimentos.csv`.

---

### Caso 2: Validar Algoritmo con Dataset
Procesar todas las imágenes del dataset para generar métricas.

```bash
# Procesar conjunto de entrenamiento
python main.py CitoDataset_v1/images/train --lote --no-gui --bitacora DATASET-TRAIN

# Procesar conjunto de validación
python main.py CitoDataset_v1/images/val --lote --no-gui --bitacora DATASET-VAL
```

---

### Caso 3: Análisis Exploratorio Rápido
Revisar visualmente una imagen con diferentes parámetros.

```bash
# Abrir con ventanas para ver resultado inmediato
python main.py data/raw/muestra_nueva.jpg --sigma1 3.0 --sigma2 5.0

# Si no te gustó el resultado, probar con otros valores
python main.py data/raw/muestra_nueva.jpg --sigma1 2.5 --sigma2 4.5
```

---

## 📊 Ver Ayuda del Sistema

```bash
python main.py --help
```

Muestra todos los argumentos disponibles con descripción.

---

## 🎓 Argumentos Disponibles

| Argumento | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `ruta` | posicional | `data/raw/image.png` | Imagen o carpeta a analizar |
| `--lote` | flag | `False` | Activar modo procesamiento por lotes |
| `--sigma1` | float | `3.0` | Sigma 1 del filtro DoG (desenfoque fino) |
| `--sigma2` | float | `5.0` | Sigma 2 del filtro DoG (desenfoque grueso) |
| `--ruido` | flag | `False` | Activar reducción de ruido (bilateral filter) |
| `--no-contraste` | flag | `False` | Desactivar mejora de contraste CLAHE |
| `--no-gui` | flag | `False` | No mostrar ventanas (headless mode) |
| `--bitacora` | string | auto | ID de prueba para registrar en bitácora |

---

## 💡 Tips y Trucos

### Tip 1: Crear Alias (Atajos)
En PowerShell, puedes crear funciones para comandos frecuentes:

```powershell
# Agregar a tu perfil de PowerShell
function ccproto { python "c:\ruta\CitoCounter_Proto\main.py" $args }

# Ahora puedes usar:
ccproto data/raw/imagen.jpg --sigma1 2.0
```

---

### Tip 2: Procesamiento en Serie
Procesar con múltiples configuraciones:

```powershell
# PowerShell
$sigmas = @((2,4), (3,5), (4,8), (5,10))
foreach ($s in $sigmas) {
    python main.py --sigma1 $s[0] --sigma2 $s[1] --no-gui --bitacora "S1-$($s[0])-S2-$($s[1])"
}
```

---

### Tip 3: Comparar Resultados
Después de procesar con diferentes parámetros:

```bash
python analizar_bitacora.py
```

Esto genera estadísticas comparativas de todas tus pruebas.

---

## 🆚 Comparación v1.0 vs v1.1

### v1.0 (Antiguo)
```python
# Editar main.py cada vez
RUTA_IMAGEN = "data/raw/paciente_045.jpg"
SIGMA1 = 2.0
SIGMA2 = 4.0

# Ejecutar
python main.py
```

### v1.1 (Nuevo)
```bash
# Todo desde la terminal, sin editar
python main.py data/raw/paciente_045.jpg --sigma1 2.0 --sigma2 4.0
```

**Ventajas:**
- ✅ Más rápido (no abrir editor)
- ✅ Más seguro (no modificar código accidentalmente)
- ✅ Más profesional (estándar en bioinformática)
- ✅ Más reproducible (comandos documentables)

---

## 🔄 Migración desde v1.0

Si tenías scripts o documentación con `main.py` v1.0:

**Antes:**
```python
# En main.py
RUTA_IMAGEN = "data/raw/muestra.jpg"
SIGMA1 = 3.0
SIGMA2 = 5.0
```

**Después:**
```bash
python main.py data/raw/muestra.jpg --sigma1 3.0 --sigma2 5.0
```

**Respaldo disponible:** Tu versión anterior está guardada en `main_v1.0_backup.py`

---

## 📈 Resultados

Todos los resultados se guardan en:
- **Imágenes:** `data/results/PANEL_nombrearchivo.png`
- **Bitácora:** `bitacora_experimentos.csv`

---

## 🐛 Troubleshooting

### Problema: "No module named 'argparse'"
**Solución:** `argparse` es parte de la biblioteca estándar de Python 3.2+. Actualiza Python.

### Problema: "FileNotFoundError: [Errno 2] No such file or directory"
**Solución:** Verifica que la ruta sea correcta. Usa comillas si tiene espacios:
```bash
python main.py "ruta con espacios/imagen.jpg"
```

### Problema: Muchas detecciones falsas
**Solución:** Ajusta los parámetros:
- Aumenta `sigma1` y `sigma2` para detectar solo objetos más grandes
- Edita `AREA_MINIMA_NUCLEO` en `src/analysis.py`

---

## 📚 Próximos Pasos

1. **Calibrar con imágenes reales:** Prueba diferentes sigmas y documenta en bitácora
2. **Procesar dataset completo:** Usa modo `--lote` para todas las imágenes
3. **Analizar bitácora:** Ejecuta `python analizar_bitacora.py` para ver tendencias
4. **Validar hipótesis:** Compara tus detecciones con diagnósticos de referencia

---

## 📞 Soporte

Si tienes dudas:
1. Ejecuta `python main.py --help`
2. Revisa `README.md` principal
3. Consulta ejemplos en esta guía

---

**¡Feliz análisis!** 🔬✨

*CitoCounter Proto v1.1 - Noviembre 2024*
