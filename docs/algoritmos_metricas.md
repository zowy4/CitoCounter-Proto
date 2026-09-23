# Cito-35: Documentar Algoritmos, Parámetros y Métricas de Evaluación

## Visión General

Este documento describe los algoritmos implementados, los parámetros configurables y las métricas de evaluación utilizadas en CitoCounter-Proto para la detección y clasificación de núcleos celulares en citología cervical.

## Algoritmos Implementados

### 1. Filtro DoG (Difference of Gaussians)

**Archivo:** `src/dog_filter.py`

**Descripción:**
Aplica un filtro Difference of Gaussians para resaltar regiones con diferentes escalas de luminosidad, útil para la detección de núcleos en imágenes de microscopio.

**Parámetros:**
- `sigma1` (float): Sigma del primer kernel Gaussiano. Controla la detección de estructuras pequeñas.
  - Valor por defecto: 7.0
  - Rango recomendado: 5.0 - 10.0
- `sigma2` (float): Sigma del segundo kernel Gaussiano. Controla la detección de estructuras más grandes.
  - Valor por defecto: 8.0
  - Rango recomendado: 1.6 - 2.0 × sigma1
- `umbral` (int, opcional): Umbral de binarización para la salida del filtro.
  - Utiliza Otsu automáticamente si se establece en 0.

**Función principal:** `aplicar_filtro_dog(imagen_gris, sigma1, sigma2)`

**Relación sigma2/sigma1:**
- La relación aproximadamente entre 1.6 y 2.0 veces sigma1 es un buen punto de partida.
- Debe calibrarse con el dataset específico para obtener mejores resultados.
- Esta relación determina el tamaño máximo de los núcleos que pueden detectarse.

### 2. Binarización Otsu

**Ubicación:** Múltiples archivos (`src/analysis.py`, `src/preprocessing.py`)

**Descripción:**
Aplica el método de umbral de Otsu para convertir la imagen DoG a blanco y negro, donde los núcleos aparecen como regiones blancas sobre fondo negro.

**Parámetros:**
- Ninguno (automático): El umbral se calcula automáticamente usando la desviación estándar y la mediana de la imagen.

**Nota:** Este método es robusto para variaciones de iluminación moderadas pero puede requerir ajustes para imágenes con contraste muy bajo o muy alto.

### 3. Detección de Contornos

**Ubicación:** `src/analysis.py`

**Descripción:**
Detecta contornos externos en la imagen binarizada usando `cv2.RETR_EXTERNAL` y `cv2.CHAIN_APPROX_SIMPLE`.

**Parámetros:**
- Ninguno configurables directamente; se deriva del umbral binario.

**Consideraciones:**
- Solo se detectan contornos externos, ignorando huecos internos en los núcleos.
- El encadenamiento simple comprime segmentos rectos para ahorrar memoria.

### 4. Filtrado de Ruido (Artifact Removal)

**Ubicación:** `src/analysis.py`, sección de filtrado posterior a la detección de contornos

**Descripción:**
Filtra los contornos detectados para eliminar artefactos (polvo, manchas de tinción, estructuras no celulares) basándose en:

**Parámetros de filtrado:**

| Parámetro | Descripción | Umbral por defecto | Justificación |
|-----------|-------------|-------------------|---------------|
| `area_minima` | Área mínima para considerar un contorno como núcleo | `AREA_MINIMA_NUCLEO[polaridad] * 0.1` | Elimina ruido muy pequeño |
| `area_maxima` | Área máxima para considerar un contorno como núcleo | `AREA_MAXIMA_NUCLEO[polaridad] * 5` | Elimina manchas de tinción grandes |
| `circularidad_min` | Circularidad mínima (4π·área/perímetro²) | 0.3 | Elimina formas irregulares (ruido) |
| `aspecto_maximo` | Relación ancho/alto máxima | 3.0 | Elimina formas muy alargadas |

**Cálculo de circularidad:**
```
circularidad = 4 · π · área / perímetro²
```
- Valor 1.0: círculo perfecto
- Valor < 0.3: forma muy irregular (probablemente ruido)
- Valor > 0.7: forma relativamente redondeada

### 5. Clasificación por Área

**Ubicación:** `src/analysis.py`, función `clasificar_nucleo_por_area()`

**Descripción:**
Clasifica cada núcleo detectado como normal o sospechoso basándose en su área en relación con el umbral de riesgo.

**Parámetros:**
- `area` (float): Área del núcleo detectado
- `polaridad` (str): 'nucleos-claros' o 'nucleos-oscuros'

**Umbrales de clasificación:**
- `area_minima_nucleo`: Área mínima analizable para la polaridad especificada
- `area_maxima_nucleo`: Área máxima analizable para la polaridad especificada
- `umbral_sospechoso = AREA_PROMEDIO_NUCLEO_NORMAL · FACTOR_RIESGO`
- `MARGEN_FRONTERA = 0.1` (10% alrededor del umbral)

**Resultados de clasificación:**
- `descartada`: Área fuera del rango analizable (demasiado pequeña o grande)
- `normal`: Área < umbral_sospechoso (y no en zona de frontera)
- `sospechosa`: Área >= umbral_sospechoso

**Zona de frontera (opcional):**
- Si el área cae dentro de ±10% alrededor del umbral_sospechoso, se marca como `es_frontera: True`
- Esto indica que la decisión está en el límite y requiere revisión

### 5. Separación de Núcleos Superpuestos

**Ubicación:** `src/analysis.py`, función `analizar_nucleos()`

**Métodos disponibles:**

| Método | Descripción | Complejidad | Recomendación |
|--------|-------------|-------------|---------------|
| `None` | Sin separación, contornos detectados directamente | Baja | Para imágenes sin núcleos superpuestos |
| `'watershed'` | Transformada de distancia + watershed | Media-Alta | Para núcleos en contacto o superposición |
| `'maximos_locales'` | Detección de máximos locales en la transformada de distancia | Media | Alternativa al watershed |

**Parámetros por método:**

**Watershed:**
- `metodo='watershed'`: Activa la separación watershed
- No requiere parámetros adicionales além del método

**Máximos locales:**
- `metodo='maximos_locales'`: Activa la detección de máximos locales
- No requiere parámetros adicionales além del método

### 6. Métricas de Evaluación

**Archivo:** `validar_metricas_cito23.py`, `test_cito23_metrics.py`

** métricas calculadas:**

| Métrica | Fórmula | Interpretación |
|---------|---------|----------------|
| **Verdaderos Positivos (TP)** | Núcleos detectados que coinciden con ground truth | Detecciones correctas |
| **Falsos Positivos (FP)** | Núcleos detectados que no coinciden con ground truth | Falsas alarmas |
| **Falsos Negativos (FN)** | Núcleos en ground truth que no fueron detectados | Faltas de detección |
| **Precisión** | TP / (TP + FP) | Fracción de detecciones que son correctas |
| **Sensibilidad/Recall** | TP / (TP + FN) | Fracción de núcleos reales que fueron detectados |
| **F1-Score** | 2 · (Precisión · Recall) / (Precisión + Recall) | Media armónica de precisión y recall |
| **IoU (Intersection over Union)** | Área de intersección / Área de unión entre detección y ground truth | Superposición espacial |
| **Jaccard Index** | Igual a IoU para detección-binaria | Medida de similitud |

**Umbrales de aceptación (CITO-31):**
- F1-Score >= 90% con dataset de prueba congelado
- Este es el criterio principal para considerar el sistema validado

### 7. Generación de Ground Truth Sintético

**Archivo:** `generar_groundtruth_sintetico.py`

**Descripción:**
Genera ground truth sintético para validación cuando no hay anotaciones humanas disponibles.

**Parámetros:**
- `diagnostico_bethesda`: Distribución de diagnósticos (BENIGNO, LSIL, HSIL, CSC)
- `num_nucleos`: Número de núcleos por imagen
- `semilla`: Semilla aleatoria para reproducibilidad

**Formato de salida:**
- Máscara binarial por imagen
- Etiquetas YOLO normalizadas (clase, x_centro, y_centro, ancho, alto)
- Datos clínicos sintéticos en CSV

## Parámetros Configurables a Nivel de CLI

### main.py

| Opción | Parámetro | Descripción | Valor por defecto |
|--------|-----------|-------------|-------------------|
| `ruta` | Posicional | Ruta a imagen o carpeta | Requerido |
| `--sigma1` | sigma1 | Sigma primera Gaussian DoG | 7.0 |
| `--sigma2` | sigma2 | Sigma segunda Gaussian DoG | 8.0 |
| `--ruido` | - | Activar reducción de ruido bilateral | False |
| `--no-contraste` | - | Desactivar mejora de contraste CLAHE | False |
| `--polaridad` | polaridad | 'nucleos-claros' o 'nucleos-oscuros' | 'nucleos-claros' |
| `--no-gui` | - | Evitar ventanas gráficas | False |
| `--bitacora` | ID | Identificador de bitácora personalizado | Auto-generado |
| `--lote` | - | Procesar carpeta completa en lugar de imagen individual | False |

### api_v1.py

| Campo JSON | Tipo | Descripción |
|------------|------|-------------|
| `ruta_imagen` | string | Ruta de la imagen a analizar |
| `mejorar_contraste` | boolean | Si aplicar CLAHE |
| `metodo_contraste` | string | 'clahe', 'histogram', 'normalize', 'auto' |
| `reduzir_ruido` | boolean | Si aplicar filtro bilateral |
| `nivel_ruido` | string | 'bajo', 'medio', 'alto' |
| `polaridad` | string | 'nucleos-claros' o 'nucleos-oscuros' |
| `metodo_separacion` | string | None, 'watershed', 'maximos_locales' |

## Guía de Calibración de Parámetros

### Paso 1: Establecer sigmas iniciales
- Comenzar con sigma1=7.0, sigma2=8.0
- La relación sigma2/sigma1 debe estar entre 1.6 y 2.0
- Ajustar según el tamaño esperado de los núcleos en el dataset

### Paso 2: Configurar polaridad
- Usar 'nucleos-claros' para imágenes de fluorescencia
- Usar 'nucleos-oscuros' para imágenes de campo claro (Papanicolaou/EDF)
- El sistema invertirá automáticamente la polaridad si es necesario

### Paso 3: Activar/desactivar preprocesamiento
- `--ruido`: Activar para imágenes con mucho ruido de fondo
- `--no-contraste`: Desactivar si la iluminación ya es uniforme
- El CLAHE es recomendado para iluminación irregular

### Paso 4: Evaluar métricas
- Ejecutar con `--bitacora ID` para registrar resultados
- Revisar el resumen generado en `bitacora_experimentos.csv`
- Verificar que F1-Score >= 90% con el dataset de prueba
- Ajustar un parámetro a la vez

### Paso 5: Validar con ground truth
- Comparar resultados con anotaciones manuales
- Calcular IoU y precisión/recall
- Ajustar umbrales de filtrado si es necesario

## Limitaciones y Consideraciones

### Limitaciones del Algoritmo
1. **Núcleos muy superpuestos**: El watershed y máximos locales pueden fallar núcleos en contacto extremo
2. **Variaciones de iluminación intensas**: CLAHE ayuda pero puede no ser suficiente para iluminación muy desigual
3. **Núcleos de formas irregulares**: La circularidad < 0.3 filtra muchos, pero también puede eliminar núcleos genuinos con forma alterada
4. **Núcleos muy pequeños/grandes**: Los filtros de área tienen límites fijos que pueden no aplicarse a todos los tipos de muestra

### Consideraciones de Seguridad
- **No es software de diagnóstico**: Los resultados deben ser validados por personal calificado
- **No presentar conteos aproximados** como validación clínica sin ground truth espacial
- **Registrar cada experimento**: versión, dataset, parámetros, fecha, evidencia y decisión

### Reproducibilidad
- Cada experimento debe registrar: versión, dataset, parámetros, fecha, evidencia y decisión
- Usar `--bitacora ID` para identificar experimentos en la bitácora
- Los cambios múltiples de parámetros simultáneamente deben evitarse durante la calibración

## Próximas Actividades

- **CITO-35 (ACT-14)**: Documentar algoritmos, parámetros y métricas de evaluación (documento actual)
- **CITO-36 (ACT-15)**: Crear guía de usuario y manual de instalación
- **CITO-37 (ACT-16)**: Ejecutar pruebas de usabilidad con citotecnólogos
- **CITO-38 (ACT-17)**: Recopilar feedback de personal clínico y resolver cambios

## Referencias

- Documentación de OpenCV: funciones cv2.distanceTransform, cv2.watershed, cv2.findContours
- Método Otsu: thresholding automático basado en la histograma
- CLAHE: Contrast Limited Adaptive Histogram Equalization (OpenCV)
- Métricas: Precisión, Recall, F1-Score, IoU (estándar en visión por computadora)

