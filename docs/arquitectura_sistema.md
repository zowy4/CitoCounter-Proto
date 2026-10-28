# CitoCounter-Proto: Arquitectura del Sistema y Flujo de Datos

## Visión General

CitoCounter-Proto es un prototipo de investigación en Python para la detección y clasificación de núcleos en citología cervical. El sistema utiliza filtros DoG (Difference of Gaussians) y técnicas de watershed para separar núcleos superpuestos.

## Arquitectura del Sistema

El pipeline de procesamiento se compone de los siguientes módulos principales:

### 1. Punto de Entrada CLI (`main.py`)
- Interfaz de línea de comandos para procesamiento por lotes
- Parámetros configurables: sigmas DoG, reducción de ruido, contraste, polaridad
- Modos: imagen individual o lote completo
- Salida: resultados en `data/results/` y bitácora en `bitacora_experimentos.csv`

### 2. Preprocesamiento (`src/preprocessing.py`)
- Conversión a escala de grises
- Mejora de contraste (CLAHE, ecualización global, normalización)
- Reducción de ruido (filtro bilateral)
- Ajuste de polaridad ('nucleos-claros' / 'nucleos-oscuros')
- Función principal: `preprocesar_imagen()`

### 3. Filtro DoG (`src/dog_filter.py`)
- Aplicación del filtro Difference of Gaussians
- Parámetros: sigma1, sigma2
- Salida: imagen DoG en float32
- Función principal: `aplicar_filtro_dog()`
- Conserva la resta en `float32` antes de normalizar

### 4. Análisis de Núcleos (`src/analysis.py`)
- Binarización con umbral de Otsu
- Detección de contornos
- Filtrado de ruido (artefactos por tamaño, circularidad, aspecto)
- Clasificación por área (normales/sospechosas)
- Métodos de separación de núcleos superpuestos:
  - Ninguno (comportamiento original)
  - Watershed (transformada de distancia + watershed)
  - Máximos locales (detección de picos)
- Función principal: `analizar_nucleos()`

### 5. Visualización (`src/visualization.py`)
- Paneles de salida con anotaciones
- Colores: verde para normales, rojo para sospechosas
- Función principal: panel de resultados

### 6. API REST (`api_v1.py`)
- Endpoint `/analyze` para análisis programático
- Validación de entradas y salidas JSON
- Manejo de errores y códigos de estado
- Función principal: endpoint de análisis HTTP

## Flujo de Datos

```mermaid
graph TD
    A[Imagen de entrada] --> B[Preprocesamiento]
    B --> C[Filtro DoG]
    C --> D[Análisis de Núcleos]
    D --> E[Separación de Núcleos (opcional)]
    D --> F[Clasificación]
    E --> G[Resultados]
    F --> G
    G --> H[Visualización]
    G --> I[Guardar Bitácora]
    G --> J[Guardar Resultados]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px
```

### Paso a Paso

1. **Carga de Imagen**: `main.py` carga la imagen usando OpenCV (`cv2.imread`)
2. **Preprocesamiento**: `preprocesar_imagen()` convierte a gris, opcionalmente reduce ruido y mejora contraste
3. **Inversión de Polaridad** (si es 'nucleos-oscuros'): La imagen se invierte para que el DoG detecte núcleos como blobs claros
4. **Filtro DoG**: `aplicar_filtro_dog()` aplica el filtro Difference of Gaussians con sigmas configurables
5. **Análisis**: `analizar_nucleos()`:
   - Binarización con Otsu
   - Detección de contornos
   - Filtrado de ruido (artefactos pequeños/grandes, circularidad, aspecto)
   - Clasificación por área (umbral 3x del promedio)
   - Separación opcional de núcleos superpuestos
6. **Resultados**: Diccionario con total_celulas, normales, sospechosas, áreas, contornos
7. **Salida**: Resultados guardados en `data/results/` y bitácora en `bitacora_experimentos.csv`

## Polaridades Soportadas

- `'nucleos-claros'`: Núcleos claros sobre fondo oscuro (fluorescencia)
  - El pipeline Detecta blobs claros sin inversión
- `'nucleos-oscuros'`: Núcleos oscuros sobre fondo claro (Papanicolaou, EDF)
  - Requiere inversión de polaridad antes del DoG (ver `invertir_polaridad()`)
  - El DoG detecta blobs claros; la geometría se preserva

## Parámetros Clave

| Parámetro | Descripción | Valor por Defecto | Rango Recomendado |
|-----------|-------------|-------------------|-------------------|
| `--sigma1` | Sigma primera Gaussian | 7.0 | 5.0 - 10.0 |
| `--sigma2` | Sigma segunda Gaussian | 8.0 | 1.6-2.0 × sigma1 |
| `--ruido` | Reducción de ruido bilateral | False | Nivel 'medio' |
| `--no-contraste` | Desactivar CLAHE | False | Activar para iluminación irregular |
| `--polaridad` | Polaridad de núcleos | 'nucleos-claros' | 'nucleos-oscuros' para campo claro |

## Limitaciones y Consideraciones

- El sistema es un **prototipo de investigación**, no software de diagnóstico ni dispositivo médico
- Los valores de precisión, recall, F1 e IoU requieren ground truth espacial válido
- Los parámetros deben calibrarse con el dataset específico
- Un solo parámetro a la vez durante la calibración
- Los artefactos de tinción y variaciones de iluminación son manejados por CLAHE y filtrado de tamaño
- La separación de núcleos superpuestos mejora la precisión en imágenes de contacto celular

## Próximas Actividades

- **CITO-34**: Documentar arquitectura del sistema y flujo de datos (ACT-13)
- **CITO-35**: Documentar algoritmos, parámetros y métricas de evaluación (ACT-14)
- **CITO-36**: Crear guía de usuario y manual de instalación (ACT-15)
