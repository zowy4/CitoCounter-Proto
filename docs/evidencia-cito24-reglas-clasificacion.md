# Evidencia CITO-24 - Reglas explicables de clasificación

## Alcance

Se formalizaron reglas explícitas para clasificar núcleos en `normal` o `sospechosa` con límites trazables por área.

## Reglas implementadas

Fuente: `src/analysis.py`

1. **Filtro de validez**
   - Área `< AREA_MINIMA_NUCLEO` → `descartada` (ruido).
   - Área `> AREA_MAXIMA_NUCLEO` → `descartada` (artefacto).

2. **Umbral de riesgo**
   - `umbral_sospechoso = AREA_PROMEDIO_NUCLEO_NORMAL * FACTOR_RIESGO`
   - Área `>= umbral_sospechoso` → `sospechosa`
   - Área `< umbral_sospechoso` → `normal`

3. **Casos frontera**
   - Se marca `es_frontera=True` cuando el área cae en ±10% del umbral de riesgo.
   - Objetivo: facilitar revisión experta de casos limítrofes.

## Evidencia de pruebas

- `tests/test_analysis_rules.py`
  - Rechazo por área mínima
  - Rechazo por área máxima
  - Clasificación sospechosa en umbral
  - Marcado de frontera en rango limítrofe

## Resultado operativo

El pipeline conserva compatibilidad y ahora expone:

- `frontera` (conteo de casos limítrofes)
- `criterios_clasificacion` (motivo y umbral aplicado por núcleo válido)

Esto cubre la actividad CITO-24 para reglas explicables y límites en el prototipo.
