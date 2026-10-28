# CITO-30: Almacenamiento para resultados de experimentación

## Estado: **Finalizado** ✅

## Resumen
Se implementó un sistema de almacenamiento basado en CSV (`bitacora_experimentos.csv`) para registrar y consultar el historial de experimentaciones, con funciones de agregación y preparación de datos para dashboards.

## Componentes implementados

### 1. Modelo de datos (`CAMPOS_BITACORA`)
Esquema de 19 campos para cada experimento:
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_prueba` | string | Identificador único (prefijo `T-`) |
| `fecha` | string | YYYY-MM-DD |
| `hora` | string | HH:MM |
| `imagen` | string | Nombre del archivo analizado |
| `sigma1` | float | Parámetro DoG (desenfoque fino) |
| `sigma2` | float | Parámetro DoG (desenfoque grueso) |
| `area_promedio_normal` | int | Área promedio de referencia (px²) |
| `factor_riesgo` | float | Factor de clasificación (default 3.0) |
| `area_minima` | int | Umbral mínimo de área (px²) |
| `total_celulas` | int | Total núcleos detectados |
| `normales` | int | Células normales (área < 3x) |
| `sospechosas` | int | Células sospechosas (área ≥ 3x) |
| `porcentaje_riesgo` | float | % células sospechosas |
| `falsos_positivos` | int | FP (para validación con ground truth) |
| `falsos_negativos` | int | FN (para validación con ground truth) |
| `precision_estimada` | float | Precision calculada |
| `observaciones` | string | Notas libres |
| `calidad_dog` | string | Calidad de imagen DoG |
| `ajuste_siguiente` | string | Parámetros sugeridos para siguiente prueba |
| `responsable` | string | Operador que ejecutó la prueba |

### 2. Lectura robusta (`cargar_historial`)
- Lee CSV con o sin encabezado
- Filtra filas válidas (prefijo `T-`)
- Convierte campos numéricos automáticamente
- Maneja archivos vacíos o inexistentes

### 3. Agregación (`agregar_historial`)
Calcula indicadores consolidados:
```python
{
    "total_ejecuciones": 15,
    "imagenes_unicas": 8,
    "total_celulas": 187,
    "normales": 138,
    "sospechosas": 49,
    "promedio_riesgo": 26.2
}
```

### 4. Preparación para Dashboard (`filas_para_tabla`)
Reduce a 10 columnas esenciales para `st.dataframe()`:
`id_prueba`, `fecha`, `hora`, `imagen`, `sigma1`, `sigma2`, `total_celulas`, `normales`, `sospechosas`, `porcentaje_riesgo`

## Evidencia de funcionamiento

### Tests automatizados (2 tests pasan)
```bash
python -m pytest tests/test_historial_resultados.py -v
```
- `test_carga_bitacora_sin_encabezado_y_agrega_metricas` ✅
- `test_ignora_filas_invalidas_y_prepara_tabla` ✅

### Ejemplo de uso
```python
from src.historial_resultados import cargar_historial, agregar_historial, filas_para_tabla

# Cargar historial
historial = cargar_historial()

# Calcular métricas consolidadas
resumen = agregar_historial(historial)
print(f"Total ejecuciones: {resumen['total_ejecuciones']}")
print(f"Imágenes únicas: {resumen['imagenes_unicas']}")
print(f"Riesgo promedio: {resumen['promedio_riesgo']:.1f}%")

# Preparar tabla para dashboard
tabla = filas_para_tabla(historial)
# tabla → lista de dicts lista para st.dataframe()
```

### Integración con Dashboard (CITO-27)
El almacenamiento se integra directamente con `app.py`:
```python
# En app.py - sección historial
from src.historial_resultados import cargar_historial, agregar_historial, filas_para_tabla

historial = cargar_historial()
resumen = agregar_historial(historial)
tabla = filas_para_tabla(historial)
st.dataframe(tabla, use_container_width=True)
```

### Integración con ETL (CITO-29)
El almacenamiento es la fuente de datos para el ETL:
```python
# En etl_resultados.py
from .historial_resultados import cargar_historial, CAMPOS_BITACORA, CAMPOS_NUMERICOS

def extraer_bitacora(ruta=DEFAULT_BITACORA):
    # Usa la misma lógica de lectura que historial_resultados
    ...
```

## Archivo de datos
- **Ubicación**: `bitacora_experimentos.csv` (raíz del proyecto)
- **Formato**: CSV sin encabezado, campos separados por comas
- **Ejemplo de fila**:
```
T-001,2026-10-15,14:30,MUESTRA_014.jpg,5.0,10.0,300,3.0,10,6,4,2,66.67,,,,,,,
```

## Referencias
- Código: `src/historial_resultados.py`
- Tests: `tests/test_historial_resultados.py`
- Integración: `src/etl_resultados.py`, `src/metricas_sistema.py`, `app.py`
- Tarea padre: J-14 (Almacenamiento analítico y modelo de datos)