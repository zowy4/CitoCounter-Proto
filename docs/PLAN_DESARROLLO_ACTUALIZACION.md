# Plan de Desarrollo - Actualización CitoCounter-Proto

## Estado Actual del Proyecto

### Resumen Ejecutivo
- **Arquitectura**: CLI (`main.py`) + Streamlit UI (`app.py`) + Pipeline modular en `src/`
- **Enfoque actual**: DoG (Difference of Gaussians) con regla de área
- **Dataset**: Herlev 223 imágenes con ground truth, splits 156/33/34
- **CITO-22**: Baseline DoG validado localmente - En revisión en Jira
- **Problema identificado**: F1 = 0.92% (muy por debajo del objetivo del 90%)

### Métricas CITO-22 Baseline (Test Set - 34 imágenes)

**Resultados por imagen:**
- TP total: ~300 (muy bajo)
- FP total: ~15,000+ (extremadamente alto)
- FN total: ~10-20 (bajo)
- Precisión: ~0.5%
- Recall: ~50-75%
- **F1-Score promedio: 0.009 (0.9%)**

**Diagnóstico:** El filtro DoG genera demasiados falsos positivos, lo que invalida la detección para uso clínico real.

---

### Fase 5: Entrenamiento y Evaluación (Actualizado)

### Fase 6: Muestras y Pruebas (Activa)

#### Actividad 6.1: Protocolo de validación en microscopio real

**Estado:** En curso

**Descripción:** Diseñar protocolo de prueba con laminillas físicas en microscopio óptico con cámara acoplada.

**Implementación:**
- Creado `src/protocolo_microscopio_real.py` con clase `ProtocoloMicroscopioReal`
- Registro de pruebas con metadatos: laminilla_id, aumento, exposición, ganancia
- Cálculo automático de error absoluto y relativo (%)
- Bitácora JSON persistente en `data/results/bitacora_microscopio.json`
- Método `obtener_resumen()` para estadísticas de pruebas

**Pruebas unitarias:** `tests/test_protocolo_microscopio_real.py` - ✅ Pasan correctamente

### Fase 5: Entrenamiento y Evaluación

#### Actividad 5.2: Protocolo de métricas clínicas

**Estado:** Completo

**Descripción:** Evaluar precisión, recall, mAP@0.5, error relativo de conteo y FPS sostenido.

**Implementación:**
- Creado `src/protocolo_metricas_clinicas.py` con clase `EvaluadorMetricasClinicas`
- Cálculo de IoU entre cajas delimitadoras (ymin, xmin, ymax, xmax)
- Métricas: precisión, recall, F1, mAP@0.5 (basado en IoU)
- Error relativo de conteo porcentual
- FPS sostenido para benchmark de rendimiento
- Control de tamaño de datos de entrada (OWASP/STRIDE)

**Pruebas unitarias:** `tests/test_protocolo_metricas_clinicas.py` - ✅ Pasan correctamente

---

## Problemas Identificados

1. **Alta tasa de falsos positivos** (>99% de detecciones son incorrectas)
2. **No cumple requisito clínico** (F1 ≥ 90% en datos reales)
3. **Necesidad de migración a Deep Learning** para validación clínica real

---

## Plan de Desarrollo para Actualización

### Fase 1: Preparación y Análisis (1-2 días)

#### Actividad 1.1: Analizar cambios en rama MIGRACION
**Objetivo:** Integrar mejoras existentes de la rama MIGRACION
**Tarea:**
- Verificar archivos agregados en `src/segmentador_dl.py`
- Revisar integración de Cellpose/StarDist
- Validar estructura de datos preparada
**Tiempo estimado:** 4 horas

#### Actividad 1.2: Revizar dataset disponible
**Objetivo:** Validar el dataset Herlev con ground truth
**Tarea:**
- Verificar 223 imágenes en `data/raw/im_Dyskeratotic/`
- Revisar ground truth en `data/ground_truth/herlev/`
- Validar splits train/val/test (156/33/34)
**Tiempo estimado:** 3 horas

---

### Fase 2: Migración a Deep Learning (3-5 días)

#### Actividad 2.1: Instalar dependencias Deep Learning
**Objetivo:** Preparar entorno para modelos DL
**Tarea:**
- Instalar PyTorch (CPU/GPU según disponibilidad)
- Instalar Cellpose
- Instalar StarDist (para apoptosis)
- Verificar compatibilidad con OpenCV
**Tiempo estimado:** 4 horas

#### Actividad 2.2: Implementar adaptador segmentador DL
**Objetivo:** Crear interfaz para modelos Deep Learning
**Tarea:**
- Implementar clase `SegmentadorDL` en `src/`
- Soporte para Cellpose, StarDist, U-Net
- Manejo de entrada/salida estandarizada
**Tiempo estimado:** 8 horas

#### Actividad 2.3: Evaluar modelos con dataset congelado
**Objetivo:** Validar F1 ≥ 90% en datos reales
**Tarea:**
- Ejecutar Cellpose zero-shot en test set (34 imágenes)
- Ejecutar StarDist en test set
- Comparar métricas con ground truth
- Documentar resultados en CSV
**Tiempo estimado:** 6 horas

---

### Fase 3: UI de Escritorio con Qt Designer + PySide6 (4-6 días)

#### Actividad 3.1: Crear esqueleto Qt Designer
**Objetivo:** Estructura base de la aplicación de escritorio
**Tarea:**
- Crear archivo .ui con Qt Designer
- Definir paneles: carga, procesamiento, visualización, exportación
- Diseñar barra de herramientas y estado
**Tiempo estimado:** 6 horas

#### Actividad 3.2: Implementar lógica PySide6
**Objetivo:** Conectar UI con pipeline
**Tarea:**
- Convertir .ui a Python con pyu6
- Implementar eventos de botones
- Integrar con `main.py` y `src/`
- Manejo de threads para procesamiento
**Tiempo estimado:** 10 horas

#### Actividad 3.3: Integrar detección DoG y DL
**Objetivo:** Interfaz unificada para ambos métodos
**Tarea:**
- Toggle entre DoG y Deep Learning
- Parámetros ajustables por usuario
- Visualización de resultados superpuestos
- Exportación de resultados
**Tiempo estimado:** 8 horas

---

### Fase 4: Pruebas y Validación (2-3 días)

#### Actividad 4.1: Pruebas unitarias
**Objetivo:** Garantizar calidad del código
**Tarea:**
- Cobertura de funciones nuevas en `tests/`
- Tests para segmentador_dl
- Tests para UI
**Tiempo estimado:** 6 horas

#### Actividad 4.2: Pruebas con usuarios potenciales
**Objetivo:** Validar usabilidad y funcionalidad
**Tarea:**
- Revisar cuestionario en `data/questionarios/cuestionario_usuarios_potenciales.json`
- Reunión con citotecnólogos
- Recopilar feedback
- Documentar mejoras necesarias
**Tiempo estimado:** 8 horas

---

### Fase 5: Documentación y Entrega (1-2 días)

#### Actividad 5.1: Actualizar documentación
**Objetivo:** Documentar cambios y uso
**Tarea:**
- Actualizar README.md
- Documentar nuevas funciones
- Guía de instalación de dependencias
**Tiempo estimado:** 4 horas

#### Actividad 5.2: Generar evidencia para Jira
**Objetivo:** Completar CITO-22 y preparar siguiente actividad
**Tarea:**
- Generar reporte final de validación DL
- Subir evidencias en `docs/`
- Actualizar estado en Jira
**Tiempo estimado:** 4 horas

---

## Actividades de Usuario - Pruebas con Citotecnólogos

Preguntas clave para validación:

### 1. Experiencia de Usuario
1. ¿La interfaz es intuitiva para cargar imágenes y configurar parámetros?
2. ¿Los tiempos de procesamiento son aceptables (menos de 10 segundos por imagen)?
3. ¿La visualización de resultados (superposición de detecciones) es clara?

### 2. Flujo de Trabajo
4. ¿El flujo de trabajo sigue el proceso clínico real (cargar → procesar → revisar → exportar)?
5. ¿Los colores y estilos visuales son apropiados para uso clínico?
6. ¿Hay suficiente espacio para anotaciones o observaciones?

### 3. Parámetros Técnicos
7. ¿Los parámetros de detección (sigma, umbrales) son ajustables y comprensibles?
8. ¿Ofrecen opciones para filtrar detecciones sospechosas?
9. ¿Permite comparar DoG vs Deep Learning en tiempo real?

### 4. Validación Clínica
10. ¿Los resultados visualizados coinciden con su percepción humana?
11. ¿Qué casos falteran en la detección/segmentación?
12. ¿Ofrecen sugerencias de mejora o ajustes?

### 5. Recomendaciones Generales
13. ¿Qué características faltan para uso en su clínica/práctica?
14. ¿Preferirían una versión web o aplicación de escritorio?
15. ¿Qué documentación o tutoriales necesitarían?

---

## Próximos Pasos

1. **Inmediatamente:** Jalar cambios de rama MIGRACION y analizar estructura existente
2. **Semana 1:** Preparar entorno DL e instalar dependencias
3. **Semana 2:** Implementar evaluación de modelos Cellpose/StarDist
4. **Semana 3-4:** Desarrollar UI Qt Designer + PySide6
5. **Semana 5:** Pruebas con usuarios y ajustes finales

---

## Consideraciones Técnicas

### Seguridad
- No almacenar imágenes sensibles en el repositorio (seguro en `.gitignore`)
- Validación de tamaño de imágenes (límite 64 KiB para DoS)
- Logs estructurados para auditoría (CITO-93)

### Arquitectura
- Mantener modularidad en `src/`
- Contratos explícitos con dataclasses (`pipeline_contract.py`)
- Tipado estático con typing
- Tests unitarios para cada nueva función

### Compatibilidad
- Python ≥ 3.8 (mínimo requerido)
- OpenCV ≥ 4.5
- PyTorch ≥ 1.9 (opcional, según disponibilidad GPU)
- PySide6 para UI de escritorio

---

## Decisión Técnica: Qt Designer + PySide6

**Ventajas para uso clínico:**
- Aplicación nativa (mejor rendimiento)
- Offline posible (sin conexión a internet)
- Control total de UI y experiencia
- Distribución como ejecutable

**Consideraciones:**
- Mayor complejidad que Streamlit
- Necesidad de instalar dependencias de Qt
- Soporte multiplataforma requerido

---

**Fecha de creación:** 2026-09-16  
**Autor:** Zoé Andrés Chacón Zavala  
**Versión:** 1.0  
**Estado:** Planificación - Esperando validación