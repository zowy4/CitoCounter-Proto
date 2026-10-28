# CITO-29: Flujo ETL para resultados y reportes históricos

## Estado: **Finalizado** ✅

## Resumen
Se implementó un flujo ETL (Extract, Transform, Load) completo para procesar la bitácora de experimentación (`bitacora_experimentos.csv`) y generar reportes consolidados, exportaciones CSV/JSON y agregaciones para dashboards.

## Componentes implementados

### 1. Extracción (`extraer_bitacora`)
- Lee `bitacora_experimentos.csv` con o sin encabezado
- Filtra filas válidas (prefijo `T-`)
- Convierte campos a tipos apropiados (int, float, string)
- Ignora filas inválidas o incompletas

### 2. Transformación
- **`normalizar_registro`**: Estandariza fechas, asegura tipos numéricos
- **`transformar_a_esquema_unificado`**: Reduce a campos esenciales para métricas
  - Campos: `id_prueba`, `fecha`, `hora`, `imagen`, `sigma1`, `sigma2`, `total_celulas`, `normales`, `sospechosas`, `porcentaje_riesgo`
  - Calcula campos derivados (sospechosas = total - normales)

### 3. Carga y Agregación
- **`cargar_a_dataframe`**: Genera CSV listo para análisis
- **`agregado_por_imagen`**: Métricas consolidadas por imagen
  - Total ejecuciones, imágenes únicas, promedios de células/normales/sospechosas/riesgo
- **`agregado_por_sigma`**: Métricas agrupadas por configuración (sigma1, sigma2)
  - Permite comparar rendimiento por parámetros DoG

### 4. Exportación
- **`exportar_csv`**: Exporta a CSV con esquema unificado
- **`exportar_json`**: Exporta a JSON con campos normalizados

## Evidencia de funcionamiento

### Tests automatizados (10 tests pasan)
```bash
python -m pytest tests/test_etl_resultados.py -v
```
- `test_extraer_bitacora_con_datos` ✅
- `test_extraer_bitacora_vacia` ✅
- `test_ignora_filas_invalidas` ✅
- `test_normalizar_registro` ✅
- `test_transformar_a_esquema_unificado` ✅
- `test_cargar_a_dataframe` ✅
- `test_agregado_por_imagen` ✅
- `test_agregado_por_sigma` ✅
- `test_exportar_csv` ✅
- `test_exportar_json` ✅

### Ejemplo de uso
```python
from src.etl_resultados import extraer_bitacora, transformar_a_esquema_unificado, exportar_csv, exportar_json

# Extraer y transformar
registros = extraer_bitacora()
unificados = transformar_a_esquema_unificado(registros)

# Agregar métricas
from src.etl_resultados import agregado_por_imagen, agregado_por_sigma
metricas_imagen = agregado_por_imagen(unificados)
metricas_sigma = agregado_por_sigma(unificados)

# Exportar
exportar_csv(Path("data/results/etl_export.csv"), unificados)
exportar_json(Path("data/results/etl_export.json"), unificados)
```

### Salida de ejemplo (agregado_por_imagen)
```json
{
  "total_ejecuciones": 15,
  "imagenes_unicas": 8,
  "total_celulas_promedio": 12.5,
  "normales_promedio": 9.2,
  "sospechosas_promedio": 3.3,
  "riesgo_promedio": 26.4
}
```

## Integración con Dashboard (CITO-27)
El ETL se integra con `src/historial_resultados.py` y `src/metricas_sistema.py` para alimentar el dashboard Streamlit (`app.py`):
- `cargar_historial()` → `extraer_bitacora()`
- `agregar_historial()` → usa agregaciones del ETL
- `filas_para_tabla()` → prepara datos para `st.dataframe()`

## Archivos generados
- `data/results/etl_export.csv` - CSV consolidado
- `data/results/etl_export.json` - JSON consolidado

## Referencias
- Código: `src/etl_resultados.py`
- Tests: `tests/test_etl_resultados.py`
- Integración: `src/historial_resultados.py`, `src/metricas_sistema.py`, `app.py`
- Tarea padre: J-15 (Dashboard, ETL y almacenamiento analítico)