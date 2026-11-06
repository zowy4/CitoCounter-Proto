# Bitácora de Regresión y Validación - CITO-95 / CitoCounter-Proto

- **Fecha:** 2026-11-05
- **Rama:** `MIGRACION`
- **Responsable:** Asistente Copilot / Zoé Andrés Chacón Zavala

## Resumen de Ejecución
1. **Suite de Pruebas Unitarias y de Integración:**
   - Se ejecutaron con éxito las suites principales: `test_segmentador_dl.py`, `test_cito77_reglas.py`, `test_api_v1.py`, `test_dataset_validator.py`, `test_herlev_evaluation.py`, `test_dog_filter.py`, `test_analysis_rules.py`, `test_cito23_metrics.py`, `test_cito75_metrics.py` y `test_segmentador_dl_correcto.py`.
   - **Total de pruebas verificadas:** 79+ pruebas pasando en verde (`OK`).

2. **Validación de Consistencia de Dataset:**
   - Ejecutado: `python validar_consistencia_dataset.py`.
   - **Estructura:** Verificada correctamente (`CitoDataset_v1`, `train`, `val`, `test`).
   - **Matching imagen-etiqueta:** 1400 train, 400 val, 200 test (100% emparejadas).
   - **Distribución:** 70% train, 20% val, 10% test.

3. **Conclusión:**
   - El sistema se encuentra estable, con todas las características de Deep Learning, API REST y reglas explicables integradas y validadas.
