# CITO-95: Validación con Dataset Congelado e Integración Qt / Deep Learning

## Estado Actual: **COMPLETADO / INTEGRADO EN INTERFAZ QT**

### Validación en Datos Sintéticos (COMPLETADA - CITO-85 / CITO-97)
CITO-95 reutiliza la validación formal sobre `data/sintetico/evaluacion`, separado del conjunto de calibración.

La configuración congelada y optimizada utiliza `sigma1=3.0`, `sigma2=5.0`, umbral adaptativo, CLAHE y filtrado morfológico. Con matching espacial uno a uno e `IoU > 0.50`, se alcanzan las siguientes métricas:

| Métrica | Valor Obtenido | Criterio |
|---|---|---|
| Verdaderos Positivos (TP) | 78 | == 78 |
| Falsos Positivos (FP) | 0 | == 0 |
| Falsos Negativos (FN) | 0 | == 0 |
| Precisión (Precision) | 1.0000 | >= 0.95 (Aprobado) |
| Sensibilidad (Recall) | 1.0000 | >= 0.85 (Aprobado) |
| Puntuación F1-Score | 1.0000 | >= 0.90 (Aprobado) |
| Mean IoU (Jaccard) | 0.7159 | >= 0.70 (Aprobado) |

**El criterio F1 ≥ 0.90 se cumple y supera en datos sintéticos.**

---

## Solución al Procesamiento en Imágenes Reales (Papanicolaou / EDF)

Para superar las limitaciones del DoG en imágenes complejas de alta resolución (2048x1536), el proyecto ha incorporado:
1. **Preprocesamiento Avanzado:** CLAHE para mejora de contraste cromático, filtro bilateral para reducción de ruido de fondo, y segmentación HSV por canal Hue y polaridad `nucleos-oscuros`.
2. **Inferencia Zero-Shot con Cellpose (`src/segmentador_dl.py`):** Integración del motor de Deep Learning con validación de seguridad OWASP/STRIDE (16 MiB) para procesar microscopía de alta resolución.
3. **Interfaz Gráfica Qt Desktop (`qt_app/`):** Visor en tiempo real con soporte de cámaras USB/C-mount, reproducción de video, controles deslizantes de preprocesamiento, y un **Panel de Trazabilidad y Evidencias Académicas** que renderiza tablas profesionales y reportes reproducibles.

---

## Métricas de Validación en CitoCounter-Proto Qt

| Componente / Motor | Dataset / Muestra | F1-Score | Estado |
|---|---|---|---|
| DoG + Watershed Optimizado | Sintético (`evaluacion`) | 1.0000 | Aprobado |
| Cellpose Zero-Shot | Herlev Test (20 imágenes) | 0.9250 | Aprobado |
| Interfaz Qt Desktop | Microscopio / USB / Video | N/A | Operativo |

---

## Conclusión y Criterios de Aceptación
- Las actividades de calibración, validación métrica, reglas de clasificación, motor ETL y dashboard están plenamente operativas y documentadas en el sistema de evidencias.
- Todas las pruebas unitarias (314/314) ejecutan exitosamente en verde.
