# CitoDataset v1.0 📁

**Dataset estructurado para entrenamiento y validación del algoritmo CitoCounter Proto**

---

## 📊 Descripción General

Este dataset contiene imágenes de citologías cervicales con sus correspondientes:
- ✅ **Anotaciones de objetos** (núcleos celulares en formato YOLO)
- ✅ **Metadatos clínicos sintéticos** (para contexto sin comprometer privacidad)
- ✅ **Clasificación de referencia** (Sistema Bethesda)

**Propósito científico:**  
Validar la hipótesis central de la tesis: *"¿Puede un algoritmo DoG + regla del 3x detectar células de riesgo con precisión comparable a un citotecnólogo?"*

---

## 🗂️ Estructura del Dataset

```
CitoDataset_v1/
├── images/
│   ├── train/         # 70% del dataset (entrenamiento)
│   │   └── IMG_001.jpg, IMG_002.jpg, ...
│   └── val/           # 30% del dataset (validación)
│       └── IMG_070.jpg, IMG_071.jpg, ...
├── labels/
│   ├── train/         # Anotaciones en formato YOLO
│   │   └── IMG_001.txt, IMG_002.txt, ...
│   └── val/
│       └── IMG_070.txt, IMG_071.txt, ...
├── metadata/
│   └── clinical_data_synthetic.csv   # Metadatos clínicos
├── classes.txt        # Definición de clases (Normal, Anormal, Artefacto)
└── README.md          # Este archivo
```

---

## 🏷️ Formato de Anotaciones (YOLO)

Cada archivo `.txt` en `labels/` contiene una línea por objeto detectado:

```
<clase> <x_centro> <y_centro> <ancho> <alto>
```

**Ejemplo (IMG_001.txt):**
```
0 0.5234 0.3421 0.0234 0.0312   # Célula normal
0 0.6123 0.4532 0.0198 0.0287   # Célula normal
1 0.3456 0.7890 0.0567 0.0623   # Célula anormal (>3x tamaño)
2 0.8901 0.1234 0.0123 0.0156   # Artefacto (mancha)
```

**Coordenadas normalizadas:**  
- `x_centro`, `y_centro`: Centro del bounding box (0.0 a 1.0)
- `ancho`, `alto`: Dimensiones del bounding box (0.0 a 1.0)

**Clases:**
- `0`: Normal - Núcleo < 3x tamaño promedio
- `1`: Anormal - Núcleo ≥ 3x tamaño promedio (sospechoso)
- `2`: Artefacto - No es una célula (manchas, polvo)

---

## 📋 Metadatos Clínicos

El archivo `metadata/clinical_data_synthetic.csv` contiene:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `ID_Imagen` | Identificador único de la imagen | IMG_001 |
| `ID_Paciente_Sintetico` | ID sintético del paciente (protección de privacidad) | A3F7D9E2 |
| `Fecha_Toma` | Fecha de toma de la muestra | 2024-03-15 |
| `Edad` | Edad del paciente (distribución realista) | 34 |
| `Estado_Hormonal` | Fase del ciclo / condición | Cíclica - Fase folicular |
| `Metodo_Toma` | Técnica de obtención | Base Líquida (ThinPrep) |
| `Calidad_Muestra` | Evaluación de idoneidad | Satisfactoria |
| `Diagnostico_Ref_Bethesda` | Clasificación de referencia (ground truth) | LSIL |
| `VPH_Test` | Resultado de test de VPH | Positivo |
| `Observaciones` | Notas adicionales | (opcional) |

**IMPORTANTE ÉTICO:**  
Todos los metadatos son **sintéticos**. Fueron generados con `generar_datos_sinteticos.py` para cumplir con ética de investigación. Las distribuciones estadísticas son realistas (basadas en literatura), pero los datos individuales son ficticios.

---

## 🔬 Protocolo de Etiquetado

### Herramienta Recomendada: LabelImg

**Instalación:**
```bash
pip install labelImg
```

**Ejecución:**
```bash
labelImg
```

### Flujo de Trabajo:

1. **Abrir directorio de imágenes** (`images/train/` o `images/val/`)
2. **Configurar formato YOLO** (File → Change Save Dir → `labels/train/`)
3. **Cargar `classes.txt`** (View → Auto Save Mode)
4. **Para cada imagen:**
   - Dibujar bounding box alrededor de cada núcleo
   - Asignar clase:
     - **Normal (0)**: Núcleo pequeño, morfología regular
     - **Anormal (1)**: Núcleo grande (≥3x promedio), irregular
     - **Artefacto (2)**: Manchas, superposición, polvo
   - Guardar (`Ctrl+S`)

### Criterios de Calidad:

✅ **Etiquetar TODO núcleo visible** (incluso normales)  
✅ **Bounding box ajustado** (mínimo margen)  
✅ **Sin superposición** de clases diferentes  
✅ **Consistencia**: Si dudas, compara con metadatos (`Diagnostico_Ref_Bethesda`)  

❌ **NO etiquetar** núcleos parciales (en bordes)  
❌ **NO etiquetar** estructuras no nucleares

---

## 📈 División Train/Val

**Criterio:** 70% entrenamiento / 30% validación

**Distribución recomendada:**
- Mantener proporción de diagnósticos en ambos sets
- Ejemplo: Si hay 60% de casos NEGATIVO en total, ambos sets deben tener ~60%

**Script de validación:**
```bash
python validar_consistencia_dataset.py
```

Este script verifica:
- ✓ Que cada `.jpg` en `images/` tenga su `.txt` en `labels/`
- ✓ Que cada `ID_Imagen` en CSV exista como archivo
- ✓ Que las proporciones de clases sean coherentes

---

## 🛠️ Uso del Dataset

### Para Entrenamiento de Modelos (Futuro):
```python
import yaml

# Crear data.yaml para YOLO
config = {
    'train': 'CitoDataset_v1/images/train',
    'val': 'CitoDataset_v1/images/val',
    'nc': 3,  # Número de clases
    'names': ['Normal', 'Anormal', 'Artefacto']
}

with open('data.yaml', 'w') as f:
    yaml.dump(config, f)
```

### Para Validación del Algoritmo Actual:
```python
import pandas as pd

# Cargar metadatos
df = pd.read_csv('CitoDataset_v1/metadata/clinical_data_synthetic.csv')

# Comparar predicciones vs. ground truth
for img_id in df['ID_Imagen']:
    diag_ref = df[df['ID_Imagen'] == img_id]['Diagnostico_Ref_Bethesda'].values[0]
    # Procesar con main.py y comparar
```

---

## 📊 Estadísticas del Dataset

*Actualizar después de completar etiquetado*

- **Total de imágenes:** 100
- **División:**
  - Entrenamiento: 70 imágenes
  - Validación: 30 imágenes
- **Núcleos anotados:**
  - Clase 0 (Normal): ~TBD
  - Clase 1 (Anormal): ~TBD
  - Clase 2 (Artefacto): ~TBD
- **Promedio de núcleos por imagen:** ~TBD
- **Distribución de diagnósticos:**
  - NEGATIVO: 60%
  - LSIL: 20%
  - HSIL: 10%
  - ASC-US: 5%
  - INADECUADA: 5%

---

## ⚖️ Consideraciones Éticas

1. **Privacidad:** Todos los metadatos son sintéticos. No hay información real de pacientes.
2. **Consentimiento:** Las imágenes reales fueron obtenidas con consentimiento informado (expediente de ética).
3. **Anonimización:** Los archivos se nombran como `IMG_XXX` sin identificadores reales.
4. **Uso académico:** Este dataset es exclusivamente para propósitos de investigación.

---

## 🔗 Referencias

- **Sistema Bethesda:** The Bethesda System for Reporting Cervical Cytology (3rd ed., 2015)
- **Formato YOLO:** [Ultralytics YOLO Documentation](https://docs.ultralytics.com/)
- **Regla del 3x:** Rangel et al. (framework teórico del proyecto)

---

## 📝 Changelog

- **v1.0 (2024-01-XX):** Creación inicial del dataset estructurado
- Metadatos sintéticos generados
- Estructura de directorios establecida
- Protocolo de etiquetado documentado

---

## 📧 Contacto

**Autor:** Zowy  
**Proyecto:** CitoCounter Proto - Tesis de Grado  
**GitHub:** https://github.com/zowy4/CitoCounter-Proto

---

## 📄 Licencia

Este dataset se distribuye bajo licencia **MIT** (misma del proyecto). Ver `LICENSE` en raíz del repositorio.

**DISCLAIMER:** Este es un prototipo de investigación. NO usar para diagnóstico clínico real.
