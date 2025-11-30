# 📦 Cómo instalar y usar LabelImg para etiquetar el dataset

## ¿Qué es LabelImg?

**LabelImg** es una herramienta gráfica de anotación de imágenes que permite dibujar **bounding boxes** (cajas delimitadoras) alrededor de objetos y asignarles clases.

Es la herramienta estándar para crear datasets en formato **YOLO** (el que usamos en CitoCounter Proto).

---

## 🛠️ Instalación

### Opción 1: Instalación con pip (Recomendada)

```powershell
pip install labelImg
```

### Opción 2: Si hay problemas con la opción 1

```powershell
pip install labelImg --user
```

### Verificar instalación:

```powershell
labelImg --version
```

---

## 🚀 Cómo ejecutar LabelImg

### Opción A: Desde cualquier terminal

```powershell
labelImg
```

### Opción B: Si el comando no funciona

```powershell
python -m labelImg
```

---

## 📋 Configuración inicial (Solo la primera vez)

### 1. **Cambiar a formato YOLO**
   - Menú: `View` → `Auto Save mode` (activar)
   - Menú: `File` → `Change default saved annotation folder`
   - Seleccionar: `CitoDataset_v1/labels/train/`

### 2. **Cargar clases predefinidas**
   - Menú: `View` → `Auto Save mode` (activar)
   - LabelImg buscará automáticamente `classes.txt` en el directorio

### 3. **Abrir directorio de imágenes**
   - Menú: `File` → `Open Dir`
   - Seleccionar: `CitoDataset_v1/images/train/`

---

## 🖱️ Flujo de trabajo básico

### Paso a paso para etiquetar una imagen:

1. **Abrir imagen:**
   - Click en `Open Dir` → Seleccionar carpeta `images/train/`
   - La primera imagen se carga automáticamente

2. **Dibujar bounding box:**
   - Presionar tecla `W` (o click en botón "Create RectBox")
   - Click y arrastrar sobre el núcleo celular
   - Soltar para crear la caja

3. **Asignar clase:**
   - Aparece un menú emergente
   - Seleccionar la clase apropiada:
     - `Normal` (clase 0): Núcleo pequeño, morfología regular
     - `Anormal` (clase 1): Núcleo grande (≥3x promedio)
     - `Artefacto` (clase 2): Manchas, polvo, no es célula

4. **Guardar:**
   - Presionar `Ctrl+S` (o click en "Save")
   - Se guarda automáticamente en `labels/train/IMG_XXX.txt`

5. **Siguiente imagen:**
   - Presionar `D` (Next Image)
   - Repetir proceso

---

## ⌨️ Atajos de teclado útiles

| Tecla | Acción |
|-------|--------|
| `W` | Crear bounding box |
| `D` | Siguiente imagen |
| `A` | Imagen anterior |
| `Ctrl+S` | Guardar |
| `Del` | Eliminar bounding box seleccionado |
| `Ctrl+Z` | Deshacer |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `↑↓←→` | Mover bounding box |

---

## 📏 Criterios de etiquetado (CitoCounter Proto)

### ✅ **Clase 0: Normal**
- Núcleos de tamaño regular (~área promedio = 300 px²)
- Morfología redondeada u ovalada
- Bordes definidos
- Son la MAYORÍA de células en muestras NEGATIVO

### ✅ **Clase 1: Anormal**
- **Criterio clave:** Núcleo ≥ 3x el tamaño promedio
- Morfología irregular (puede ser hipercromático)
- Estos son los núcleos que el algoritmo DoG debe detectar
- Aparecen en muestras LSIL, HSIL, ASC-US

### ✅ **Clase 2: Artefacto**
- NO es una célula real
- Manchas de sangre
- Superposición de células (no se distinguen núcleos individuales)
- Polvo, burbujas, artefactos de tinción

---

## 🎯 Consejos para etiquetar bien

### DO's (Hacer):
✅ **Etiquetar TODOS los núcleos** (incluso los normales)  
✅ **Ajustar el bounding box** lo más cerca posible del núcleo  
✅ **Ser consistente** en el criterio de clasificación  
✅ **Comparar con el CSV:** Si `IMG_005` tiene `Diagnostico_Ref_Bethesda = HSIL`, debe tener al menos algunas etiquetas de clase 1  
✅ **Tomar descansos:** La fatiga visual causa errores  

### DON'Ts (Evitar):
❌ **NO etiquetar núcleos parciales** (cortados en el borde de la imagen)  
❌ **NO dejar bounding boxes vacíos** (siempre seleccionar clase)  
❌ **NO superponer** bounding boxes de diferentes clases  
❌ **NO etiquetar citoplasma** (solo núcleos)  

---

## 🔄 Flujo completo de etiquetado

```
INICIO
  ↓
1. Instalar LabelImg: pip install labelImg
  ↓
2. Ejecutar: labelImg
  ↓
3. Configurar:
   - Formato YOLO (View → Auto Save)
   - Cargar classes.txt
  ↓
4. Abrir carpeta: images/train/
  ↓
5. Para cada imagen:
   ├─ Dibujar bounding boxes (tecla W)
   ├─ Asignar clase (0, 1, o 2)
   ├─ Guardar (Ctrl+S)
   └─ Siguiente imagen (tecla D)
  ↓
6. Repetir hasta completar 70 imágenes de train
  ↓
7. Cambiar a carpeta: images/val/
  ↓
8. Repetir paso 5 para 30 imágenes de val
  ↓
9. Ejecutar validador:
   python validar_consistencia_dataset.py
  ↓
FIN
```

---

## 📂 Estructura de archivos después de etiquetar

```
CitoDataset_v1/
├── images/
│   ├── train/
│   │   ├── IMG_001.jpg    ← Tu imagen
│   │   ├── IMG_002.jpg
│   │   └── ...
│   └── val/
│       ├── IMG_070.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── IMG_001.txt    ← Generado por LabelImg
│   │   ├── IMG_002.txt
│   │   └── ...
│   └── val/
│       ├── IMG_070.txt
│       └── ...
└── classes.txt            ← Leído por LabelImg
```

---

## 🐛 Problemas comunes y soluciones

### Problema 1: "labelImg no es reconocido como comando"
**Solución:**
```powershell
python -m labelImg
```

O agregar al PATH:
```powershell
$env:PATH += ";$env:USERPROFILE\AppData\Local\Programs\Python\Python312\Scripts"
```

### Problema 2: "No se encuentra PyQt5"
**Solución:**
```powershell
pip install PyQt5
```

### Problema 3: "No aparecen las clases predefinidas"
**Solución:**
- Asegurarse de que `classes.txt` esté en `CitoDataset_v1/`
- O crear manualmente en LabelImg: `View` → `Edit Label`

### Problema 4: "Las etiquetas se guardan en formato XML"
**Solución:**
- Verificar que el formato esté en YOLO: Menú `File` → Debe decir "PascalVOC" (cambiarlo)
- Click en el botón que alterna entre "PascalVOC" y "YOLO"

---

## 📊 Verificar progreso

Después de etiquetar algunas imágenes, ejecutar:

```powershell
python validar_consistencia_dataset.py
```

Este script verifica:
- ✓ Que cada imagen tenga su archivo .txt
- ✓ Que las etiquetas no estén vacías
- ✓ Que haya coherencia entre diagnósticos y clases
- ✓ Estadísticas de objetos etiquetados

---

## 🎓 Recursos adicionales

- **Documentación oficial:** https://github.com/heartexlabs/labelImg
- **Tutorial en video:** Buscar "LabelImg tutorial YOLO format" en YouTube
- **Formato YOLO explicado:** Ver `CitoDataset_v1/README.md` sección "Formato de Anotaciones"

---

## 📝 Checklist de etiquetado completo

- [ ] LabelImg instalado correctamente
- [ ] Formato configurado en YOLO
- [ ] `classes.txt` cargado
- [ ] Directorio `images/train/` abierto
- [ ] Carpeta de guardado `labels/train/` configurada
- [ ] 70 imágenes de train etiquetadas
- [ ] 30 imágenes de val etiquetadas
- [ ] Ejecutado `validar_consistencia_dataset.py` sin errores
- [ ] Revisado CSV para coherencia con diagnósticos

---

## 🚀 Una vez completado el etiquetado

**¡Felicitaciones!** Tu dataset está listo para:

1. **Validar tu algoritmo actual** (main.py)
   - Procesar cada imagen
   - Comparar detecciones vs. ground truth (etiquetas)
   - Calcular métricas: Precisión, Recall, F1-score

2. **Entrenar modelos futuros** (YOLO, Faster R-CNN)
   - Usar `data.yaml` para configuración
   - Entrenar con framework de tu elección

3. **Incluir en tu tesis**
   - Documentar en Capítulo 5: Resultados
   - Tablas de confusion matrix
   - Análisis de rendimiento

---

**¡Éxito en tu etiquetado! 🎯**

*Recuerda: La calidad de las etiquetas determina la calidad del modelo. Tómate tu tiempo.*
