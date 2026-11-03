# CITO-22: Validación del Algoritmo DoG para Detección de Núcleos Celulares

## Resumen Ejecutivo

**Actividad:** CITO-22 - Calibrar el algoritmo DoG para detectar núcleos celulares  
**Estado:** En revisión  
**Fecha:** 11/09/2026  
**Responsable:** Zoé Andrés Chacón Zavala  

---

## Resultados de Validación

### Métricas en Test Set Herlev (34 imágenes)

| Métrica | Valor |
|---------|-------|
| **TP (Verdaderos Positivos)** | 301 |
| **FP (Falsos Positivos)** | 14,341 |
| **FN (Falsos Negativos)** | 36 |
| **Precisión** | 0.0203 (2.03%) |
| **Recall** | 0.8947 (89.47%) |
| **F1-Score** | 0.0398 (3.98%) |
| **Imágenes procesadas** | 34 |

### Métricas Promedio por Imagen

| Métrica | Valor |
|---------|-------|
| Precisión promedio | 0.008-0.020 |
| Recall promedio | 0.50-1.00 |
| F1 promedio | 0.009-0.030 |

---

## Análisis de Resultados

### Hallazgos Principales

1. **Alta tasa de falsos positivos (>99%)**: El algoritmo detecta 14,341 células falsas por cada 301 verdaderas.
2. **Baja precisión (2.03%)**: Solo el 2% de las detecciones son correctas.
3. **Readequo aceptable (89.47%)**: Logra detectar la mayoría de las células reales.
4. **F1 muy por debajo del objetivo**: El F1 de 3.98% está muy lejos del objetivo del 90%.

### Problemas Identificados

**Causa principal de altos FP:**
- El filtro Difference of Gaussians (DoG) es muy sensible a artefactos
- No distingue correctamente células reales de ruido y estructuras no celulares
- Umbrales actuales no ajustados al ancho de banda típico de núcleos

**Imágenes con peor rendimiento:**
- `144.bmp`: 0 TP, 1325 FP (detección completa fallida)
- `151.bmp`: 1 TP, 1082 FP (muy baja precisión)
- `152.bmp`: 0 TP, 972 FP (detección sin células reales)
- `164.bmp`: 17 TP, 263 FP (alguna capacidad, pero con FP altos)

---

## Comparación con Objetivos

### Objetivo Técnico (CITO-95)
- **F1-Score ≥ 90%** en dataset congelado
- **Estado:** ❌ NO CUMPLE - F1 = 3.98%

### Recomendación (CITO-95)
El bajo F1 invalida el enfoque DoG para uso clínico real. Se requiere migración a modelos de Deep Learning.

---

## Próximos Pasos

### Inmediatamente
1. ✓ Registrar resultados en CVS y documentar
2. ✓ Analizar causas de altos falsos positivos
3. ⏳ Actualizar estado en Jira a "Bloqueado"

### Para la Siguiente Actividad (CITO-95)
1. Investigar instalación de Cellpose/StarDist/U-Net
2. Evaluar modelos zero-shot en test set
3. Comparar métricas con DoG
4. Documentar resultados y decisión de migración

---

## Archivos Generados

1. `data/results/CITO-22-baseline-dog-test.csv` - Resultados por imagen
2. `data/results/CITO-22-validacion-DOG-2026-09-11.txt` - Detalle completo
3. `calibration/cito22_barrido_dog.csv` - Análisis de parámetros
4. `docs/evidencia-cito22-barrido-calibracion.md` - Documentación de calibración

---

## Conclusión

**El algoritmo DoG implementado NO es viable para uso clínico real.**

La validación con imágenes reales del dataset Herlev muestra:
- Fuerza de detección aceptable (90% recall)
- Pero calidad extremadamente baja (2% precisión)
- Necesidad clara de migrar a Deep Learning

**Decisión:** Recomendado pasar a CITO-95 (validación F1 ≥ 90% con DL)

---

## Evidencia Adjunta

- CSV de resultados: Adjunto
- Logs de procesamiento: Adjunto  
- Comparación parámetros: Adjunto
- Imágenes ejemplares: Adjunto

---

**Fecha de generación:** 11/09/2026  
**Generado por:** CITO Counter Auto-evaluation  
**Próxima revisión:** Jira CITO-22